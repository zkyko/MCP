# ui_server.py - FastAPI server with UI and smart file handling
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import json
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
import uuid
import re

# Load environment
load_dotenv()

# Import your existing trading functions
from tools.extract_trade import extract_trade_from_image
from tools.trade import search_trade_logs, get_trade_stats

app = FastAPI(title="Trading Analysis UI", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Request models
class TradeImageRequest(BaseModel):
    image_path: str

class SearchRequest(BaseModel):
    query: str = ""
    limit: int = 10

# Smart filename generation
def generate_smart_filename(original_filename: str, trade_data: dict = None) -> str:
    """Generate intelligent filename based on trade data"""
    
    # Extract file extension
    extension = original_filename.split('.')[-1] if '.' in original_filename else 'png'
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Try to create descriptive name from trade data
    if trade_data:
        parts = ['trade']
        
        # Add ticker if available
        if trade_data.get('ticker'):
            ticker = re.sub(r'[^\w]', '', str(trade_data['ticker']))
            parts.append(ticker.lower())
        
        # Add direction if available  
        if trade_data.get('direction'):
            parts.append(trade_data['direction'].lower())
        
        # Add P&L indicator if available
        if trade_data.get('pnl_amount'):
            pnl = trade_data['pnl_amount']
            if isinstance(pnl, (int, float)):
                parts.append('profit' if pnl >= 0 else 'loss')
        
        # Add timestamp
        parts.append(timestamp)
        
        filename = '_'.join(parts) + f'.{extension}'
    else:
        # Fallback to simple naming
        filename = f'trade_{timestamp}.{extension}'
    
    return filename

def save_uploaded_file(file: UploadFile, smart_name: str = None) -> str:
    """Save uploaded file with smart naming"""
    
    # Generate smart filename if not provided
    if not smart_name:
        smart_name = generate_smart_filename(file.filename)
    
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    file_path = os.path.join("uploads", smart_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

def move_to_processed(file_path: str, trade_data: dict) -> str:
    """Move processed file to organized folder structure"""
    
    # Create date-based folder structure
    date_folder = datetime.now().strftime('%Y-%m')
    processed_dir = os.path.join("processed", date_folder)
    os.makedirs(processed_dir, exist_ok=True)
    
    # Generate final smart filename
    original_name = os.path.basename(file_path)
    smart_name = generate_smart_filename(original_name, trade_data)
    
    # Move file
    new_path = os.path.join(processed_dir, smart_name)
    shutil.move(file_path, new_path)
    
    return new_path

# HTML template for the UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Analysis UI</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useRef, useCallback } = React;
        const { Upload, Image, BarChart3, TrendingUp, TrendingDown, Clock, DollarSign, Camera, FileText, Zap } = lucide;

        const TradingAnalysisUI = () => {
            // Your React component code will be injected here
            // This is a placeholder for the actual UI component
            
            return React.createElement('div', { 
                className: 'min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4' 
            }, 
                React.createElement('div', { className: 'max-w-4xl mx-auto text-center' },
                    React.createElement('h1', { className: 'text-4xl font-bold text-gray-800 mb-4' }, 'Trading Analysis UI'),
                    React.createElement('p', { className: 'text-gray-600' }, 'Upload interface is loading...')
                )
            );
        };

        ReactDOM.render(React.createElement(TradingAnalysisUI), document.getElementById('root'));
    </script>
</body>
</html>
"""

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main UI"""
    return HTML_TEMPLATE

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ui": "enabled"}

@app.post("/extract-trade-upload")
async def extract_trade_upload(file: UploadFile = File(...)):
    """Enhanced endpoint with smart file naming"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save with temporary name first
        temp_path = save_uploaded_file(file)
        
        # Process the image to get trade data
        trade_data = extract_trade_from_image(temp_path)
        
        # Generate smart filename based on trade data
        smart_filename = generate_smart_filename(file.filename, trade_data)
        
        # Move to processed folder with smart name
        final_path = move_to_processed(temp_path, trade_data)
        
        # Add metadata
        trade_data.update({
            'original_filename': file.filename,
            'smart_filename': smart_filename,
            'processed_path': final_path,
            'upload_timestamp': datetime.now().isoformat(),
            'file_size': os.path.getsize(final_path)
        })
        
        return {
            "success": True, 
            "data": trade_data,
            "filename": smart_filename,
            "message": f"File saved as: {smart_filename}"
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/extract-trade")
async def extract_trade_endpoint(request: TradeImageRequest):
    """Extract trade data from existing image path"""
    try:
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail=f"Image file not found: {request.image_path}")
        
        result = extract_trade_from_image(request.image_path)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/search-trades")
async def search_trades_endpoint(request: SearchRequest):
    """Search through trade logs"""
    try:
        result = search_trade_logs(request.query, request.limit)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching trades: {str(e)}")

@app.get("/trading-stats")
async def trading_stats_endpoint():
    """Get trading statistics"""
    try:
        result = get_trade_stats()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/list-images")
async def list_images():
    """List available image files"""
    try:
        images = []
        
        # Check uploads folder
        if os.path.exists("uploads"):
            for file in os.listdir("uploads"):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    file_path = os.path.join("uploads", file)
                    images.append({
                        "filename": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "folder": "uploads"
                    })
        
        # Check processed folder
        if os.path.exists("processed"):
            for root, dirs, files in os.walk("processed"):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(root, "processed")
                        images.append({
                            "filename": file,
                            "path": file_path,
                            "size": os.path.getsize(file_path),
                            "folder": f"processed/{rel_path}" if rel_path != "." else "processed"
                        })
        
        return {"success": True, "data": {"images": images, "total": len(images)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@app.get("/trade-log")
async def get_trade_log():
    """Get raw trade log content"""
    try:
        log_path = "logs/trade_log.jsonl"
        if not os.path.exists(log_path):
            return {"success": True, "data": {"trades": [], "message": "No trade log found"}}
        
        trades = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    trade = json.loads(line.strip())
                    trades.append(trade)
                except json.JSONDecodeError:
                    continue
        
        return {"success": True, "data": {"trades": trades, "total": len(trades)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading trade log: {str(e)}")

@app.get("/file-structure")
async def get_file_structure():
    """Get organized file structure information"""
    try:
        structure = {
            "uploads": [],
            "processed": {},
            "logs": []
        }
        
        # Get uploads
        if os.path.exists("uploads"):
            structure["uploads"] = [f for f in os.listdir("uploads") 
                                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        # Get processed files by month
        if os.path.exists("processed"):
            for item in os.listdir("processed"):
                item_path = os.path.join("processed", item)
                if os.path.isdir(item_path):
                    files = [f for f in os.listdir(item_path) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                    if files:
                        structure["processed"][item] = files
        
        # Get log files
        if os.path.exists("logs"):
            structure["logs"] = [f for f in os.listdir("logs") if f.endswith('.jsonl')]
        
        return {"success": True, "data": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file structure: {str(e)}")

# File serving endpoints
@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve uploaded files"""
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/processed/{date_folder}/{filename}")
async def serve_processed(date_folder: str, filename: str):
    """Serve processed files"""
    file_path = os.path.join("processed", date_folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    print("🚀 Starting Trading Analysis UI Server...")
    print("📊 Features enabled:")
    print("  - Web UI for drag & drop upload")
    print("  - Smart file naming and organization")
    print("  - Image paste support")
    print("  - Automatic trade analysis")
    print("  - File management and history")
    print("\n🌐 UI will be available at: http://localhost:8003")
    print("📚 API documentation at: http://localhost:8003/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)