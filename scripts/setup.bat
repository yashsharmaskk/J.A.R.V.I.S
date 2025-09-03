@echo off
setlocal EnableDelayedExpansion
echo ========================================
echo    JARVIS AI Assistant - Complete Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Not running as administrator. Some installations may fail.
    echo 💡 Consider running as administrator if you encounter issues.
    echo.
    timeout /t 3 >nul
)

REM Check if Python is available
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! 
    echo 💡 Please install Python 3.8+ from https://python.org
    echo 💡 Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check Python version (ensure it's 3.8+)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3.8+ required. Current version: %PYTHON_VERSION%
    echo 💡 Please upgrade Python to 3.8 or higher
    pause
    exit /b 1
)
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found!
    echo 💡 Please run this script from the JARVIS project root directory
    echo 💡 Current directory: %CD%
    pause
    exit /b 1
)

REM Create virtual environment
echo 🔄 Setting up virtual environment...
if exist ".venv" (
    echo ⚠️  Virtual environment already exists. 
    choice /C YN /M "Remove existing environment and create fresh one? (Y/N)"
    if !errorlevel! equ 1 (
        echo 🗑️  Removing old virtual environment...
        rmdir /s /q .venv
    ) else (
        echo ℹ️  Using existing virtual environment...
        goto :activate_env
    )
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    echo 💡 Try: python -m pip install --upgrade pip
    pause
    exit /b 1
)

echo ✅ Virtual environment created

:activate_env
REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip first
echo 🔄 Upgrading pip to latest version...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo ⚠️  Pip upgrade failed, continuing anyway...
)

REM Check if CUDA is available
echo 🔍 Checking for NVIDIA GPU and CUDA support...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ NVIDIA GPU detected - will install CUDA versions
    set CUDA_AVAILABLE=1
) else (
    echo ℹ️  No NVIDIA GPU detected - will install CPU versions
    set CUDA_AVAILABLE=0
)
echo.

REM Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch (with or without CUDA)
if %CUDA_AVAILABLE% equ 1 (
    echo � Installing PyTorch with CUDA 12.1 support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    if !errorlevel! neq 0 (
        echo ⚠️  CUDA PyTorch installation failed. Trying CUDA 11.8...
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        if !errorlevel! neq 0 (
            echo ⚠️  All CUDA versions failed. Installing CPU version...
            pip install torch torchvision torchaudio
        )
    )
) else (
    echo 💻 Installing PyTorch CPU version...
    pip install torch torchvision torchaudio
)

REM Install llama-cpp-python (with or without CUDA)
echo 🦙 Installing llama-cpp-python...
if %CUDA_AVAILABLE% equ 1 (
    echo    Attempting CUDA version...
    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
    if !errorlevel! neq 0 (
        echo    CUDA version failed, trying CUDA 11.8...
        pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118
        if !errorlevel! neq 0 (
            echo    All CUDA versions failed, installing CPU version...
            pip install llama-cpp-python
        )
    )
) else (
    pip install llama-cpp-python
)

REM Install core dependencies with error handling
echo 🔄 Installing core web framework dependencies...
pip install flask>=2.3.0 flask-cors>=4.0.0 starlette>=0.27.0
if %errorlevel% neq 0 (
    echo ❌ Failed to install web framework dependencies
    echo 💡 Check your internet connection and try again
    pause
    exit /b 1
)

echo 🔄 Installing uvicorn with standard extras...
pip install "uvicorn[standard]>=0.22.0"
if %errorlevel% neq 0 (
    echo ⚠️  uvicorn[standard] failed, installing basic uvicorn...
    pip install uvicorn>=0.22.0
)

REM Install Whisper dependencies
echo 🎤 Installing Whisper speech recognition...
pip install openai-whisper>=20231117
if %errorlevel% neq 0 (
    echo ⚠️  OpenAI Whisper installation failed, trying alternatives...
)

pip install faster-whisper>=1.0.0
if %errorlevel% neq 0 (
    echo ⚠️  faster-whisper installation failed
)

REM Install audio dependencies with multiple fallback methods
echo 🔊 Installing audio processing dependencies...
pip install numpy>=1.24.0 sounddevice>=0.4.6
if %errorlevel% neq 0 (
    echo ❌ Failed to install numpy/sounddevice
)

