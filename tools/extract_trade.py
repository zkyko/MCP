# tools/extract_trade.py

from .enhanced_extract_trade import process_single_image, process_multiple_images

# Unified export for MCP/UI/API layers
extract_trade_from_image = process_single_image
extract_trade_from_folder = process_multiple_images