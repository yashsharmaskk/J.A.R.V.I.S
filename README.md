# 🤖 Jarvis AI Assistant

## ✨ What's New in v2.0

- 🏗️ **Clean Architecture**: Proper separation of concerns, modular design
- 🧹 **Project Cleanup**: Removed 20+ old files, organized structure
- 🧠 **Smart Model Routing**: phi3 for quick chats, llama3.1 for complex topics

## 🎭 Available Personalities
- `iron_man_jarvis` - Sophisticated, witty, calls you "sir"
- `professional` - Helpful and concise
- `friendly` - Warm and conversational

## 🧠 Smart Model Routing

Jarvis automatically selects the optimal AI model based on your conversation:

### ⚡ **Quick Mode (phi3)**
**Used for:**
- Simple greetings: "Hello Jarvis"
- Basic questions: "What time is it?"
- Short conversations: "How are you?"
- Quick commands: "Thanks!" 

**Benefits:** Fast response (~1-2 seconds), low resource usage

### 🧠 **Smart Mode (llama3.1)** 
**Used for:**
- Complex topics: "Explain quantum computing"
- Technical questions: "How does machine learning work?"
- Detailed requests: "Write a plan for learning Python"
- Analysis: "Compare different programming languages"
- Creative tasks: "Help me brainstorm ideas"

**Benefits:** Deep understanding, detailed responses, better reasoning

### 🔧 **Manual Override**
You can force a specific model:
- "Use smart mode" - Switch to llama3.1
- "Use fast mode" - Switch to phi3
- "Status report" - See current model

## 📁 Clean Project Structure

```
jarvis/
├── 🤖 jarvis_clean.py          # Main implementation (RECOMMENDED)
├── 🚀 main.py                  # Alternative entry point
├── ⚙️  config/                 # Configuration system
├── 📦 src/                     # Source code modules  
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
