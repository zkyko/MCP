# mcp_server.py

import asyncio
import json
import os
from typing import Any
from dotenv import load_dotenv
from pydantic import AnyUrl

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ServerCapabilities

# Load environment variables
load_dotenv()

# === Path Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRADE_LOG_PATH = os.path.join(BASE_DIR, "logs", "trade_log.jsonl")

# Ensure logs directory exists
os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)

# Optional failsafe check
if os.path.exists(TRADE_LOG_PATH):
    print(f"✅ Trade log found at: {TRADE_LOG_PATH}")
else:
    print(f"⚠️  Trade log will be created at: {TRADE_LOG_PATH}")

# === Tool Imports ===
from tools.extract_trade import extract_trade_from_image
from tools.trade import search_trade_logs, get_trade_stats

# === Initialize Server ===
server = Server("trading-analysis")

# === Tool List ===
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="extract_trade_from_image",
            description="Extract structured trade info from a trading chart screenshot using OCR + LLM.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to trading chart image"}
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="search_trades",
            description="Search logged trades by term (e.g., ticker, direction).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="get_trading_stats",
            description="Return aggregated stats from all logged trades.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

# === Tool Execution ===
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    arguments = arguments or {}
    try:
        if name == "extract_trade_from_image":
            image_path = arguments.get("image_path", "")
            if not image_path:
                return [TextContent(type="text", text="❌ image_path is required")]
            result = extract_trade_from_image(image_path)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_trades":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            result = search_trade_logs(query, limit)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_trading_stats":
            result = get_trade_stats()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        return [TextContent(type="text", text=f"❓ Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error executing {name}: {str(e)}")]

# === Resource Listing ===
@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    if os.path.exists(TRADE_LOG_PATH):
        return [
            Resource(
                uri=AnyUrl(f"file://{TRADE_LOG_PATH}"),
                name="Trade Log",
                description="Complete trade history in JSONL format.",
                mimeType="application/x-jsonlines"
            )
        ]
    return []

# === Resource Reading ===
@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    if str(uri).startswith("file://"):
        file_path = str(uri)[7:]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return "Unsupported resource URI"

# === Main Entrypoint ===
async def main():
    # Print startup info
    print(" Starting MCP Trading Analysis Server...")
    print(f" Server: trading-analysis v1.0.0")
    print(f"  Tools: {len(await handle_list_tools())} available")
    print(f" Resources: Trade logs and data")
    print(" Server ready - waiting for connections...")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="trading-analysis",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={"listChanged": False},
                    resources={"listChanged": False, "subscribe": False}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())