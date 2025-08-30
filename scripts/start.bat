@echo off
echo ========================================
echo    JARVIS - Virtual Environment Mode
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo 💡 Run scripts\setup.bat first to create it.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if model exists
if not exist "models\*.gguf" (
    echo ⚠️  No GGUF model found in models\ directory
    echo 🔄 Downloading optimal model for your system...
    python src\utils\download_model.py
)

REM Test Whisper setup
echo 🔄 Testing Whisper setup...
python -c "import whisper; print('✅ Whisper ready'); model = whisper.load_model('tiny'); print('✅ Tiny model loaded')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Whisper not fully ready, will use Web Speech API fallback
) else (
    echo ✅ Whisper is ready!
)

echo.
echo 🚀 Starting JARVIS Web Server...
echo ========================================
echo.

REM Start the server
python src\core\server.py
