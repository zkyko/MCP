import os
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import json
from datetime import datetime
from openai import OpenAI

# Load env vars
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DeepSeek_api_key"),
    base_url=os.getenv("DeepSeek_api_base")
)

# Step 1: Extract raw text from image
def extract_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

# Step 2: Ask DeepSeek to summarize as structured JSON
def summarize_trade_from_text(raw_text: str) -> str:
    prompt = f"""
You are an intelligent trading assistant. A trader has uploaded a screenshot of their chart.
The OCR-extracted text is below. Analyze it and output a JSON object with as much structure as possible.

OCR TEXT:
\"\"\"
{raw_text}
\"\"\"

Extract and infer the following:
- ticker (e.g., BTCUSD)
- timeframe (e.g., 3min, 5min, etc.)
- entry price
- exit price
- direction (long or short)
- PnL (if visible)
- date/time (if visible)
- reason or annotations (if visible)

Return only the JSON object.
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Step 3: Format the JSON output
def log_trade_json(json_string, log_path="logs/trade_log.jsonl"):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # 🔥 Strip Markdown code fences
    if json_string.strip().startswith("```json"):
        json_string = json_string.strip()[7:-3].strip()
    elif json_string.strip().startswith("```"):
        json_string = json_string.strip()[3:-3].strip()

    try:
        trade = json.loads(json_string)
    except json.JSONDecodeError as e:
        print("❌ Could not parse DeepSeek response as JSON.")
        print("🔍 Error:", e)
        return

    # Auto-tag with timestamp
    trade["logged_at"] = datetime.now().isoformat()

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(trade) + "\n")

    print(f"\n📁 Trade logged to {log_path}")


# Entrypoint
if __name__ == "__main__":
    image_path = "trade_test.png"  # Change to your image name
    ocr_text = extract_text_from_image(image_path)

    result_json = summarize_trade_from_text(ocr_text)
    print("\n🧠 DeepSeek JSON Output:\n", result_json)

    # ✅ Log it!
    log_trade_json(result_json)

    print("\n✅ Trade analysis complete!")
    print("You can now view the structured trade data in logs/trade_log.jsonl")
# Note: Ensure you have the required packages installed:
# pip install openai python-dotenv pytesseract pillow