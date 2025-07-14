#!/usr/bin/env python3
"""
Simple MCP server for trading analysis that actually works with Claude.
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Simple imports without extra dependencies
def get_trading_stats():
    """Get trading statistics without external dependencies"""
    log_path = "logs/trade_log.jsonl"
    if not os.path.exists(log_path):
        return {"error": "No trade log file found"}
    
    trades = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    trades.append(trade)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return {"error": f"Failed to read log: {str(e)}"}
    
    if not trades:
        return {"message": "No trades found"}
    
    # Calculate basic stats
    total_trades = len(trades)
    tickers = set()
    directions = {"long": 0, "short": 0}
    
    for trade in trades:
        if trade.get("ticker"):
            tickers.add(trade["ticker"])
        if trade.get("direction"):
            direction = trade["direction"].lower()
            if direction in directions:
                directions[direction] += 1
    
    return {
        "total_trades": total_trades,
        "unique_tickers": len(tickers),
        "tickers": list(tickers),
        "directions": directions,
        "latest_trade": trades[-1] if trades else None
    }

def search_trades(query="", limit=10):
    """Search trades without external dependencies"""
    log_path = "logs/trade_log.jsonl"
    if not os.path.exists(log_path):
        return {"results": [], "total_found": 0, "message": "No trade log found"}

    matches = []
    total_count = 0
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    total_count += 1
                    
                    if not query or query.lower() in json.dumps(trade).lower():
                        matches.append(trade)
                        
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return {"results": [], "total_found": 0, "error": f"Failed to read log: {str(e)}"}

    limited_matches = matches[-limit:] if matches else []
    
    return {
        "results": limited_matches,
        "total_found": len(matches),
        "total_trades": total_count
    }

async def handle_request(request):
    """Handle MCP requests"""
    try:
        method = request.get("method", "")
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "trading-analysis",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "search_trades",
                            "description": "Search through logged trades by query term (ticker, direction, etc.)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search query (ticker symbol, direction like 'long'/'short', etc.)"
                                    },
                                    "limit": {
                                        "type": "integer",
                                        "description": "Maximum number of results to return",
                                        "default": 10
                                    }
                                }
                            }
                        },
                        {
                            "name": "get_trading_stats",
                            "description": "Get comprehensive statistics about all logged trades including total trades, win/loss ratio, and recent activity",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "search_trades":
                result = search_trades(arguments.get("query", ""), arguments.get("limit", 10))
            elif tool_name == "get_trading_stats":
                result = get_trading_stats()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

async def main():
    """Run the MCP server"""
    print("🚀 Starting Simple Trading Analysis MCP Server...", file=sys.stderr)
    
    while True:
        try:
            # Read from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            # Parse JSON-RPC request
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            # Handle request
            response = await handle_request(request)
            
            # Write response to stdout
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Server error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())