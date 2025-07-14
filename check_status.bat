@echo off
echo ==========================================
echo    📊 TRADING SYSTEM STATUS CHECK
echo ==========================================
echo.

echo 🔍 Checking running services...
echo.

REM Check if ports are in use
echo 📡 Port 8001 (API Server):
netstat -an | findstr :8001 | findstr LISTENING > nul
if %errorlevel% == 0 (
    echo    ✅ RUNNING
) else (
    echo    ❌ NOT RUNNING
)

echo 📡 Port 5173 (Frontend):
netstat -an | findstr :5173 | findstr LISTENING > nul
if %errorlevel% == 0 (
    echo    ✅ RUNNING
) else (
    echo    ❌ NOT RUNNING
)

echo.
echo 🔍 Active Python processes:
tasklist /fi "imagename eq python.exe" /fo table 2>nul | findstr python.exe

echo.
echo 🔍 Active Node.js processes:
tasklist /fi "imagename eq node.exe" /fo table 2>nul | findstr node.exe

echo.
echo 🌐 Quick connectivity test:
echo    Testing API server...
curl -s http://localhost:8001/ > nul 2>&1
if %errorlevel% == 0 (
    echo    ✅ API Server responding
) else (
    echo    ❌ API Server not responding
)

echo    Testing Frontend...
curl -s http://localhost:5173/ > nul 2>&1
if %errorlevel% == 0 (
    echo    ✅ Frontend responding
) else (
    echo    ❌ Frontend not responding
)

echo.
echo ==========================================
echo Press any key to exit...
pause > nul