echo 🎵 Installing PyAudio (may require Visual Studio Build Tools)...
pip install pyaudio>=0.2.13
if %errorlevel% neq 0 (
    echo ⚠️  PyAudio pip installation failed. Trying alternative methods...
    
    REM Try pipwin method
    pip install pipwin
    if !errorlevel! equ 0 (
        pipwin install pyaudio
        if !errorlevel! neq 0 (
            echo ⚠️  pipwin method also failed
        )
    )
    
    REM Try conda if available
    conda --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo 🐍 Trying conda installation for PyAudio...
        conda install -c conda-forge pyaudio -y
    )
    
    if !errorlevel! neq 0 (
        echo ❌ All PyAudio installation methods failed
        echo 💡 Manual solutions:
        echo    1. Install Visual Studio Build Tools
        echo    2. Use conda: conda install pyaudio
        echo    3. Download pre-compiled wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/
        echo ⚠️  JARVIS will use Web Speech API fallback without PyAudio
    )
)

REM Install remaining dependencies from requirements.txt
echo 📦 Installing remaining dependencies...
pip install requests>=2.31.0 aiohttp>=3.8.0 rich>=13.0.0 colorama>=0.4.6
pip install pyttsx3>=2.90 typing-extensions>=4.0.0 pydantic>=2.0.0

REM Optional dependencies (don't fail if these don't work)
echo 🔧 Installing optional dependencies...
pip install langchain>=0.1.0 langchain-community>=0.0.10 langchain-ollama>=0.1.0 2>nul
pip install librosa>=0.10.0 scipy>=1.10.0 2>nul

REM Test critical imports
echo 🧪 Testing critical installations...
python -c "import flask, starlette, uvicorn; print('✅ Web framework OK')" 2>nul
if %errorlevel% neq 0 echo ❌ Web framework test failed

python -c "import torch; print('✅ PyTorch OK')" 2>nul
if %errorlevel% neq 0 echo ❌ PyTorch test failed

python -c "from llama_cpp import Llama; print('✅ llama-cpp-python OK')" 2>nul
if %errorlevel% neq 0 echo ❌ llama-cpp-python test failed

python -c "import whisper; print('✅ Whisper OK')" 2>nul
if %errorlevel% neq 0 echo ⚠️  Whisper test failed (will use Web Speech API)

python -c "import pyaudio; print('✅ PyAudio OK')" 2>nul
if %errorlevel% neq 0 echo ⚠️  PyAudio test failed (will use Web Speech API)

echo.
echo ========================================
echo 🎉 JARVIS AI Assistant Setup Complete!
echo ========================================
echo.
echo � Installation Summary:
echo ✅ Virtual Environment: .venv
echo ✅ Python Version: %PYTHON_VERSION%
if %CUDA_AVAILABLE% equ 1 (
    echo ✅ GPU Support: NVIDIA CUDA detected
) else (
    echo ✅ CPU Mode: No GPU detected ^(still works great!^)
)
echo ✅ Web Framework: Flask + Starlette + Uvicorn
echo ✅ AI Engine: llama-cpp-python
echo ✅ Speech: Whisper ^(+ Web Speech API fallback^)
echo.
echo 🚀 Quick Start Instructions:
echo.
echo 1️⃣  ACTIVATE ENVIRONMENT:
echo    .venv\Scripts\activate.bat
echo.
echo 2️⃣  START JARVIS SERVER:
echo    python src\core\server.py
echo.
echo 3️⃣  OPEN IN BROWSER:
echo    http://localhost:5000
echo.
echo 💡 Alternative URLs:
echo    Main Interface: http://localhost:5000/
echo    New Interface:  http://localhost:5000/new  
echo    Classic:        http://localhost:5000/old
echo.
echo � Troubleshooting:
echo    • If model not found: Download models to models/ folder
echo    • If PyAudio issues: Install Visual Studio Build Tools
echo    • If GPU not working: Check NVIDIA drivers
echo    • For help: Check README.md or GitHub issues
echo.
echo 📁 Important Files:
echo    🤖 Server: src\core\server.py
echo    🌐 Frontend: src\frontend\index.html  
echo    📋 Config: requirements.txt
echo    🎯 Models: models\ folder
echo.
choice /C YN /M "Start JARVIS now? (Y/N)"
if %errorlevel% equ 1 (
    echo.
    echo 🚀 Starting JARVIS...
    python src\core\server.py
) else (
    echo.
    echo 💡 To start later, run: python src\core\server.py
    echo 😊 Happy AI chatting!
)

pause
