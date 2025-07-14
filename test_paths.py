#!/usr/bin/env python3
"""
Test script to verify absolute paths are working correctly
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.trade import TRADE_LOG_PATH, get_trade_stats
from tools.enhanced_extract_trade import TRADE_LOG_PATH as EXTRACT_LOG_PATH, OUTPUT_DIR, SUMMARIES_DIR

def test_paths():
    print("🔍 Testing Absolute Paths Configuration")
    print("=" * 50)
    
    # Get current working directory
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.abspath(__file__)}")
    
    # Test paths from different modules
    print(f"\n📁 Path Configuration:")
    print(f"  Trade log (tools/trade.py): {TRADE_LOG_PATH}")
    print(f"  Trade log (enhanced_extract): {EXTRACT_LOG_PATH}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Summaries directory: {SUMMARIES_DIR}")
    
    # Check if paths exist
    print(f"\n📂 Path Status:")
    print(f"  Trade log exists: {os.path.exists(TRADE_LOG_PATH)}")
    print(f"  Output dir exists: {os.path.exists(OUTPUT_DIR)}")
    print(f"  Summaries dir exists: {os.path.exists(SUMMARIES_DIR)}")
    
    # Check if directories can be created
    try:
        os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(SUMMARIES_DIR, exist_ok=True)
        print(f"  ✅ All directories created successfully")
    except Exception as e:
        print(f"  ❌ Error creating directories: {e}")
    
    # Test trade stats function
    print(f"\n📊 Testing trade stats function:")
    try:
        stats = get_trade_stats()
        print(f"  ✅ Trade stats function works: {stats.get('total_trades', 0)} trades found")
    except Exception as e:
        print(f"  ❌ Error in trade stats: {e}")
    
    print("\n✅ Path testing complete!")

if __name__ == "__main__":
    test_paths()
