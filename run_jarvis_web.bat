@echo off
echo ===============================================
echo    🤖 JARVIS WEB INTERFACE LAUNCHER
echo ===============================================
echo.

cd /d "%~dp0"

echo 🔍 Checking Python environment...
if not exist ".venv" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo 🐍 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 📦 Installing web server dependencies...
pip install flask flask-cors

echo.
echo 🧪 Testing server components...
python -c "print('✅ Testing imports...'); import flask; import flask_cors; from jarvis_clean import OllamaAI; print('✅ All components ready!')"

if %errorlevel% neq 0 (
    echo ❌ Component test failed. Please check your installation.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Jarvis Web Interface...
echo ===============================================
echo 🌐 Frontend will be available at:
echo    http://localhost:5000
echo.
echo 💡 To access from other devices on your network:
echo    python jarvis_web_server.py --host 0.0.0.0
echo.
echo ⏹️  Press Ctrl+C to stop the server
echo ===============================================
echo.

python jarvis_web_server.py

echo.
echo 👋 Jarvis Web Interface stopped.
pause
