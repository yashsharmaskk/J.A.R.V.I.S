"""
JARVIS Voice Assistant with Ollama Integration

Enhanced voice assistant that integrates with Ollama to use Llama 3.1
for intelligent conversational responses.

Features:
- Speech-to-text with Whisper
- Local LLM responses via Ollama
- Text-to-speech responses
- Graceful error handling for connection issues
"""

import subprocess
import sys
import time
import threading
import json
import requests
from typing import Optional, Dict, Any

# Auto-install required packages
def install_if_missing(package, pip_name=None):
    """Install package if it's missing."""
    pip_name = pip_name or package
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {pip_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

# Install required packages
install_if_missing("pyttsx3")
install_if_missing("whisper", "openai-whisper")
install_if_missing("sounddevice")
install_if_missing("numpy")
install_if_missing("requests")

import pyttsx3
import whisper
import sounddevice as sd
import numpy as np


class OllamaClient:
    """Client for communicating with Ollama API."""
    
    def __init__(self, base_url="http://localhost:11434", model="llama3.1"):
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()
        self.session.timeout = 30
        
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> list:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def chat(self, message: str, system_prompt: str = None) -> Optional[str]:
        """Send a chat message to Ollama and get response."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏱️ Ollama request timed out")
            return None
        except requests.exceptions.ConnectionError:
            print("🔌 Cannot connect to Ollama - is it running?")
            return None
        except Exception as e:
            print(f"❌ Error communicating with Ollama: {e}")
            return None


class JarvisWithOllama:
    """
    Enhanced voice assistant with Ollama/Llama 3.1 integration.
    """
    
    def __init__(self, whisper_model_size="tiny", ollama_model="llama3.1"):
        """
        Initialize Jarvis with Ollama integration.
        
        Args:
            whisper_model_size (str): Whisper model size for speech recognition
            ollama_model (str): Ollama model to use for responses
        """
        print("🚀 Initializing Jarvis with Ollama integration...")
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Load Whisper model
        print(f"📥 Loading Whisper model ({whisper_model_size})...")
        self.whisper_model = whisper.load_model(whisper_model_size)
        
        # Initialize Ollama client
        print(f"🤖 Connecting to Ollama with {ollama_model}...")
        self.ollama = OllamaClient(model=ollama_model)
        
        # Check Ollama availability
        if self.ollama.is_available():
            models = self.ollama.list_models()
            if ollama_model in [m.split(':')[0] for m in models]:
                print(f"✅ Connected to Ollama with {ollama_model}")
                self.ollama_available = True
            else:
                print(f"⚠️ Model {ollama_model} not found. Available models: {models}")
                print("🔄 You can use 'phi3' or pull llama3.1 with: ollama pull llama3.1")
                # Fall back to phi3 if available
                if any("phi3" in m for m in models):
                    self.ollama.model = "phi3"
                    print("📝 Falling back to phi3 model")
                    self.ollama_available = True
                else:
                    self.ollama_available = False
        else:
            print("❌ Ollama not available - falling back to basic responses")
            print("💡 Start Ollama with: ollama serve")
            self.ollama_available = False
        
        # Audio settings
        self.sample_rate = 16000
        self.record_duration = 4
        self.listening = False
        
        # System prompt for Jarvis personality
        self.system_prompt = """You are Jarvis, an intelligent AI assistant. You are helpful, concise, and professional. 
        Keep your responses brief but informative. Address the user as 'sir' when appropriate. 
        You have a sophisticated but friendly personality similar to the AI assistant from Iron Man."""
        
        print("✅ Jarvis is ready with AI capabilities!")
    
    def speak(self, text: str):
        """Convert text to speech and speak it."""
        print(f"🗣️  Jarvis: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self) -> np.ndarray:
        """Record audio from microphone."""
        print("🎤 Listening... (speak now)")
        
        audio = sd.rec(
            int(self.record_duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        
        print("🔇 Recording complete")
        return audio.flatten()
    
    def speech_to_text(self, audio_data: np.ndarray) -> str:
        """Convert audio to text using Whisper."""
        try:
            result = self.whisper_model.transcribe(audio_data, fp16=False)
            text = result['text'].strip()
            
            if text:
                print(f"👂 You said: '{text}'")
                return text
            else:
                print("🤐 No speech detected")
                return ""
                
        except Exception as e:
            print(f"❌ Error transcribing audio: {e}")
            return ""
    
    def get_ai_response(self, user_input: str) -> str:
        """Get response from Ollama or fall back to basic responses."""
        
        if self.ollama_available:
            print("🤔 Thinking... (asking Ollama)")
            
            # Try to get AI response
            ai_response = self.ollama.chat(user_input, self.system_prompt)
            
            if ai_response:
                return ai_response
            else:
                print("⚠️ Ollama request failed, using fallback response")
                self.ollama_available = False  # Temporarily disable
        
        # Fallback to basic responses
        return self.get_basic_response(user_input)
    
    def get_basic_response(self, text: str) -> str:
        """Generate basic responses when Ollama is unavailable."""
        text_lower = text.lower().strip()
        
        if "hello jarvis" in text_lower or "hello" in text_lower:
            return "Hello sir, how can I help you?"
        elif "how are you" in text_lower:
            return "I'm functioning optimally, thank you for asking!"
        elif "what time is it" in text_lower or "time" in text_lower:
            current_time = time.strftime("%I:%M %p")
            return f"The current time is {current_time}, sir."
        elif "thank you" in text_lower or "thanks" in text_lower:
            return "You're welcome, sir!"
        elif "weather" in text_lower:
            return "I don't have access to weather data at the moment, sir."
        elif "who are you" in text_lower or "what are you" in text_lower:
            return "I'm Jarvis, your AI assistant. I'm here to help you with various tasks."
        else:
            return "I understand, sir. How else may I assist you?"
    
    def process_command(self, text: str) -> bool:
        """Process voice command and respond."""
        text_lower = text.lower().strip()
        
        # Handle exit commands
        if any(word in text_lower for word in ["goodbye", "exit", "stop", "quit"]):
            self.speak("Goodbye sir! It was a pleasure assisting you.")
            return False
        
        # Handle reconnect command
        if "reconnect" in text_lower or "restart ollama" in text_lower:
            print("🔄 Attempting to reconnect to Ollama...")
            self.ollama_available = self.ollama.is_available()
            if self.ollama_available:
                self.speak("Ollama connection restored, sir.")
            else:
                self.speak("Unable to connect to Ollama, sir. Operating in basic mode.")
            return True
        
        # Get and speak AI response
        response = self.get_ai_response(text)
        if response:
            self.speak(response)
        else:
            self.speak("I apologize, sir. I'm having difficulty processing that request.")
        
        return True
    
    def run_once(self) -> bool:
        """Listen for one command and respond."""
        try:
            # Record audio
            audio_data = self.listen()
            
            # Convert to text
            text = self.speech_to_text(audio_data)
            
            if text:
                # Process the command
                return self.process_command(text)
            else:
                print("💭 Try speaking louder or closer to the microphone")
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return True
    
    def run_interactive(self):
        """Run in interactive mode - press Enter to record."""
        self.speak("Jarvis AI assistant activated. Press Enter to speak, or type quit to exit.")
        
        while True:
            try:
                user_input = input("\n🎤 Press Enter to record (or 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.speak("Goodbye sir!")
                    break
                
                # Check Ollama status
                if not self.ollama_available and user_input == "":
                    print("🔄 Checking Ollama availability...")
                    self.ollama_available = self.ollama.is_available()
                
                # Listen and respond
                continue_listening = self.run_once()
                if not continue_listening:
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                self.speak("Goodbye sir!")
                break
    
    def run_continuous(self):
        """Run in continuous mode - automatically listens."""
        self.listening = True
        self.speak("Jarvis AI assistant activated and ready for continuous operation, sir.")
        
        while self.listening:
            try:
                print("\n" + "="*50)
                print("🤖 Jarvis is listening...")
                
                # Periodically check Ollama availability
                if not self.ollama_available:
                    self.ollama_available = self.ollama.is_available()
                
                # Listen and respond
                continue_listening = self.run_once()
                if not continue_listening:
                    self.listening = False
                    break
                
                # Brief pause between recordings
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                self.listening = False
                self.speak("Goodbye sir!")
                break


def main():
    """Main function to run Jarvis with Ollama."""
    print("🤖 JARVIS AI Voice Assistant with Ollama")
    print("=" * 50)
    
    try:
        # Create enhanced Jarvis
        jarvis = JarvisWithOllama(
            whisper_model_size="tiny",  # Fast speech recognition
            ollama_model="llama3.1"     # Try llama3.1, fallback to phi3
        )
        
        # Show status
        print(f"\n📊 Status:")
        print(f"   🎤 Speech Recognition: ✅ Ready")
        print(f"   🗣️  Text-to-Speech: ✅ Ready")
        print(f"   🤖 AI (Ollama): {'✅ Connected' if jarvis.ollama_available else '❌ Unavailable'}")
        
        if not jarvis.ollama_available:
            print("\n💡 To enable AI features:")
            print("   1. Start Ollama: ollama serve")
            print("   2. Pull model: ollama pull llama3.1")
        
        # Choose mode
        print("\nSelect mode:")
        print("1. Interactive (press Enter to record)")
        print("2. Continuous (always listening)")
        
        choice = input("Choice (1 or 2): ").strip()
        
        if choice == "1":
            jarvis.run_interactive()
        else:
            jarvis.run_continuous()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Make sure you have:")
        print("- A working microphone")
        print("- Ollama installed and running (ollama serve)")
        print("- Llama 3.1 model pulled (ollama pull llama3.1)")


if __name__ == "__main__":
    main()
