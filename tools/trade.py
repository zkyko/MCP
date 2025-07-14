import os
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# === Path Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADE_LOG_PATH = os.path.join(BASE_DIR, "logs", "trade_log.jsonl")

# ---------- Schemas ----------

class TradeSummary(BaseModel):
    ticker: Optional[str] = None
    timeframe: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    direction: Optional[str] = None
    pnl: Optional[str] = None
    pnl_amount: Optional[float] = None
    date_time: Optional[str] = None
    reason_or_annotations: Optional[str] = None
    logged_at: Optional[str] = None

class SearchTradeInput(BaseModel):
    query: str = ""

class SearchTradeOutput(BaseModel):
    results: List[TradeSummary]
    total_found: int

# ---------- Search Function ----------

def search_trade_logs(query: str = "", limit: int = 10) -> dict:
    """Search through trade logs"""
    
    if not os.path.exists(TRADE_LOG_PATH):
        print(f"⚠️  Trade log file not found at: {TRADE_LOG_PATH}")
        return {"results": [], "total_found": 0, "message": f"No trade log file found at {TRADE_LOG_PATH}"}

    matches = []
    total_count = 0
    
    try:
        with open(TRADE_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    total_count += 1
                    
                    # If no query, return all trades
                    if not query or query.lower() in json.dumps(trade).lower():
                        matches.append(trade)
                        
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return {"results": [], "total_found": 0, "error": f"Failed to read log file: {str(e)}"}

    # Limit results
    limited_matches = matches[-limit:] if matches else []
    
    return {
        "results": limited_matches,
        "total_found": len(matches),
        "total_trades": total_count
    }

def parse_pnl_amount(pnl_str: str) -> Optional[float]:
    """Parse PnL string to float value"""
    if not pnl_str:
        return None
    
    # Remove common symbols and normalize
    pnl_clean = str(pnl_str).replace('$', '').replace(',', '').replace('+', '').strip()
    
    try:
        return float(pnl_clean)
    except (ValueError, TypeError):
        return None

def get_trade_stats() -> dict:
    """Get comprehensive statistics about trades"""
    
    if not os.path.exists(TRADE_LOG_PATH):
        print(f"⚠️  Trade log file not found at: {TRADE_LOG_PATH}")
        return {
            "total_trades": 0,
            "win_rate": None,
            "total_pnl": None,
            "best_trade": None,
            "worst_trade": None,
            "pnl_history": [],
            "message": f"No trade log file found at {TRADE_LOG_PATH}"
        }
    
    trades = []
    with open(TRADE_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                trade = json.loads(line.strip())
                trades.append(trade)
            except json.JSONDecodeError:
                continue
    
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": None,
            "total_pnl": None,
            "best_trade": None,
            "worst_trade": None,
            "pnl_history": [],
            "message": "No trades found in log"
        }
    
    # Calculate comprehensive stats
    total_trades = len(trades)
    tickers = set()
    directions = {"long": 0, "short": 0, "buy": 0, "sell": 0}
    pnl_amounts = []
    pnl_history = []
    winning_trades = 0
    
    for trade in trades:
        # Collect tickers
        if trade.get("ticker"):
            tickers.add(trade["ticker"])
        
        # Count directions
        if trade.get("direction"):
            direction = trade["direction"].lower()
            if direction in directions:
                directions[direction] += 1
        
        # Parse PnL amounts
        pnl_amount = None
        if trade.get("pnl_amount") is not None:
            pnl_amount = trade["pnl_amount"]
        elif trade.get("pnl"):
            pnl_amount = parse_pnl_amount(trade["pnl"])
        
        if pnl_amount is not None:
            pnl_amounts.append(pnl_amount)
            if pnl_amount > 0:
                winning_trades += 1
            
            # Add to PnL history
            date = trade.get("date_time", trade.get("logged_at", "Unknown"))
            if date:
                try:
                    # Try to parse and format date
                    if "T" in date:
                        parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
                        formatted_date = parsed_date.strftime("%Y-%m-%d")
                    else:
                        formatted_date = date.split(" ")[0] if " " in date else date
                except:
                    formatted_date = date
                
                pnl_history.append({
                    "date": formatted_date,
                    "pnl": pnl_amount,
                    "ticker": trade.get("ticker", "Unknown")
                })
    
    # Calculate final statistics
    total_pnl = sum(pnl_amounts) if pnl_amounts else None
    win_rate = (winning_trades / len(pnl_amounts)) if pnl_amounts else None
    best_trade = max(pnl_amounts) if pnl_amounts else None
    worst_trade = min(pnl_amounts) if pnl_amounts else None
    
    # Sort PnL history by date
    pnl_history.sort(key=lambda x: x["date"])
    
    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "winning_trades": winning_trades,
        "losing_trades": len(pnl_amounts) - winning_trades if pnl_amounts else 0,
        "total_pnl": total_pnl,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "average_pnl": total_pnl / len(pnl_amounts) if pnl_amounts else None,
        "unique_tickers": len(tickers),
        "tickers": list(tickers),
        "directions": directions,
        "pnl_history": pnl_history,
        "trades_with_pnl": len(pnl_amounts),
        "latest_trade": trades[-1] if trades else None
    }

# ---------- STANDALONE USAGE ----------

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"🔍 Searching for: '{query}'")
        result = search_trade_logs(query)
    else:
        print("📊 Getting trade statistics...")
        result = get_trade_stats()
    
    print("\n" + "="*50)
    print("📈 TRADE SEARCH RESULT")
    print("="*50)
    print(json.dumps(result, indent=2))