@echo off
echo ==========================================
echo    🚀 STARTING TRADING ANALYSIS SYSTEM
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "web_api_server.py" (
    echo ❌ Error: Please run this from the MCP directory
    pause
    exit /b 1
)

echo 📁 Current directory: %CD%
echo.

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    echo Make sure .venv exists and contains Scripts\activate.bat
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Start the backend API server
echo 🚀 Starting Backend API Server (Port 8001)...
start "Trading API Server" cmd /k "python web_api_server.py"

REM Wait a moment for the API server to start
timeout /t 3 /nobreak > nul

REM Start the correct MCP server
echo 🔗 Starting MCP Server...
start "MCP Trading Server" cmd /k "python mcp_server.py"

REM Wait a moment for the MCP server to start
timeout /t 2 /nobreak > nul

REM Start the frontend
echo 🎨 Starting Frontend (Port 5173)...
cd frontend
start "Trading Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================
echo ✅ ALL SERVICES STARTED SUCCESSFULLY!
echo ==========================================
echo.
echo 🌐 Frontend:  http://localhost:5173
echo 📊 API:       http://localhost:8001
echo 📚 API Docs:  http://localhost:8001/docs
echo 🔗 MCP:       Running in background
echo.
echo Press any key to close this window...
echo (The services will continue running in their own windows)
pause > nul
