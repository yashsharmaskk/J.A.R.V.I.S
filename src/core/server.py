#!/usr/bin/env python3
"""
JARVIS Web Server - Ultra-fast with llama-cpp-python direct integration
Eliminates HTTP overhead by running model directly in Python process
"""

import os
import sys
import logging
import time
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string, send_from_directory, Response
from flask_cors import CORS
from starlette.applications import Starlette
from starlette.middleware.wsgi import WSGIMiddleware

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Wrap our Flask WSGI app into a Starlette ASGI app
asgi_app = Starlette()
asgi_app.mount("/", WSGIMiddleware(app))

# Model configuration
MODEL_PATH = None              # Will be set dynamically
MODEL_INSTANCE = None
speak_hindi = False
GPU_AVAILABLE = False          # torch.cuda.is_available()
LOADED_ON_GPU = False          # whether model loaded on GPU
### Global Variables ###
# Model configuration and status
MODEL_PATH = None              # Will be set dynamically
MODEL_INSTANCE = None
speak_hindi = False
# GPU flags
GPU_AVAILABLE = False          # torch.cuda.is_available()
LOADED_ON_GPU = False          # whether model loaded on GPU

# Try to import llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMACPP_AVAILABLE = True
    logger.info("✅ llama-cpp-python available")
except ImportError:
    LLAMACPP_AVAILABLE = False
    logger.error("❌ llama-cpp-python not available")

# Try to import Whisper
try:
    from whisper_stream import initialize_whisper, start_whisper_recording, stop_whisper_recording, record_whisper_chunk
    WHISPER_AVAILABLE = True
    logger.info("✅ Whisper streaming available")
except ImportError:
    WHISPER_AVAILABLE = False
    logger.error("❌ Whisper streaming not available")

def find_model_file():
    """Find available GGUF model files"""
    common_paths = [
        "models/",
        "../models/",
        "~/.ollama/models/blobs/",
        "C:/Users/*/AppData/Local/Programs/Ollama/",
    ]
    
    model_extensions = [".gguf", ".ggml"]
    model_names = ["qwen2.5", "qwen", "phi-3", "phi3", "llama", "mistral", "tinyllama"]
    
    for base_path in common_paths:
        try:
            path = Path(base_path).expanduser()
            if path.exists():
                for model_file in path.rglob("*"):
                    if model_file.is_file():
                        filename_lower = model_file.name.lower()
                        if any(ext in filename_lower for ext in model_extensions):
                            if any(name in filename_lower for name in model_names):
                                logger.info(f"🎯 Found model: {model_file}")
                                return str(model_file)
        except Exception as e:
            logger.debug(f"Error searching {base_path}: {e}")
    
    return None

def initialize_model():
    """Initialize the llama-cpp model"""
    global MODEL_INSTANCE, MODEL_PATH
    
    if not LLAMACPP_AVAILABLE:
        logger.error("❌ Cannot initialize: llama-cpp-python not available")
        return False
    
    # Find model file
    MODEL_PATH = find_model_file()
    if not MODEL_PATH:
        logger.error("❌ No GGUF model files found. Please download a model.")
        logger.info("💡 You can download models from:")
        logger.info("   - https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf")
        logger.info("   - https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF")
        return False
    
    # Check for CUDA (GPU) availability
    try:
        import torch
        use_cuda = torch.cuda.is_available()
        logger.info(f"ℹ️ CUDA available: {use_cuda}")
    except ImportError:
        use_cuda = False
        logger.info("ℹ️ torch not installed, defaulting to CPU load")

    if use_cuda:
        try:
            logger.info(f"🔥 Loading model on GPU: {MODEL_PATH}")
            MODEL_INSTANCE = Llama(
                model_path=MODEL_PATH,
                n_ctx=2048,
                n_batch=512,
                n_threads=None,
                n_gpu_layers=-1,       # Use all GPU layers
                verbose=False,
                use_mmap=True,
                use_mlock=False,
                f16_kv=True,            # Use fp16 for key/value cache
            )
            logger.info("✅ Model loaded successfully with GPU acceleration!")
            return True
        except Exception as gpu_e:
            logger.warning(f"⚠️ GPU load failed: {gpu_e}. Falling back to CPU...")

    # CPU fallback
    try:
        logger.info(f"🔥 Loading model on CPU: {MODEL_PATH}")
        MODEL_INSTANCE = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_batch=512,
            n_threads=None,
            n_gpu_layers=0,         # CPU only
            verbose=False,
            use_mmap=True,
            use_mlock=False,
            f16_kv=False,           # Use fp32 for CPU compatibility
        )
        logger.info("✅ Model loaded successfully on CPU!")
        return True
    except Exception as cpu_e:
        logger.error(f"❌ CPU load failed: {cpu_e}")
        return False

