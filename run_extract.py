from tools.extract_trade import extract_trade_core, TradeOutput
import argparse
import json
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract trade from chart image using OCR + DeepSeek")
    parser.add_argument("--image", required=True, help="Path to the image file")
    args = parser.parse_args()

    image_path = args.image
    print(f"🔍 Processing image: {image_path}")

    result = extract_trade_core(image_path)

    output_dir = "trade_logs"
    os.makedirs(output_dir, exist_ok=True)
    image_name = os.path.basename(image_path)
    output_path = os.path.join(output_dir, f"{image_name}.json")

    if isinstance(result, dict):
        print("✅ Output is dict:")
        print(json.dumps(result, indent=2))
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)

    elif isinstance(result, TradeOutput):
        print("✅ Output is TradeOutput model:")
        print(result.model_dump_json(indent=2))
        with open(output_path, "w") as f:
            f.write(result.model_dump_json(indent=2))

    else:
        print("❌ Unknown output format. Type:", type(result))
        with open(output_path, "w") as f:
            f.write(json.dumps({"error": "Unknown output format"}, indent=2))
