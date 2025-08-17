"""
Clean Jarvis AI Assistant - Main Entry Point

A well-structured voice assistant with proper separation of concerns.
Uses direct Ollama integration instead of LangChain for simplicity.
"""

import logging
import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import requests

# Audio and AI imports
try:
    import sounddevice as sd
    import numpy as np
    import whisper
    import pyttsx3
    AUDIO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Audio dependencies missing: {e}")
    AUDIO_AVAILABLE = False


@dataclass
class JarvisConfig:
    """Configuration for Jarvis."""
    
    # App info
    app_name: str = "Jarvis AI Assistant"
    version: str = "2.0.0"
    personality: str = "iron_man_jarvis"  # iron_man_jarvis, professional, friendly
    
    # Audio settings
    sample_rate: int = 16000
    record_duration: float = 4.0
    whisper_model: str = "tiny"
    tts_rate: int = 180
    tts_volume: float = 0.9
    
    # AI settings
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    temperature: float = 0.7
    timeout: float = 30.0


class AudioManager:
    """Handles all audio input/output."""
    
    def __init__(self, config):
        if not AUDIO_AVAILABLE:
            raise RuntimeError("Audio dependencies not available")
        # Support both pydantic JarvisConfig (with .audio) and direct AudioConfig/dataclass config
        # If passed a full config with .audio attribute, unwrap to audio-specific settings
        if hasattr(config, 'audio'):
            cfg = config.audio
        else:
            cfg = config
        self.config = cfg
        self.whisper_model = None
        self.tts_engine = None
        self._initialize()
    
    def _initialize(self):
        """Initialize audio components."""
        # Determine which whisper model to load
        if hasattr(self.config, 'whisper_model'):
            model_name = self.config.whisper_model
        elif hasattr(self.config, 'audio') and hasattr(self.config.audio, 'whisper_model'):
            model_name = self.config.audio.whisper_model
        else:
            model_name = 'tiny'
        # Load Whisper
        print(f"📥 Loading Whisper model ({model_name})...")
        self.whisper_model = whisper.load_model(model_name)
        
        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', self.config.tts_rate)
        self.tts_engine.setProperty('volume', self.config.tts_volume)
        
        print("✅ Audio manager ready")
    
    def listen(self) -> Optional[str]:
        """Record and transcribe speech."""
        try:
            print("🎤 Listening... (speak now)")
            
            # Record audio
            audio = sd.rec(
                int(self.config.record_duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            print("🔇 Recording complete")
            
            # Transcribe
            result = self.whisper_model.transcribe(audio.flatten(), fp16=False)
            text = result['text'].strip()
            
            if text:
                print(f"👂 You said: '{text}'")
                return text
            else:
                print("🤐 No speech detected")
                return None
                
        except Exception as e:
            print(f"❌ Audio error: {e}")
            return None
    
    def speak(self, text: str) -> bool:
        """Convert text to speech."""
        try:
            print(f"🗣️  Jarvis: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return False


class OllamaAI:
    """Smart Ollama integration with model routing."""
    
    def __init__(self, config: JarvisConfig):
        self.config = config
        self.conversation_history = []
        
        # Model routing configuration
        self.fast_model = "llama2-uncensored"    # Use llama2-uncensored for all conversations
        self.smart_model = "llama2-uncensored"   # Use llama2-uncensored for complex topics too
        self.current_model = self.fast_model  # Start with llama2-uncensored model
        
        self.system_prompts = {
            "iron_man_jarvis": """You are J.A.R.V.I.S., the AI assistant from Iron Man. You are sophisticated, witty, and occasionally display dry humor. Address the user as 'sir' or 'madam' appropriately. You are highly intelligent and capable. Keep responses precise and to the point - no unnecessary elaboration.""",
            
            "professional": """You are Jarvis, a professional AI assistant. You are helpful, concise, and polite. Provide clear, informative responses while maintaining a respectful tone. Always give precise, direct answers without excessive detail unless specifically requested.""",
            
            "friendly": """You are Jarvis, a friendly AI assistant. You're warm, conversational, and enjoy helping. Maintain an approachable and enthusiastic tone. Keep responses brief and precise while staying friendly."""
        }
        
        # Topic complexity keywords for model routing
        self.complex_topics = {
            'science': ['physics', 'chemistry', 'biology', 'quantum', 'molecular', 'scientific', 'research', 'experiment'],
            'technology': ['programming', 'coding', 'algorithm', 'database', 'software', 'hardware', 'technical', 'development'],
            'analysis': ['analyze', 'explain', 'compare', 'detailed', 'comprehensive', 'in-depth', 'breakdown', 'elaborate'],
            'creative': ['write', 'create', 'story', 'poem', 'essay', 'design', 'brainstorm', 'creative'],
            'academic': ['philosophy', 'history', 'literature', 'mathematics', 'economics', 'political', 'theory'],
            'problem_solving': ['solve', 'calculate', 'plan', 'strategy', 'optimize', 'troubleshoot', 'debug']
        }
    
    def _should_use_smart_model(self, message: str) -> bool:
        """Determine if message requires the smart model."""
        message_lower = message.lower()
        
        # Check for complex topic keywords
        for category, keywords in self.complex_topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return True
        
        # Check for long, detailed questions (likely complex)
        if len(message.split()) > 20:
            return True
        
        # Check for question words indicating complexity
        complex_question_patterns = [
            'how does', 'why does', 'what is the difference',
            'explain how', 'tell me about', 'what are the',
            'how can i', 'what should i', 'help me understand'
        ]
        
        if any(pattern in message_lower for pattern in complex_question_patterns):
            return True
        
        return False
    
    def _select_model(self, message: str) -> str:
        """Select appropriate model based on message complexity."""
        # Always use llama2-uncensored for all conversations
        return "llama2-uncensored"
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.config.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> List[str]:
        """Get available Ollama models."""
        try:
            response = requests.get(f"{self.config.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []
    
    def _model_available(self, model_name: str) -> bool:
        """Check if specific model is available."""
        available_models = self.get_models()
        return any(model_name in model.lower() for model in available_models)
    
    def chat(self, message: str) -> Optional[str]:
        """Send message to Ollama with smart model routing."""
        try:
            # Select appropriate model
            selected_model = self._select_model(message)
            
            # Check if selected model is available, fallback if needed
            if not self._model_available(selected_model):
                if selected_model == self.smart_model and self._model_available(self.fast_model):
                    selected_model = self.fast_model
                    print(f"⚠️  {self.smart_model} unavailable, using {self.fast_model}")
                elif selected_model == self.fast_model and self._model_available(self.smart_model):
                    selected_model = self.smart_model
                    print(f"⚠️  {self.fast_model} unavailable, using {self.smart_model}")
                else:
                    # Use whatever model is configured as default
                    selected_model = self.config.ollama_model
            
            # Indicate which model is being used
            if selected_model != self.current_model:
                self.current_model = selected_model
                model_emoji = "🧠" if selected_model == self.smart_model else "⚡"
                print(f"{model_emoji} Switching to {selected_model} for this query...")
            
            # Build conversation context
            messages = [
                {"role": "system", "content": self.system_prompts.get(self.config.personality, self.system_prompts["professional"])}
            ]
            
            # Add recent history (last 6 messages for fast model, 10 for smart model)
            history_limit = 10 if selected_model == self.smart_model else 6
            recent_history = self.conversation_history[-history_limit:] if len(self.conversation_history) > history_limit else self.conversation_history
            
            for msg in recent_history:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Adjust timeout based on model complexity
            timeout = self.config.timeout if selected_model == self.smart_model else 15.0
            
            payload = {
                "model": selected_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature
                }
            }
            
            thinking_emoji = "🤔" if selected_model == self.smart_model else "💭"
            print(f"{thinking_emoji} Thinking with {selected_model}...")
            
            response = requests.post(
                f"{self.config.ollama_url}/api/chat",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("message", {}).get("content", "").strip()
                
                if ai_response:
                    # Store in history with model info
                    self.conversation_history.append({
                        "user": message,
                        "assistant": ai_response,
                        "model": selected_model,
                        "timestamp": time.time()
                    })
                    
                    return ai_response
            
        except requests.exceptions.Timeout:
            print(f"⏱️ {selected_model} request timed out")
        except requests.exceptions.ConnectionError:
            print("🔌 Cannot connect to Ollama")
        except Exception as e:
            print(f"❌ AI error: {e}")
        
        return None
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        print("🧹 Conversation history cleared")


class JarvisAssistant:
    """Main Jarvis assistant orchestrator."""
    
    def __init__(self, config: Optional[JarvisConfig] = None):
        self.config = config or JarvisConfig()
        self.running = False
        
        # Initialize components
        if AUDIO_AVAILABLE:
            self.audio = AudioManager(self.config)
        else:
            self.audio = None
            print("⚠️  Audio unavailable - text-only mode")
        
        self.ai = OllamaAI(self.config)
        
        print(f"✅ {self.config.app_name} v{self.config.version} ready!")
    
    def get_fallback_response(self, message: str) -> str:
        """Get response when AI is unavailable."""
        message_lower = message.lower()
        
        responses = {
            "hello": "Hello sir, how can I help you?",
            "how are you": "I'm functioning optimally, thank you for asking!",
            "time": f"The current time is {time.strftime('%I:%M %p')}, sir.",
            "thanks": "You're welcome, sir!",
            "status": "All systems operational, sir."
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        return "I understand, sir. How else may I assist you?"
    
    def process_message(self, message: str) -> Optional[str]:
        """Process user message and generate response."""
        # Check for exit commands
        if any(word in message.lower() for word in ["goodbye", "exit", "quit", "stop"]):
            return None  # Signal to exit
        
        # Check for control commands
        if "clear history" in message.lower():
            self.ai.clear_history()
            return "Conversation history cleared, sir."
        
        if "status" in message.lower():
            ai_status = "online" if self.ai.is_available() else "offline"
            current_model = getattr(self.ai, 'current_model', 'unknown')
            available_models = ", ".join(self.ai.get_models())
            return f"Status report: AI system is {ai_status}, current model: {current_model}, available models: {available_models}."
        
        if "use smart mode" in message.lower() or "switch to llama" in message.lower():
            if self.ai._model_available("llama3.1"):
                self.ai.current_model = self.ai.smart_model
                return "Switched to smart mode with Llama 3.1 for complex discussions, sir."
            else:
                return "Llama 3.1 model not available, sir. Please ensure it's installed with 'ollama pull llama3.1'."
        
        if "use fast mode" in message.lower() or "switch to phi" in message.lower():
            if self.ai._model_available("phi3"):
                self.ai.current_model = self.ai.fast_model
                return "Switched to fast mode with Phi-3 for quick responses, sir."
            else:
                return "Phi-3 model not available, sir. Please ensure it's installed with 'ollama pull phi3'."
        
        # Get AI response
        if self.ai.is_available():
            response = self.ai.chat(message)
            if response:
                return response
            else:
                return "I apologize, sir. I'm having difficulty processing that request."
        else:
            return self.get_fallback_response(message)
    
    def run_interactive(self):
        """Run in interactive mode."""
        self.running = True
        
        print("\n🤖 Starting interactive mode...")
        if self.audio:
            print("Press Enter to speak, or type 'quit' to exit.")
        else:
            print("Audio unavailable. Type your messages or 'quit' to exit.")
        
        try:
            while self.running:
                if self.audio:
                    user_input = input("\n🎤 Press Enter to record (or 'quit'): ").strip()
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    
                    message = self.audio.listen()
                    if not message:
                        continue
                else:
                    message = input("\n💬 Your message: ").strip()
                    if not message or message.lower() in ['quit', 'exit']:
                        break
                
                response = self.process_message(message)
                if response is None:
                    break
                
                if self.audio:
                    self.audio.speak(response)
                else:
                    print(f"🤖 Jarvis: {response}")
                    
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        
        finally:
            self.running = False
            final_message = "Goodbye, sir!"
            if self.audio:
                self.audio.speak(final_message)
            else:
                print(f"🤖 Jarvis: {final_message}")
    
    def run_continuous(self):
        """Run in continuous listening mode."""
        if not self.audio:
            print("❌ Continuous mode requires audio - falling back to interactive")
            return self.run_interactive()
        
        self.running = True
        
        print("\n🤖 Starting continuous mode...")
        self.audio.speak("Jarvis activated for continuous operation. Say goodbye to exit.")
        
        try:
            while self.running:
                print("\n" + "="*50)
                print("🤖 Jarvis is listening...")
                
                message = self.audio.listen()
                if not message:
                    time.sleep(1)
                    continue
                
                response = self.process_message(message)
                if response is None:
                    break
                
                self.audio.speak(response)
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        
        finally:
            self.running = False
            self.audio.speak("Goodbye, sir!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jarvis AI Assistant")
    parser.add_argument("--mode", choices=["interactive", "continuous"], 
                       default="interactive", help="Operation mode")
    parser.add_argument("--personality", choices=["iron_man_jarvis", "professional", "friendly"],
                       default="iron_man_jarvis", help="AI personality")
    parser.add_argument("--model", help="Ollama model to use")
    
    args = parser.parse_args()
    
    # Create config
    config = JarvisConfig()
    if args.personality:
        config.personality = args.personality
    if args.model:
        config.ollama_model = args.model
    
    try:
        print("🤖 JARVIS AI ASSISTANT")
        print("=" * 30)
        
        # Initialize Jarvis
        jarvis = JarvisAssistant(config)
        
        # Check system status
        print(f"\n📊 System Status:")
        print(f"   🎤 Audio: {'✅ Ready' if jarvis.audio else '❌ Unavailable'}")
        print(f"   🤖 AI: {'✅ Online' if jarvis.ai.is_available() else '❌ Offline'}")
        print(f"   👤 Personality: {config.personality}")
        
        if jarvis.ai.is_available():
            available_models = jarvis.ai.get_models()
            has_phi3 = any("phi3" in model.lower() for model in available_models)
            has_llama = any("llama3.1" in model.lower() for model in available_models)
            
            print(f"   ⚡ Fast Model (phi3): {'✅' if has_phi3 else '❌'}")
            print(f"   🧠 Smart Model (llama3.1): {'✅' if has_llama else '❌'}")
            
            if has_phi3 and has_llama:
                print(f"   🎯 Smart Routing: ✅ Enabled")
            elif has_phi3 or has_llama:
                print(f"   🎯 Smart Routing: ⚠️  Limited (missing model)")
            else:
                print(f"   🎯 Smart Routing: ❌ Disabled")
        
        if not jarvis.ai.is_available():
            print("\n💡 To enable AI:")
            print("   1. Start Ollama: ollama serve")
            print("   2. Pull models: ollama pull phi3 && ollama pull llama3.1")
            print("   Jarvis will use basic responses.")
        elif not (any("phi3" in m.lower() for m in jarvis.ai.get_models()) and 
                  any("llama3.1" in m.lower() for m in jarvis.ai.get_models())):
            print(f"\n💡 For optimal experience:")
            missing_models = []
            if not any("phi3" in m.lower() for m in jarvis.ai.get_models()):
                missing_models.append("phi3")
            if not any("llama3.1" in m.lower() for m in jarvis.ai.get_models()):
                missing_models.append("llama3.1")
            print(f"   Pull missing models: ollama pull {' && ollama pull '.join(missing_models)}")
            print("   This enables smart routing: phi3 for quick chats, llama3.1 for complex topics.")
        
        # Run in selected mode
        if args.mode == "continuous" and jarvis.audio:
            jarvis.run_continuous()
        else:
            jarvis.run_interactive()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