def chat_with_llamacpp_stream(message, system_prompt="You are JARVIS, AI assistant. Be consice , informative and witty according to question. Respond in 2-3 sentences."):
    """Stream chat responses from llama-cpp-python - OPTIMIZED FOR SPEED"""
    global MODEL_INSTANCE, speak_hindi
    
    if not MODEL_INSTANCE:
        yield f"data: {json.dumps({'content': 'Model not loaded, sir.', 'done': True})}\n\n"
        return
    
    try:
        # Check for instant responses first (ultra-fast)
        instant_responses = {
            "hello": "Hello, sir.",
            "hi": "Greetings, sir.",
            "hey": "Yes, sir?",
            "how are you": "Systems operational, sir.",
            "status": "All systems online.",
            "what's up": "Standing by, sir.",
            "who are you": "I am JARVIS, your AI assistant, sir.",
            "who are u": "I am JARVIS, sir.",
            "what are you": "I am JARVIS, Tony Stark's AI assistant.",
            "your name": "I am JARVIS, sir.",
            "introduce yourself": "I am JARVIS, your personal AI assistant.",
            "good morning": "Good morning, sir.",
            "good evening": "Good evening, sir.",
            "thanks": "You're welcome, sir.",
            "thank you": "My pleasure, sir.",
            "what is ai": "AI is Artificial Intelligence, sir.",
            "what is artificial intelligence": "AI is machine intelligence, sir.",
            "help": "How may I assist you, sir?",
            "test": "Systems operational, sir."
        }
        
        msg_lower = message.lower().strip()
        for key, response in instant_responses.items():
            if key in msg_lower:
                yield f"data: {json.dumps({'content': response, 'done': True})}\n\n"
                return
        
        # Prepare system prompt for Hindi if enabled
        if speak_hindi:
            system_prompt += " कृपया केवल हिंदी में उत्तर दें।"
        
        # Detect model type and format prompt accordingly
        model_name_lower = MODEL_PATH.lower() if MODEL_PATH else ""
        
        if "qwen" in model_name_lower:
            # Qwen2.5 format
            prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"
            stop_tokens = ["<|im_end|>", "<|endoftext|>"]
        elif "phi" in model_name_lower:
            # Phi-3 format
            prompt = f"<|system|>{system_prompt}<|end|><|user|>{message}<|end|><|assistant|>"
            stop_tokens = ["<|end|>", "<|user|>", "<|system|>"]
        else:
            # Generic format
            prompt = f"System: {system_prompt}\n\nUser: {message}\n\nAssistant:"
            stop_tokens = ["\nUser:", "\nSystem:", "\n\n"]
        
        # Generate streaming response (optimized parameters)
        for token in MODEL_INSTANCE(
            prompt,
            max_tokens=150,       # Slightly longer for richer responses
            temperature=0.25,     # Modest randomness for more natural output
            top_p=0.92,           # Wider nucleus sampling for quality
            top_k=50,             # Larger top-k for diverse yet coherent output
            repeat_penalty=1.1,   # Prevent repetition
            stop=stop_tokens,
            echo=False,
            stream=True           # Enable streaming for real-time response
        ):
            content = token['choices'][0]['text']
            if content:
                done = token['choices'][0].get('finish_reason') is not None
                yield f"data: {json.dumps({'content': content, 'done': done})}\n\n"
                if done:
                    break
        
    except Exception as e:
        logger.error(f"Error in streaming generation: {e}")
        yield f"data: {json.dumps({'content': 'An error occurred while processing your request, sir.', 'done': True})}\n\n"

# Fallback responses (for when model isn't loaded)
FALLBACK_RESPONSES = {
    "greeting": "Hello! I'm JARVIS running in basic mode. Model loading required for full AI functionality.",
    "status": "Systems partially online. AI core needs model loading for full functionality.",
    "unknown": "I'm in basic mode. Please ensure the AI model is loaded for full functionality."
}

