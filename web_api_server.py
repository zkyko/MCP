# web_api_server.py - Web API for Claude integration
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
import json
import os
import shutil
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

# Load environment
load_dotenv()

# Import trading functions
from tools.extract_trade import process_single_image
from tools.trade import search_trade_logs, get_trade_stats

app = FastAPI(title="Trading Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory as static files (SEPARATE from CORS)
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Request models
class TradeImageRequest(BaseModel):
    image_path: str

class SearchRequest(BaseModel):
    query: str = ""
    limit: int = 10

# API Routes
@app.get("/")
async def root():
    return {"message": "Trading Analysis API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/extract-trade")
async def extract_trade_endpoint(request: TradeImageRequest):
    """Extract trade data from image path"""
    try:
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail=f"Image file not found: {request.image_path}")
        
        result = process_single_image(request.image_path)
        return {"success": True, "data": result}
    except Exception as e:
        print(f"Error in extract_trade_endpoint: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/extract-trade-upload")
async def extract_trade_upload(file: UploadFile = File(...)):
    """Extract trade data from uploaded image"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        print(f"Saving file to: {file_path}")  # Debug logging
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"File saved. Processing image...")  # Debug logging
        
        # Process the image
        result = process_single_image(file_path)
        
        print(f"Processing complete: {result}")  # Debug logging
        
        return {"success": True, "data": result, "message": "Upload and analysis successful!"}
        
    except Exception as e:
        print(f"Error in extract_trade_upload: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        raise HTTPException(status_code=500, detail=f"Error processing uploaded image: {str(e)}")

@app.post("/search-trades")
async def search_trades_endpoint(request: SearchRequest):
    """Search through trade logs"""
    try:
        result = search_trade_logs(request.query, request.limit)
        return {"success": True, "data": result}
    except Exception as e:
        print(f"Error in search_trades_endpoint: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Error searching trades: {str(e)}")

@app.get("/trading-stats")
async def trading_stats_endpoint():
    """Get trading statistics"""
    try:
        result = get_trade_stats()
        return {"success": True, "data": result}
    except Exception as e:
        print(f"Error in trading_stats_endpoint: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/list-images")
async def list_images():
    """List available image files in uploads directory"""
    try:
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        upload_dir = "uploads"
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            return {"success": True, "data": {"images": [], "total": 0}}
        
        images = []
        for file in os.listdir(upload_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                file_path = os.path.join(upload_dir, file)
                images.append({
                    "filename": file,
                    "path": file_path,
                    "url": f"/uploads/{file}",  # Add URL for frontend
                    "size": os.path.getsize(file_path)
                })
        
        return {"success": True, "data": {"images": images, "total": len(images)}}
    except Exception as e:
        print(f"Error in list_images: {str(e)}")  # Debug logging
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
        print(f"Error in get_trade_log: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Error reading trade log: {str(e)}")

# API Documentation
@app.get("/api-docs")
async def api_documentation():
    """API documentation for Claude integration"""
    return {
        "title": "Trading Analysis API",
        "description": "API for analyzing trading screenshots and managing trade logs",
        "base_url": "http://localhost:8001",
        "endpoints": {
            "POST /extract-trade": {
                "description": "Extract trade data from image file path",
                "body": {"image_path": "string"}
            },
            "POST /extract-trade-upload": {
                "description": "Extract trade data from uploaded image",
                "content_type": "multipart/form-data"
            },
            "POST /search-trades": {
                "description": "Search trade history",
                "body": {"query": "string", "limit": "integer"}
            },
            "GET /trading-stats": {
                "description": "Get comprehensive trading statistics"
            },
            "GET /list-images": {
                "description": "List available image files"
            },
            "GET /trade-log": {
                "description": "Get complete trade log"
            }
        }
    }

@app.get("/openapi.json")
async def get_openapi():
    """Return OpenAPI specification for Claude integration"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Trading Analysis API",
            "version": "1.0.0",
            "description": "API for analyzing trading screenshots and managing trade logs"
        },
        "servers": [
            {"url": "http://localhost:8001"}
        ],
        "paths": {
            "/extract-trade": {
                "post": {
                    "summary": "Extract trade data from image",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "image_path": {"type": "string"}
                                    },
                                    "required": ["image_path"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Trade data extracted successfully"
                        }
                    }
                }
            },
            "/search-trades": {
                "post": {
                    "summary": "Search trade history",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string"},
                                        "limit": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Search results"
                        }
                    }
                }
            },
            "/trading-stats": {
                "get": {
                    "summary": "Get trading statistics",
                    "responses": {
                        "200": {
                            "description": "Trading statistics"
                        }
                    }
                }
            },
            "/list-images": {
                "get": {
                    "summary": "List available images",
                    "responses": {
                        "200": {
                            "description": "List of image files"
                        }
                    }
                }
            }
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Trading Analysis Web API...")
    print("📊 Available endpoints:")
    print("  - POST /extract-trade")
    print("  - POST /extract-trade-upload")
    print("  - POST /search-trades")
    print("  - GET /trading-stats")
    print("  - GET /list-images")
    print("  - GET /trade-log")
    print("  - GET /uploads/<filename> (static files)")
    print("\n🌐 API will be available at: http://localhost:8001")
    print("📚 Documentation at: http://localhost:8001/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)