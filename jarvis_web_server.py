#!/usr/bin/env python3
"""
Jarvis Web API Server
Connects the HTML frontend to the Jarvis AI backend
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import asyncio
import threading
import os
import sys
import json
import logging
from pathlib import Path

# Import your Jarvis implementation
try:
    from jarvis_clean import JarvisAssistant
    from config.settings import JarvisConfig as SettingsConfig
except ImportError as e:
    print(f"Error importing Jarvis modules: {e}")
    print("Make sure jarvis_clean.py and config/settings.py are available")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load Pydantic settings
settings = SettingsConfig()
# Map to dataclass config used by JarvisAssistant
from jarvis_clean import JarvisConfig as DataclassConfig
dataclass_config = DataclassConfig(
    app_name=settings.app_name,
    version=settings.version,
    personality=settings.personality,
    sample_rate=settings.audio.sample_rate,
    record_duration=settings.audio.record_duration,
    whisper_model=settings.audio.whisper_model,
    tts_rate=settings.audio.tts_rate,
    tts_volume=settings.audio.tts_volume,
    ollama_url=settings.ai.ollama_url,
    ollama_model=settings.ai.ollama_model,
    temperature=settings.ai.temperature,
    timeout=settings.ai.timeout
)
# Initialize Jarvis components via JarvisAssistant
jarvis = JarvisAssistant(dataclass_config)

class WebJarvis:
    """Web-enabled Jarvis interface"""
    
    def __init__(self):
        self.is_initialized = False
        self.current_personality = "iron_man_jarvis"
        
    def initialize(self):
        """Initialize Jarvis components"""
        try:
            # Set personality in config
            jarvis.config.personality = self.current_personality
            # Test AI availability without sending a message
            if jarvis.ai.is_available() and jarvis.ai.current_model:
                self.is_initialized = True
                logger.info("✅ Jarvis AI initialized successfully")
                return True
            else:
                logger.error("❌ AI is not available or no model loaded")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize Jarvis: {e}")
            return False
    
    def process_query(self, query: str) -> dict:
        """Process user query and return response"""
        try:
            if not self.is_initialized:
                return {
                    "success": False,
                    "response": "I'm not fully online yet. Please wait a moment.",
                    "error": "Not initialized"
                }
            
            # Check for special commands
            query_lower = query.lower().strip()
            
            # Personality switching
            if "iron man mode" in query_lower or "switch to iron man" in query_lower:
                self.current_personality = "iron_man_jarvis"
                return {
                    "success": True,
                    "response": "Switching to Iron Man mode. How may I assist you, sir?",
                    "personality": self.current_personality
                }
            elif "professional mode" in query_lower:
                self.current_personality = "professional"
                return {
                    "success": True,
                    "response": "Switching to professional mode. How can I help you today?",
                    "personality": self.current_personality
                }
            elif "friendly mode" in query_lower:
                self.current_personality = "friendly"
                return {
                    "success": True,
                    "response": "Switching to friendly mode! Hey there, how can I help?",
                    "personality": self.current_personality
                }
            
            # Status check
            if "status" in query_lower and "report" in query_lower:
                model_info = {
                    "current_model": jarvis.ai.current_model,
                    "available_models": jarvis.ai.get_models(),
                    "ai_available": jarvis.ai.is_available()
                }
                return {
                    "success": True,
                    "response": f"All systems operational, sir. Currently using {jarvis.ai.current_model} in {self.current_personality} mode.",
                    "model_info": model_info,
                    "personality": self.current_personality
                }
            
            # Process with AI
            jarvis.config.personality = self.current_personality
            response = jarvis.ai.chat(query)
            
            if response:
                model_info = {
                    "current_model": jarvis.ai.current_model,
                    "available_models": jarvis.ai.get_models(),
                    "ai_available": jarvis.ai.is_available()
                }
                return {
                    "success": True,
                    "response": response,
                    "personality": self.current_personality,
                    "model_info": model_info
                }
            else:
                return {
                    "success": False,
                    "response": "I apologize, sir. I'm experiencing technical difficulties.",
                    "error": "No AI response"
                }
                
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            return {
                "success": False,
                "response": "I encountered an error processing your request, sir.",
                "error": str(e)
            }

# Global Jarvis instance
web_jarvis = WebJarvis()

@app.route('/')
def home():
    """Serve the Jarvis frontend"""
    try:
        frontend_path = Path(__file__).parent / "JARVIS FRONTEND.HTML"
        if frontend_path.exists():
            with open(frontend_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head><title>Jarvis - Frontend Not Found</title></head>
            <body>
                <h1>Jarvis Frontend Not Found</h1>
                <p>Please make sure "JARVIS FRONTEND.HTML" is in the same directory as this server.</p>
                <p>Available endpoints:</p>
                <ul>
                    <li><a href="/api/status">/api/status</a> - Check Jarvis status</li>
                    <li><a href="/api/chat">/api/chat</a> - Chat with Jarvis (POST)</li>
                </ul>
            </body>
            </html>
            """)
    except Exception as e:
        return f"Error loading frontend: {e}", 500

