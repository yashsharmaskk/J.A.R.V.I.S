# J.A.R.V.I.S - AI Assistant

> **Just A Rather Very Intelligent System** - A modern AI assistant with voice recognition, GPU-accelerated inference, and web interface.

## ✨ Features

- 🤖 **GPU-Accelerated AI**: LlamaCPP with CUDA support for RTX series GPUs
- 🎤 **Voice Recognition**: Whisper-based speech-to-text with real-time streaming
- 🌐 **Modern Web Interface**: Clean, responsive frontend with real-time chat
- ⚡ **Ultra-Fast Responses**: Optimized for speed with streaming output
- 🔄 **Fallback Support**: Graceful degradation to CPU/Web Speech API
- 🎯 **Smart Model Selection**: Auto-downloads optimal models for your hardware

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (primary support)
- **Python 3.8+** 
- **NVIDIA GPU** (RTX series recommended) with CUDA 12.1+
- **16GB+ RAM** recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yashsharmaskk/J.A.R.V.I.S.git
   cd J.A.R.V.I.S
   ```

2. **Run the setup script**
   ```bash
   scripts\setup.bat
   ```
   This will:
   - Create a Python virtual environment
   - Install all dependencies including GPU-accelerated PyTorch
   - Download the optimal AI model for your system

3. **Start JARVIS**
   ```bash
   scripts\start.bat
   ```

4. **Open your browser**
   ```
   http://localhost:5000
   ```

That's it! JARVIS should be running with GPU acceleration.

## 🛠️ Manual Installation

If the automated setup doesn't work, follow these manual steps:

### 1. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2. Install Dependencies
```bash
# Install from requirements
pip install -r requirements.txt

# Install GPU-enabled PyTorch (for CUDA 12.1)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install GPU-enabled llama-cpp-python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

### 3. Download AI Model
```bash
python src\utils\download_model.py
```

### 4. Start Server
```bash
python src\core\server.py
```

## 🔧 Configuration

### System Requirements by GPU

| GPU | Recommended Model | VRAM | Performance |
|-----|------------------|------|-------------|
| RTX 3050 Ti | Qwen2.5-7B Q3_K_M | 4GB | Excellent |
| RTX 3060 | Qwen2.5-7B Q4_K_M | 6GB | Outstanding |
| RTX 4060+ | Qwen2.5-7B Q5_K_M | 8GB+ | Maximum |

### Environment Variables

```bash
# Limit CPU threads if needed
set OMP_NUM_THREADS=4
set MKL_NUM_THREADS=4

# Force CPU mode (if GPU issues)
set JARVIS_FORCE_CPU=1
```

## 🎮 Usage

### Web Interface
1. Navigate to `http://localhost:5000`
2. Click the microphone icon to start voice input
3. Type or speak your questions
4. Get instant AI responses

### API Endpoints
```python
# Chat with AI
POST /api/chat
{
    "message": "Hello, how are you?",
    "conversation_id": "optional_id"
}

# Voice transcription
POST /api/transcribe
Content-Type: audio/wav

# Health check
GET /api/status
```

## 🎯 Performance Tuning

### GPU Settings
```python
# In server.py - optimized for speed
"n_gpu_layers": 50,        # GPU acceleration
"n_ctx": 8192,            # Context window  
"temperature": 0.7,       # Creativity balance
"top_p": 0.95,           # Token selection
"repeat_penalty": 1.1,    # Prevent loops
"n_threads": 8           # CPU threads
```

### Audio Quality
- **Sample Rate**: 16kHz (optimal for Whisper)
- **Model**: Whisper Base (accuracy/speed balance)
- **Device**: CPU-only to avoid GPU conflicts

## 📁 Project Structure

```
J.A.R.V.I.S/
├── src/
│   ├── core/              # Core AI and server logic
│   │   ├── server.py      # Main Flask/ASGI server
│   │   └── whisper_stream.py # Voice recognition
│   ├── frontend/          # Web interface
│   │   ├── index.html     # Main interface
│   │   ├── style.css      # Styling
│   │   └── script.js      # JavaScript logic
│   └── utils/             # Utilities and helpers
│       └── download_model.py # Auto model download
├── scripts/               # Setup and start scripts
│   ├── setup.bat         # Environment setup
│   └── start.bat         # Quick start
├── models/               # AI model files (auto-created)
├── audio/                # Audio assets
└── requirements.txt      # Python dependencies
```

## 🔧 Troubleshooting

### Common Issues