@app.route('/')
def main_frontend():
    """Serve the main frontend"""
    try:
        # Look for frontend in the organized structure
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        if frontend_path.exists():
            logger.info("📱 Serving main frontend (src/frontend/index.html)")
            with open(frontend_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # No frontend found
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>JARVIS - Web Interface</title></head>
        <body>
            <h1>🤖 JARVIS Web Interface</h1>
            <p>Frontend files not found. Available endpoints:</p>
            <ul>
                <li><a href="/api/status">/api/status</a> - Check system status</li>
                <li>/api/chat (POST) - Chat with JARVIS</li>
                <li>/api/chat/stream (POST) - Chat with JARVIS (streaming)</li>
            </ul>
        </body>
        </html>
        """)
    except Exception as e:
        logger.error(f"Error loading frontend: {e}")
        return f"Error loading frontend: {e}", 500

@app.route('/new')
def new_frontend():
    """Serve the new frontend"""
    try:
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        if frontend_path.exists():
            with open(frontend_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "New frontend not found", 404
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/old')
def old_frontend():
    """Serve the classic frontend"""
    try:
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        if frontend_path.exists():
            with open(frontend_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "Classic frontend not found", 404
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files"""
    try:
        audio_dir = Path(__file__).parent.parent.parent / "audio"
        if audio_dir.exists():
            return send_from_directory(str(audio_dir), filename)
        else:
            return "Audio directory not found", 404
    except Exception as e:
        return f"Error serving audio: {e}", 500

@app.route('/api/status')
def api_status():
    """Get system status"""
    model_loaded = MODEL_INSTANCE is not None
    
    status_info = {
        "jarvis_status": "online",
        "model_status": "loaded" if model_loaded else "not_loaded",
        "model_path": MODEL_PATH if MODEL_PATH else "not_found",
        "llamacpp_available": LLAMACPP_AVAILABLE,
        "gpu_available": GPU_AVAILABLE,
        "loaded_on_gpu": LOADED_ON_GPU,
        "load_device": "gpu" if LOADED_ON_GPU else "cpu",
        "mode": "llamacpp_direct" if model_loaded else "fallback",
        "version": "3.0.0 - LlamaCPP Direct",
        "timestamp": time.time()
    }
    
    return jsonify(status_info)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """DEPRECATED - Redirects to streaming for optimal performance"""
    logger.info("⚠️ /api/chat called - redirecting to use streaming only")
    return jsonify({
        "success": False,
        "error": "Please use /api/chat/stream for optimal performance",
        "redirect": "/api/chat/stream",
        "message": "This endpoint is deprecated. Use streaming API only."
    }), 302

@app.route('/api/whisper/start', methods=['POST'])
def api_whisper_start():
    """Start Whisper recording"""
    if not WHISPER_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Whisper not available"
        }), 400
    
    try:
        success = start_whisper_recording()
        return jsonify({
            "success": success,
            "message": "Recording started" if success else "Failed to start recording"
        })
    except Exception as e:
        logger.error(f"Whisper start error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/whisper/stop', methods=['POST'])
def api_whisper_stop():
    """Stop Whisper recording and get transcription"""
    if not WHISPER_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Whisper not available"
        }), 400
    
    try:
        text = stop_whisper_recording()
        return jsonify({
            "success": True,
            "transcription": text,
            "message": f"Transcribed: {text[:50]}{'...' if len(text) > 50 else ''}"
        })
    except Exception as e:
        logger.error(f"Whisper stop error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/whisper/status')
def api_whisper_status():
    """Get Whisper status"""
    # Test if Whisper is actually working
    whisper_working = False
    if WHISPER_AVAILABLE:
        try:
            from whisper_stream import whisper_recognizer
            whisper_working = (whisper_recognizer is not None and 
                             hasattr(whisper_recognizer, 'model') and 
                             whisper_recognizer.model is not None and
                             hasattr(whisper_recognizer, 'audio') and
                             whisper_recognizer.audio is not None)
        except Exception as e:
            logger.warning(f"Whisper status check failed: {e}")
            whisper_working = False
    
    return jsonify({
        "whisper_available": whisper_working,
        "llamacpp_available": LLAMACPP_AVAILABLE,
        "model_loaded": MODEL_INSTANCE is not None,
        "whisper_module_available": WHISPER_AVAILABLE,
        "fallback_mode": "web_speech_api" if not whisper_working else "whisper"
    })
@app.route('/api/chat/stream', methods=['POST'])
def api_chat_stream():
    """Process chat messages with streaming responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "No message provided"
            }), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({
                "success": False,
                "error": "Empty message"
            }), 400
        
        logger.info(f"🔄 Streaming: {message[:50]}{'...' if len(message) > 50 else ''}")
        
        # Toggle Hindi mode if requested
        global speak_hindi
        if 'talk in hindi' in message.lower():
            speak_hindi = True
            
            def hindi_response():
                yield f"data: {json.dumps({'content': 'ठीक है सर, अब से मैं हिंदी में बात करूँगा।', 'done': True})}\n\n"
            
            return Response(
                hindi_response(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        
        # Check if model is loaded
        if MODEL_INSTANCE:
            system_prompt = "You are JARVIS, Tony Stark's AI assistant. Be helpful and informative. Respond in 2-3 sentences with useful detail."
            
            return Response(
                chat_with_llamacpp_stream(message, system_prompt),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            # Fallback streaming response
            def fallback_response():
                if any(word in message.lower() for word in ["hello", "hi", "hey", "jarvis"]):
                    response = FALLBACK_RESPONSES["greeting"]
                elif any(word in message.lower() for word in ["status", "how are you"]):
                    response = FALLBACK_RESPONSES["status"]
                else:
                    response = FALLBACK_RESPONSES["unknown"]
                
                yield f"data: {json.dumps({'content': response, 'done': True})}\n\n"
            
            return Response(
                fallback_response(),
                mimetype='text/plain',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        
    except Exception as e:
        logger.error(f"Streaming API error: {e}")
        
        def error_response():
            yield f"data: {json.dumps({'content': 'I apologize, sir. An error occurred.', 'done': True})}\n\n"
        
        return Response(
            error_response(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 JARVIS WEB INTERFACE - LLAMACPP DIRECT")
    print("="*60)
    print()
    print("🌐 Frontend URLs:")
    print("   Main:           http://localhost:5000/")
    print("   New Interface:  http://localhost:5000/new")
    print("   Classic:        http://localhost:5000/old")
    print()
    print("📡 API Endpoints:")
    print("   Status:         http://localhost:5000/api/status")
    print("   Chat:           http://localhost:5000/api/chat (POST)")
    print("   Stream:         http://localhost:5000/api/chat/stream (POST)")
    print()
    print("🤖 AI Configuration:")
    
    if not LLAMACPP_AVAILABLE:
        print("   LlamaCPP:       ❌ llama-cpp-python not available")
        print("   💡 Install:     pip install llama-cpp-python")
    elif initialize_model():
        print(f"   Model:          {Path(MODEL_PATH).name}")
        print(f"   Path:           {MODEL_PATH}")
        print("   LlamaCPP:       ✅ Model loaded and ready")
        print("   Mode:           🚀 Direct in-process inference")
    else:
        print("   LlamaCPP:       ⚠️ Model not found or failed to load")
        print("   💡 Download:    Download a GGUF model file")
    
    # Initialize Whisper with error handling
    if WHISPER_AVAILABLE:
        print("   Whisper:        🔄 Initializing base model...")
        try:
            if initialize_whisper("base"):
                print("   Whisper:        ✅ Base model loaded and ready")
                print("   Speech Mode:    🎤 Real-time streaming recognition")
            else:
                print("   Whisper:        ⚠️ Failed to initialize base model, trying tiny...")
                if initialize_whisper("tiny"):
                    print("   Whisper:        ✅ Tiny model loaded and ready")
                    print("   Speech Mode:    🎤 Real-time streaming recognition")
                else:
                    print("   Whisper:        ❌ All model initialization failed")
                    print("   💡 Note:        Server will continue without Whisper (Web Speech API fallback)")
        except Exception as whisper_error:
            print(f"   Whisper:        ❌ Initialization error: {whisper_error}")
            print("   💡 Fallback:    Server will use Web Speech API instead")
            import traceback
            logger.error(f"Whisper initialization failed: {traceback.format_exc()}")
    else:
        print("   Whisper:        ❌ Not available")
        print("   💡 Install:     pip install openai-whisper pyaudio")
    
    print()
    print("🎯 Starting ASGI server with Uvicorn...")
    print("="*60)
    
    # Use Uvicorn for ASGI hosting
    import uvicorn
    try:
        uvicorn.run(asgi_app, host='0.0.0.0', port=5000, log_level="info")
    except Exception as e:
        logger.error(f"🚨 Server startup failed: {e}", exc_info=True)
        # Re-raise to trigger full traceback
        raise
