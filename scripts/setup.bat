@echo off
echo ========================================
echo    JARVIS Virtual Environment Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment
echo 🔄 Creating virtual environment...
if exist ".venv" (
    echo ⚠️  Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created
echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies
echo 🔄 Installing core dependencies...
pip install flask flask-cors starlette uvicorn[standard]

REM Install AI dependencies
echo 🔄 Installing AI dependencies...
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

REM Install PyTorch with CUDA support (for GPU acceleration)
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

REM Install Whisper dependencies
echo 🔄 Installing Faster-Whisper and Torch dependencies...
pip install faster-whisper torch torchaudio

REM Try to install PyAudio
echo 🔄 Installing PyAudio...
pip install pyaudio
if %errorlevel% neq 0 (
    echo ⚠️  PyAudio installation failed. Trying alternative method...
    pip install pipwin
    pipwin install pyaudio
    if %errorlevel% neq 0 (
        echo ❌ PyAudio installation failed. Whisper may not work properly.
        echo 💡 You can install it manually later with: pip install pyaudio
    )
)

echo.
echo ========================================
echo ✅ JARVIS Virtual Environment Ready!
echo ========================================
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To start JARVIS, run:
echo   run_jarvis_venv.bat
echo.
pause