#### ❌ "CUDA out of memory" Error
```bash
# Solution 1: Reduce GPU layers
# Edit server.py, reduce n_gpu_layers from 50 to 30

# Solution 2: Force CPU mode
set JARVIS_FORCE_CPU=1
python src\core\server.py
```

#### ❌ "Module not found" Error
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate.bat

# Reinstall dependencies
pip install -r requirements.txt
```

#### ❌ Server Won't Start
```bash
# Check if port 5000 is in use
netstat -an | findstr :5000

# Use different port
set PORT=8080
python src\core\server.py
```

#### ❌ Voice Recognition Not Working
```bash
# Check audio permissions in Windows Settings
# Allow microphone access for your browser

# Test standalone Whisper
python -c "import whisper; print('Whisper OK')"
```

#### ❌ Slow Performance
```bash
# Check GPU status
python -c "import torch; print(torch.cuda.is_available())"

# Monitor GPU memory
nvidia-smi

# Reduce model size if needed
# Use Q3_K_M instead of Q4_K_M in download_model.py
```

### Performance Benchmarks

| Hardware | Model | Load Time | Response Time | VRAM Usage |
|----------|-------|-----------|---------------|------------|
| RTX 4060 | Q4_K_M | 8s | 0.5-1s | 6.2GB |
| RTX 3060 | Q3_K_M | 6s | 0.7-1.2s | 4.8GB |
| RTX 3050 Ti | Q3_K_M | 7s | 1-1.5s | 4.2GB |
| CPU Only | Q3_K_M | 15s | 3-5s | 8GB RAM |

### Debug Mode

Enable detailed logging:
```bash
set JARVIS_DEBUG=1
python src\core\server.py
```

This will show:
- Model loading progress
- GPU memory usage
- Request/response timing
- Error stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **LlamaCPP** - Efficient model inference  
- **Hugging Face** - Model hosting
- **Qwen Team** - Base AI model

---

**Made with ❤️ for the AI community**

> "Sometimes you gotta run before you can walk." - Tony Stark  
├── 📚 docs/                    # Documentation
├── 🗃️  archive/                # Archived old files
├── 📋 requirements.txt         # Dependencies
└── 🚀 run_jarvis.bat          # Quick launcher
```

## 🌟 Key Improvements
- 🚀 **Simplified Codebase**: One main file instead of 15+ scattered files  
- 🧠 **Smart Model Routing**: phi3 for quick chats, llama3.1 for complex topics
- 🔧 **Better Configuration**: Centralized settings with personality options
- 🎯 **LangChain Ready**: Foundation for advanced LangChain integration
- 📦 **Organized Structure**: Professional project layout
- 🧹 **Zero Clutter**: Old files archived, clean workspace

## 🌟 Features

- 🎤 **Speech Recognition**: OpenAI Whisper for accurate transcription
- 🧠 **Smart AI Routing**: Automatically selects best model for each conversation
  - ⚡ **phi3** (2.2GB) - Quick responses for simple conversations
  - 🧠 **llama3.1** (4.9GB) - Deep analysis for complex topics
- 🤖 **AI Conversations**: Local LLM via Ollama (private & fast)
- 🗣️ **Text-to-Speech**: Natural voice responsestant v2.0

**Clean Architecture** | **LangChain Ready** | **Ollama Integration**

A modern, well-structured voice assistant with intelligent AI responses powered by local LLM via Ollama.

## ✨ What's New in v2.0

- 🏗️ **Clean Architecture**: Proper separation of concerns, modular design
- 🚀 **Simplified Codebase**: One main file instead of 15+ scattered files  
- 🔧 **Better Configuration**: Centralized settings with personality options
- 🎯 **LangChain Ready**: Foundation for advanced LangChain integration
- 📦 **Organized Structure**: Professional project layout
- 🧹 **Zero Clutter**: Old files archived, clean workspace

## � Features

- 🎤 **Speech Recognition**: OpenAI Whisper for accurate transcription
- 🤖 **AI Conversations**: Local Llama 3.1 via Ollama (private & fast)
- 🗣️ **Text-to-Speech**: Natural voice responses  
- 🎭 **Personalities**: Iron Man Jarvis, Professional, or Friendly modes
- 🔄 **Graceful Fallbacks**: Works even when AI is offline
- 💬 **Memory**: Remembers conversation contextVoice Assistant

A Python class that can listen for speech, convert it to text using OpenAI's Whisper, and respond with text-to-speech. Specifically responds to "Hello Jarvis" with "Hello sir, how can I help you?"

