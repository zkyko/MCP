@echo off
echo ==========================================
echo    🛑 STOPPING TRADING ANALYSIS SYSTEM
echo ==========================================
echo.

echo 🔍 Stopping all related processes...

REM Kill Python processes running our servers
taskkill /f /im python.exe /fi "WINDOWTITLE eq Trading API Server*" 2>nul
taskkill /f /im python.exe /fi "WINDOWTITLE eq MCP Trading Server*" 2>nul

REM Kill Node.js processes (frontend)
taskkill /f /im node.exe /fi "WINDOWTITLE eq Trading Frontend*" 2>nul

REM Alternative: Kill by port (more aggressive)
echo 🔧 Killing processes on ports 8001, 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /f /pid %%a 2>nul

echo.
echo ✅ All trading system processes stopped!
echo.
pause