@app.route('/api/status')
def status():
    """Check Jarvis system status"""
    try:
        if not web_jarvis.is_initialized:
            # Try to initialize
            web_jarvis.initialize()
        
        return jsonify({
            "status": "online" if web_jarvis.is_initialized else "offline",
            "personality": web_jarvis.current_personality,
            "ai_available": jarvis.ai.is_available(),
            "models_available": jarvis.ai.get_models(),
            "current_model": jarvis.ai.current_model,
            "timestamp": str(Path(__file__).stat().st_mtime)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat message from frontend"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "No message provided"
            }), 400
        
        query = data['message'].strip()
        if not query:
            return jsonify({
                "success": False,
                "error": "Empty message"
            }), 400
        
        # Process the query
        result = web_jarvis.process_query(query)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize Jarvis system"""
    try:
        success = web_jarvis.initialize()
        return jsonify({
            "success": success,
            "status": "online" if success else "offline",
            "message": "Jarvis initialized successfully" if success else "Failed to initialize Jarvis"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def run_server(host='localhost', port=5000, debug=False, use_https=False):
    """Run the Jarvis web server"""
    protocol = "https" if use_https else "http"
    print(f"""
    🤖 ═══════════════════════════════════════════════════════════
         JARVIS WEB INTERFACE STARTING
    ═══════════════════════════════════════════════════════════
    
    🌐 Frontend URL: {protocol}://{host}:{port}
    🔧 API Status:   {protocol}://{host}:{port}/api/status
    💬 API Chat:     {protocol}://{host}:{port}/api/chat (POST)
    
    🎯 Ready to serve your AI assistant!
    ═══════════════════════════════════════════════════════════
    """)
    
    # Initialize Jarvis in background
    threading.Thread(target=web_jarvis.initialize, daemon=True).start()
    
    # SSL context for HTTPS (optional)
    ssl_context = None
    if use_https:
        try:
            ssl_context = 'adhoc'  # Generate self-signed cert
            print("🔒 Using self-signed SSL certificate (for development only)")
            print("⚠️  You'll need to accept the security warning in your browser")
        except ImportError:
            print("❌ pyOpenSSL required for HTTPS. Install with: pip install pyopenssl")
            print("🔄 Falling back to HTTP...")
            ssl_context = None
    
    # Run Flask server
    app.run(host=host, port=port, debug=debug, threaded=True, ssl_context=ssl_context)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Jarvis Web Interface')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--https', action='store_true', help='Enable HTTPS for speech recognition support')
    
    args = parser.parse_args()
    
    if args.https:
        print("🔒 HTTPS mode requested for speech recognition compatibility")
    
    run_server(args.host, args.port, args.debug, args.https)