## 🌟 Features

- 🎤 **Speech Recognition**: Uses OpenAI's Whisper for accurate speech-to-text
- �️ **Text-to-Speech**: Natural voice responses using pyttsx3
- 🤖 **Jarvis Response**: Says "Hello sir, how can I help you?" when you say "Hello Jarvis"
- ⏰ **Time Queries**: Ask "What time is it?"
- 💬 **Basic Conversation**: Responds to greetings and thanks
- 🔄 **Two Modes**: Interactive (press Enter) or Continuous listening

## 🚀 Quick Start

**Easy launcher (recommended):**
```cmd
Double-click: run_jarvis.bat
```

**Manual start:**
```cmd
# 1. Start Ollama (for AI features):
ollama serve

# 2. Run Jarvis:
python jarvis_clean.py

# Or with options:
python jarvis_clean.py --personality iron_man_jarvis --mode continuous
```

**Available personalities:**
- `iron_man_jarvis` - Sophisticated, witty, calls you "sir"
- `professional` - Helpful and concise
- `friendly` - Warm and conversational

## � Project Structure

```
📁 Jarvis/
├── 🚀 jarvis_clean.py      # Main implementation (clean & simple)
├── ⚙️  main.py             # Advanced entry point (LangChain ready)
├── 🎯 run_jarvis.bat       # Windows launcher
├── 📋 requirements.txt     # Dependencies
├── 📖 README.md           # This file
├── 📁 config/             # Configuration system
├── 📁 src/                # Source code (modular architecture)
├── 📁 tests/              # Test files
├── 📁 docs/               # Documentation
└── 📁 archive/            # Old files (archived for cleanup)
```

## 🎯 How to Use

1. **Start Ollama** (in a separate terminal):
   ```cmd
   ollama serve
   ```

2. **Launch Jarvis**:
   ```cmd
   Double-click run_jarvis.bat
   # OR
   python jarvis_with_ollama.py
   ```

3. **Choose your mode**:
   - **Interactive Mode**: Press Enter when you want to speak
   - **Continuous Mode**: Jarvis listens automatically

4. **Try these conversations**:
   - "Hello Jarvis, how are you?" → AI-powered response
   - "Tell me about artificial intelligence" → Detailed explanation
   - "What should I cook for dinner?" → Helpful suggestions
   - "Thank you" → Polite response
   - "Goodbye" → Stops Jarvis

## 🤖 AI vs Basic Mode

**With Ollama (AI Mode)**:
- Intelligent, contextual responses
- Can discuss complex topics
- Learns from conversation context
- Powered by Llama 3.1

**Without Ollama (Basic Mode)**:
- Simple predefined responses
- "Hello sir, how can I help you?"
- Time queries, basic greetings
- Fallback when Ollama is unavailable

## 💻 Code Examples

### Basic Usage
```python
from jarvis_with_ollama import JarvisWithOllama

# Create Jarvis with AI
jarvis = JarvisWithOllama(ollama_model="llama3.1")

# Single interaction
jarvis.run_once()

# Interactive mode
jarvis.run_interactive()
```

### Custom AI Integration
```python
# Test Ollama connection
from jarvis_with_ollama import OllamaClient

client = OllamaClient(model="llama3.1")
if client.is_available():
    response = client.chat("Hello Jarvis!")
    print(response)
```

## Troubleshooting

### Common Issues

1. **Microphone not detected**:
   - Ensure your microphone is connected and working
   - Check Windows audio settings
   - Try running `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

2. **PyAudio installation issues**:
   - On Windows, try: `pip install pipwin` then `pipwin install pyaudio`
   - Or download the appropriate wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

3. **Whisper model loading slow**:
   - First run downloads the model, subsequent runs are faster
   - Use smaller models ("tiny" or "base") for faster loading

4. **Speech recognition not working**:
   - Speak clearly and closer to the microphone
   - Reduce background noise
   - Try adjusting the microphone sensitivity

## System Requirements

- **Python**: 3.7 or higher
- **OS**: Windows, macOS, or Linux
- **Hardware**: Microphone and speakers/headphones
- **Internet**: Required for initial Whisper model download

## Dependencies

- `speech_recognition` - For microphone input handling
- `pyttsx3` - For text-to-speech output
- `openai-whisper` - For accurate speech recognition
- `numpy` - For audio data processing
- `pyaudio` - For microphone access

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this project and submit pull requests for improvements!

---

**Note**: This is a basic implementation. For production use, consider adding error handling, configuration files, and more sophisticated command processing.
