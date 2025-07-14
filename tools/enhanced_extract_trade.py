"""
enhanced_extract_trade.py
AI-powered trade extractor with single-image and batch support,
OCR confidence metrics, DeepSeek integration, and multi-format logging.

Usage examples (CLI):
    python enhanced_extract_trade.py trade.png
    python enhanced_extract_trade.py screenshots/ --batch
    python enhanced_extract_trade.py trade.png --json-only
"""

# ---------- IMPORTS ----------
import os, sys, json, uuid, re
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from PIL import Image
import pytesseract
from openai import OpenAI

load_dotenv()

# === Path Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADE_LOG_PATH = os.path.join(BASE_DIR, "logs", "trade_log.jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")

# ---------- OPENAI / DEEPSEEK CLIENT ----------
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),                     # put in .env
    base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
)

# ---------- DATA SCHEMAS ----------
class TradeData(BaseModel):
    trade_id: str
    ticker: Optional[str] = None
    timeframe: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    direction: Optional[str] = None
    pnl: Optional[str] = None
    pnl_amount: Optional[float] = None
    date_time: Optional[str] = None
    reason_or_annotations: Optional[str] = None
    image_source: Optional[str] = None
    logged_at: str
    ocr_confidence: Optional[str] = None

    @field_validator('pnl_amount', mode='before')
    @classmethod
    def parse_pnl_amount(cls, v):
        """Parse PnL amount from various string formats"""
        if v is None or v == "":
            return None
        
        if isinstance(v, (int, float)):
            return float(v)
        
        if isinstance(v, str):
            # Remove common symbols and clean the string
            cleaned = re.sub(r'[^\d\.\-\+]', '', v.replace(',', ''))
            if cleaned:
                try:
                    return float(cleaned)
                except ValueError:
                    return None
        
        return None

# ---------- OCR ----------
def extract_text_from_image(image_path: str) -> Tuple[str, Dict]:
    """OCR text + confidence info"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    # raw text
    text = pytesseract.image_to_string(img)
    # word-level data for confidence
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    # Fixed confidence parsing
    confs = []
    for c in data["conf"]:
        try:
            conf_val = int(c)
            if conf_val > 0:
                confs.append(conf_val)
        except (ValueError, TypeError):
            continue
    
    avg_conf = sum(confs) / len(confs) if confs else 0.0

    return text, {
        "confidence": avg_conf,
        "total_words": len([w for w in data["text"] if w.strip()]),
        "image_size": img.size,
    }

# ---------- AI ANALYSIS ----------
def analyze_trade_with_ai(raw_text: str, image_path: str) -> str:
    """Call DeepSeek (OpenAI-compatible) to structure the trade"""
    prompt = f"""
You are an expert trading analyst. Given OCR text from a trading screenshot, output ONLY valid JSON with the following keys:

ticker, timeframe, entry_price, exit_price, direction, pnl, pnl_amount, date_time, reason_or_annotations

IMPORTANT: For pnl_amount, extract only the numeric value (e.g., if you see "+38.07 USD", output 38.07)

OCR text from {os.path.basename(image_path)}:
\"\"\"{raw_text}\"\"\"

