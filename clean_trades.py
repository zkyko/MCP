import json
import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

def standardize_ticker(ticker: str) -> str:
    """Normalize ticker formats to standard format"""
    ticker = ticker.strip().upper()
    
    # Map common variations
    ticker_map = {
        "BITCOIN / USD": "BTCUSD",
        "BITCOIN/USD": "BTCUSD", 
        "BTC/USD": "BTCUSD",
        "ETH/USD": "ETHUSD",
        "SOL/USD": "SOLUSD",
        "USD": "USDJPY"  # Assuming this was a JPY trade based on price
    }
    
    return ticker_map.get(ticker, ticker)

def extract_pnl_amount(pnl_value: Any) -> float:
    """Extract float PnL from various formats"""
    if isinstance(pnl_value, (int, float)):
        return float(pnl_value)
    
    if isinstance(pnl_value, str):
        # Remove currency symbols and extract number
        pnl_clean = re.sub(r'[^\d\.\-\+]', '', pnl_value)
        try:
            return float(pnl_clean)
        except ValueError:
            return 0.0
    
    return 0.0

def standardize_datetime(dt_str: str) -> str:
    """Convert various datetime formats to ISO 8601"""
    if not dt_str:
        return datetime.now().isoformat()
    
    # Handle timezone suffix
    dt_str = dt_str.replace(" UTC-5", "").strip()
    
    # Try to parse various formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%b %d, %Y %H:%M"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    
    # If all else fails, return current time
    return datetime.now().isoformat()

def standardize_trade_entry(trade: Dict[str, Any]) -> Dict[str, Any]:
    """Standardize a single trade entry"""
    
    # Generate trade_id if missing
    trade_id = trade.get("trade_id", str(uuid.uuid4())[:8])
    
    # Standardize ticker
    ticker = standardize_ticker(trade.get("ticker", "UNKNOWN"))
    
    # Extract PnL amount
    pnl_amount = 0.0
    if "pnl_amount" in trade:
        pnl_amount = extract_pnl_amount(trade["pnl_amount"])
    elif "pnl" in trade:
        pnl_amount = extract_pnl_amount(trade["pnl"])
    elif "PnL" in trade:
        pnl_amount = extract_pnl_amount(trade["PnL"])
    
    # Standardize datetime
    date_time = standardize_datetime(trade.get("date_time", ""))
    logged_at = standardize_datetime(trade.get("logged_at", ""))
    
    # Return standardized entry
    return {
        "trade_id": trade_id,
        "ticker": ticker,
        "timeframe": trade.get("timeframe"),
        "entry_price": float(trade.get("entry_price", 0)),
        "exit_price": float(trade.get("exit_price", 0)),
        "direction": trade.get("direction", "unknown"),
        "pnl_amount": pnl_amount,
        "date_time": date_time,
        "logged_at": logged_at,
        "image_source": trade.get("image_source"),
        "reason_or_annotations": trade.get("reason_or_annotations"),
        "ocr_confidence": trade.get("ocr_confidence")
    }

# Read and clean trades
input_file = r"C:\Users\Timmy\Documents\MCP\logs\trade_log.jsonl"
standardized_trades = []

# Read existing trades
with open(input_file, 'r') as f:
    for line in f:
        if line.strip():
            try:
                trade = json.loads(line)
                standardized_trade = standardize_trade_entry(trade)
                standardized_trades.append(standardized_trade)
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {line.strip()}")
                continue

# Write standardized trades back
with open(input_file, 'w') as f:
    for trade in standardized_trades:
        f.write(json.dumps(trade) + '\n')

print(f"Cleaned {len(standardized_trades)} trades")

# Show sample of cleaned data
print("\nCleaned trades:")
for i, trade in enumerate(standardized_trades):
    print(f"\nTrade {i+1}:")
    print(json.dumps(trade, indent=2))
