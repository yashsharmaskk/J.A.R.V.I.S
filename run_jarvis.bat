@echo off
echo.
echo ==========================================
echo    🤖 JARVIS AI Assistant v2.0 (Clean)
echo ==========================================
echo.

REM Check if Ollama is running
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Ollama is running
) else (
    echo ❌ Ollama not detected - will use basic mode
    echo 💡 To enable AI: Start Ollama with "ollama serve"
)

echo.
echo Starting Clean Jarvis Implementation...
echo.

cd /d "a:\Jarvis"
"A:/Jarvis/.venv/Scripts/python.exe" jarvis_clean.py --personality iron_man_jarvis

echo.
echo Jarvis has stopped.
pause