Example output:
{{
  "ticker": "SOLUSD",
  "timeframe": "5m",
  "entry_price": 150.25,
  "exit_price": 151.50,
  "direction": "long",
  "pnl": "+38.07 USD",
  "pnl_amount": 38.07,
  "date_time": "2025-07-06 14:20:58",
  "reason_or_annotations": "Quick scalp trade"
}}
"""
    rsp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500,
    )
    return rsp.choices[0].message.content

# ---------- RECORD CREATION ----------
def create_trade_record(ai_json: str, image_path: str, ocr_info: Dict) -> TradeData:
    # strip optional back-ticks
    cleaned = ai_json.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:-3].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:-3].strip()

    try:
        data = json.loads(cleaned)
        print(f"🔍 Parsed AI data: {data}")  # Debug logging
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        data = {"error": f"JSON parse error: {e}"}

    return TradeData(
        trade_id=str(uuid.uuid4())[:8],
        ticker=data.get("ticker"),
        timeframe=data.get("timeframe"),
        entry_price=data.get("entry_price"),
        exit_price=data.get("exit_price"),
        direction=data.get("direction"),
        pnl=data.get("pnl"),
        pnl_amount=data.get("pnl_amount"),
        date_time=data.get("date_time"),
        reason_or_annotations=data.get("reason_or_annotations"),
        image_source=os.path.basename(image_path),
        logged_at=datetime.now().isoformat(),
        ocr_confidence=f"{ocr_info.get('confidence', 0):.1f}%",
    )

# ---------- SAVE LOGS ----------
def save_trade_data(trade: TradeData, mode: str = "both") -> List[str]:
    saved: List[str] = []

    # 1. append to JSONL database
    os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)
    with open(TRADE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(trade.model_dump_json() + "\n")
    saved.append(TRADE_LOG_PATH)

    # 2. individual JSON
    if mode in {"both", "json"}:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        fp = os.path.join(
            OUTPUT_DIR, f"trade_{trade.trade_id}_{datetime.now():%Y%m%d_%H%M%S}.json"
        )
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(trade.model_dump(), f, indent=2, default=str)
        saved.append(fp)

    # 3. daily summary
    if mode in {"both", "jsonl"}:
        day = datetime.now().strftime("%Y-%m-%d")
        summary_path = os.path.join(SUMMARIES_DIR, f"daily_summary_{day}.json")
        os.makedirs(SUMMARIES_DIR, exist_ok=True)
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
        else:
            summary = {
                "date": day,
                "trades": [],
                "total_trades": 0,
                "total_pnl": 0,
                "created_at": datetime.now().isoformat(),
            }
        summary["trades"].append(trade.model_dump())
        summary["total_trades"] = len(summary["trades"])
        summary["total_pnl"] = sum(t.get("pnl_amount") or 0 for t in summary["trades"])
        summary["updated_at"] = datetime.now().isoformat()
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        saved.append(summary_path)

    return saved

# ---------- SINGLE IMAGE ----------
def process_single_image(image_path: str, save_mode: str = "both") -> Dict:
    try:
        print(f"🔍 Starting OCR extraction for: {image_path}")
        raw_text, ocr_info = extract_text_from_image(image_path)
        print(f"📝 OCR completed, confidence: {ocr_info['confidence']:.1f}%")
        
        print(f"🤖 Calling AI analysis...")
        ai_json = analyze_trade_with_ai(raw_text, image_path)
        print(f"🤖 AI response received")
        
        print(f"📊 Creating trade record...")
        trade = create_trade_record(ai_json, image_path, ocr_info)
        print(f"💾 Saving trade data...")
        files = save_trade_data(trade, save_mode)
        print(f"✅ Processing complete")

        return {
            "trade_id": trade.trade_id,
            "image": os.path.basename(image_path),
            "ticker": trade.ticker,
            "direction": trade.direction,
            "pnl_amount": trade.pnl_amount,
            "confidence": ocr_info["confidence"],
            "saved_files": files,
        }
    except Exception as e:
        print(f"❌ Error in process_single_image: {str(e)}")
        raise

# ---------- BATCH ----------
def process_multiple_images(folder: str, save_mode: str = "both") -> Dict:
    if not os.path.isdir(folder):
        return {"error": f"Folder not found: {folder}"}

    exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"}
    images = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(tuple(exts))]
    if not images:
        return {"error": "No image files found"}

    results = {"total": len(images), "ok": 0, "fail": 0, "details": []}
    for img in images:
        try:
            res = process_single_image(img, save_mode)
            results["details"].append(res)
            results["ok"] += 1
        except Exception as e:
            results["details"].append({"image": os.path.basename(img), "error": str(e)})
            results["fail"] += 1
    return results

# ---------- CLI ENTRY ----------
def _cli():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_extract_trade.py <image>|<folder> [--batch] [--json-only|--jsonl-only]")
        sys.exit(1)

    target = sys.argv[1]
    batch = "--batch" in sys.argv or os.path.isdir(target)
    mode = "both"
    if "--json-only" in sys.argv: mode = "json"
    if "--jsonl-only" in sys.argv: mode = "jsonl"

    if batch:
        print(f"🗂 Batch processing folder: {target}")
        print(json.dumps(process_multiple_images(target, mode), indent=2))
    else:
        print(json.dumps(process_single_image(target, mode), indent=2))

if __name__ == "__main__":
    _cli()