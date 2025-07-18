# Trading Analysis UI & MCP Project



## Overview        ✅ instead of ##Overview



This project is a part of the **MCP (Model Context Protocol)** ecosystem, providing a modern web-based UI and API for uploading, processing, and analyzing trading screenshots. It leverages FastAPI for backend services and React (served via CDN) for the frontend, enabling smart file handling, trade extraction, and analytics.

- **MCP (Model Context Protocol):** A flexible protocol and toolkit for building AI-powered, context-aware applications. This project demonstrates MCP's capabilities in the domain of trading analysis.
- **Trading Analysis UI:** A user-friendly web interface for uploading trade screenshots, extracting trade data, and managing trade logs.

---

## Features        ✅ instead of ##Features

- 🌐 **Web UI**: Drag & drop upload, image paste, and file management
- 🧠 **Automatic Trade Extraction**: Extracts trade data from images using OCR and custom logic
- 🏷️ **Smart File Naming**: Organizes files by trade metadata and date
- 📁 **File Management**: List, search, and serve uploaded/processed images
- 📊 **Trade Analytics**: Search logs and view trading statistics
- 🔒 **CORS Enabled**: For easy integration with other tools
- 📚 **API Documentation**: Available at `/docs` when the server is running

---

## Directory Structure

```
MCP/
├── analyze_trade.py
├── DeepSeek.py
├── mcp_server.py
├── mcp_trading_server.py
├── mcp.json
├── Ocr.py
├── requirements.txt
├── run_extract.py
├── simple_mcp_server.py
├── test_system.py
├── trade_test.png
├── ui_server.py         # Main FastAPI server (UI & API)
├── web_api_server.py
├── logs/
│   └── trade_log.jsonl
├── tools/
│   ├── __init__.py
│   ├── extract_trade.py  # Trade extraction logic
│   └── trade.py          # Trade log search & stats
├── uploads/            # Uploaded images
├── processed/          # Processed images (by month)
├── static/             # Static files (UI assets)
└── trade_logs/
```

---

## Setup & Installation

1. **Clone the repository**

```sh
git clone <your-repo-url>
cd MCP
```

2. **Install Python dependencies**

```sh
pip install -r requirements.txt
```

3. **(Optional) Configure environment variables**

If you use a `.env` file, place it in the project root.

4. **Run the UI server**

```sh
python ui_server.py
```

The server will start at [http://localhost:8003](http://localhost:8003)

---

## Usage

### Web UI
- Open [http://localhost:8003](http://localhost:8003) in your browser
- Drag & drop or paste trading screenshots to upload and analyze
- View processed images and trade logs

### API Endpoints

- `POST /extract-trade-upload` — Upload and process an image
- `POST /extract-trade` — Extract trade data from an existing image path
- `POST /search-trades` — Search trade logs
- `GET /trading-stats` — Get trading statistics
- `GET /list-images` — List all available images
- `GET /trade-log` — Get raw trade log content
- `GET /file-structure` — Get organized file structure
- `GET /uploads/{filename}` — Serve uploaded files
- `GET /processed/{date_folder}/{filename}` — Serve processed files

API documentation is available at [http://localhost:8003/docs](http://localhost:8003/docs)

---

## Example: Upload and Extract Trade Data

```bash
curl -F "file=@trade_test.png" http://localhost:8003/extract-trade-upload
```

---

## Extending & Customizing

- **Trade Extraction Logic:** Edit `tools/extract_trade.py` to improve OCR or parsing.
- **Trade Analytics:** Edit `tools/trade.py` for custom search/statistics.
- **UI Customization:** The UI is served as a React app via CDN; you can replace the HTML template in `ui_server.py` for a custom frontend.

---


---

## Credits
Nischal Bhandari
- Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), and [Tailwind CSS](https://tailwindcss.com/)
- Part of the Model Context Protocol (MCP) project
#   M C P 
 
 
