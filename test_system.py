#!/usr/bin/env python3
"""
Test script to verify the trading analysis system is working
"""
import os
import sys
from dotenv import load_dotenv

def test_setup():
    """Test basic setup and dependencies"""
    print("🔧 Testing Trading Analysis System Setup")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    # Test 1: Check dependencies
    print("1. Checking dependencies...")
    missing_deps = []
    
    try:
        import pytesseract
        print("   ✅ pytesseract")
    except ImportError:
        missing_deps.append("pytesseract")
        print("   ❌ pytesseract")
    
    try:
        from PIL import Image
        print("   ✅ PIL (Pillow)")
    except ImportError:
        missing_deps.append("pillow")
        print("   ❌ PIL (Pillow)")
    
    try:
        from openai import OpenAI
        print("   ✅ openai")
    except ImportError:
        missing_deps.append("openai")
        print("   ❌ openai")
    
    try:
        from fastapi import FastAPI
        print("   ✅ fastapi")
    except ImportError:
        missing_deps.append("fastapi")
        print("   ❌ fastapi")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print(f"Run: pip install {' '.join(missing_deps)}")
        return False
    
    # Test 2: Check environment variables
    print("\n2. Checking environment variables...")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE")
    
    if api_key and api_key != "your_deepseek_api_key_here":
        print(f"   ✅ DEEPSEEK_API_KEY: {api_key[:10]}...")
    else:
        print("   ❌ DEEPSEEK_API_KEY not set or using placeholder")
        print("   Update your .env file with a real API key")
        return False
    
    if api_base:
        print(f"   ✅ DEEPSEEK_API_BASE: {api_base}")
    else:
        print("   ⚠️  DEEPSEEK_API_BASE not set, using default")
    
    # Test 3: Check file structure
    print("\n3. Checking file structure...")
    required_files = [
        "main.py",
        "tools/extract_trade.py",
        "tools/trade.py",
        ".env"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} missing")
            return False
    
    # Test 4: Check tools directory
    if not os.path.exists("tools/__init__.py"):
        print("   ⚠️  Creating tools/__init__.py")
        with open("tools/__init__.py", "w") as f:
            f.write("# Tools module\n")
    
    # Test 5: Test OCR
    print("\n4. Testing OCR...")
    try:
        from PIL import Image, ImageDraw
        
        # Create test image
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "BTCUSD 1H LONG", fill='black')
        
        test_image_path = "test_ocr.png"
        img.save(test_image_path)
        
        # Test OCR
        import pytesseract
        text = pytesseract.image_to_string(img)
        print(f"   ✅ OCR test: '{text.strip()}'")
        
        # Clean up
        os.remove(test_image_path)
        
    except Exception as e:
        print(f"   ❌ OCR test failed: {e}")
        print("   Make sure tesseract is installed on your system")
        return False
    
    # Test 6: Test DeepSeek API
    print("\n5. Testing DeepSeek API...")
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url=api_base or "https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Respond with exactly: API_TEST_OK"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        if "API_TEST_OK" in result:
            print("   ✅ DeepSeek API working")
        else:
            print(f"   ⚠️  DeepSeek API responded: {result}")
        
    except Exception as e:
        print(f"   ❌ DeepSeek API test failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("✅ All tests passed! Your system is ready to use.")
    return True

def show_usage():
    """Show usage instructions"""
    print("\n🚀 How to use your trading analysis system:")
    print("="*50)
    print("1. Analyze a trade image:")
    print("   python tools/extract_trade.py your_image.png")
    print()
    print("2. Search your trade logs:")
    print("   python tools/trade.py BTCUSD")
    print("   python tools/trade.py          # Show all stats")
    print()
    print("3. Start the web server:")
    print("   python main.py")
    print()
    print("4. Test the original scripts:")
    print("   python analyze_trade.py       # If you have trade_test.png")
    print("   python Ocr.py image.png       # Just OCR extraction")

if __name__ == "__main__":
    if test_setup():
        show_usage()
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)