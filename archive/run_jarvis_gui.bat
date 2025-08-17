@echo off
echo.
echo ==========================================
echo    🎨 JARVIS AI Assistant GUI Launcher
echo ==========================================
echo.

REM Check if Ollama is running
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Ollama is running
) else (
    echo ❌ Ollama not detected - GUI will show offline status
    echo 💡 To enable AI: Start Ollama with "ollama serve"
)

echo.
echo Starting JARVIS GUI...
echo.

cd /d "a:\Jarvis"
"A:/Jarvis/.venv/Scripts/python.exe" jarvis_gui.py

echo.
echo JARVIS GUI has closed.
pause
