"""
Main Jarvis agent orchestrating all components.
"""

import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Import our core modules
from ..core.audio import AudioManager
from ..core.ai import JarvisAI, FallbackResponses
from config.settings import JarvisConfig, get_personality_prompt

logger = logging.getLogger(__name__)


class OperationMode(Enum):
    """Jarvis operation modes."""
    INTERACTIVE = "interactive"  # Press Enter to speak
    CONTINUOUS = "continuous"   # Always listening
    VOICE_ACTIVATED = "voice_activated"  # Wake word activation


@dataclass
class ConversationContext:
    """Context information for conversations."""
    user_message: str
    ai_response: str
    timestamp: float
    mode: OperationMode
    response_time: float


class JarvisAgent:
    """Main Jarvis AI agent coordinating all components."""
    
    def __init__(self, config: Optional[JarvisConfig] = None):
        if config is None:
            from config.settings import config as default_config
            config = default_config
        
        self.config = config
        self.running = False
        self.mode = OperationMode.INTERACTIVE
        
        # Initialize components
        self._initialize_components()
        
        # Conversation tracking
        self.conversation_history = []
        
        logger.info(f"Jarvis Agent initialized - Version {config.version}")
    
    def _initialize_components(self):
        """Initialize all Jarvis components."""
        try:
            # Audio management
            audio_config = {
                'sample_rate': self.config.audio.sample_rate,
                'channels': self.config.audio.channels,
                'whisper_model': self.config.ai.whisper_model,
                'tts_rate': self.config.audio.tts_rate,
                'tts_volume': self.config.audio.tts_volume
            }
            self.audio = AudioManager(audio_config)
            
            # AI integration
            ai_config = {
                'ollama_base_url': self.config.ai.ollama_base_url,
                'ollama_model': self.config.ai.ollama_model,
                'temperature': self.config.ai.temperature,
                'ollama_timeout': self.config.ai.ollama_timeout
            }
            self.ai = JarvisAI(ai_config)
            
            logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
    
    def speak(self, text: str, log_response: bool = True):
        """Make Jarvis speak."""
        if log_response:
            print(f"🗣️  Jarvis: {text}")
        
        return self.audio.speak_text(text)
    
    def listen(self, duration: float = None) -> Optional[str]:
        """Listen for user input and transcribe."""
        if duration is None:
            duration = self.config.audio.record_duration
        
        print("🎤 Listening... (speak now)")
        text = self.audio.listen_and_transcribe(duration)
        
        if text:
            print(f"👂 You said: '{text}'")
        else:
            print("🤐 No speech detected")
        
        return text
    
    def process_message(self, user_message: str) -> Optional[str]:
        """Process user message and generate response."""
        start_time = time.time()
        
        # Check for exit commands
        if self._is_exit_command(user_message):
            return None  # Signal to exit
        
        # Check for control commands
        control_response = self._handle_control_commands(user_message)
        if control_response:
            return control_response
        
        # Get AI response
        system_prompt = get_personality_prompt(self.config.personality)
        
        if self.ai.is_available():
            response = self.ai.chat(user_message, system_prompt)
        else:
            response = self._get_fallback_response(user_message)
        
        # Track conversation
        if response:
            response_time = time.time() - start_time
            context = ConversationContext(
                user_message=user_message,
                ai_response=response,
                timestamp=start_time,
                mode=self.mode,
                response_time=response_time
            )
            self.conversation_history.append(context)
        
        return response
    
    def _is_exit_command(self, message: str) -> bool:
        """Check if message is an exit command."""
        exit_words = ["goodbye", "exit", "quit", "stop", "bye"]
        return any(word in message.lower() for word in exit_words)
    
    def _handle_control_commands(self, message: str) -> Optional[str]:
        """Handle system control commands."""
        message_lower = message.lower()
        
        if "reconnect" in message_lower or "restart ai" in message_lower:
            if self.ai.reconnect():
                return "AI connection restored, sir."
            else:
                return "Unable to reconnect to AI services, sir."
        
        elif "clear memory" in message_lower or "forget conversation" in message_lower:
            self.ai.clear_memory()
            self.conversation_history.clear()
            return "Conversation history cleared, sir."
        
        elif "status report" in message_lower:
            return self._get_status_report()
        
        elif "change personality" in message_lower:
            return "Personality changes are not yet implemented, sir."
        
        return None
    
    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when AI is unavailable."""
        message_lower = message.lower()
        
        if any(greeting in message_lower for greeting in ["hello", "hi", "jarvis"]):
            return FallbackResponses.get_response("greeting")
        
        elif any(status in message_lower for status in ["how are you", "status"]):
            return FallbackResponses.get_response("status")
        
        elif "time" in message_lower:
            current_time = time.strftime("%I:%M %p")
            return FallbackResponses.get_response("time", time=current_time)
        
        elif any(thanks in message_lower for thanks in ["thank", "thanks"]):
            return FallbackResponses.get_response("thanks")
        
        else:
            return FallbackResponses.get_response("unknown")
    
    def _get_status_report(self) -> str:
        """Generate a status report."""
        ai_status = "✅ Online" if self.ai.is_available() else "❌ Offline"
        audio_status = "✅ Ready"  # Audio is always ready if initialized
        
        report = f"""Status Report:
• AI System: {ai_status}
• Audio System: {audio_status}
• Personality: {self.config.personality}
• Conversations: {len(self.conversation_history)}
• Mode: {self.mode.value}"""
        
        return report
    
    def run_interactive(self):
        """Run Jarvis in interactive mode."""
        self.mode = OperationMode.INTERACTIVE
        self.running = True
        
        self.speak("Jarvis AI assistant activated. Press Enter to speak, or type 'quit' to exit.")
        
        try:
            while self.running:
                user_input = input("\n🎤 Press Enter to record (or 'quit'): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                # Listen for speech
                message = self.listen()
                if not message:
                    continue
                
                # Process and respond
                response = self.process_message(message)
                if response is None:  # Exit command
                    break
                
                self.speak(response)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        
        finally:
            self.running = False
            self.speak("Goodbye, sir!")
            self._cleanup()
    
    def run_continuous(self):
        """Run Jarvis in continuous listening mode."""
        self.mode = OperationMode.CONTINUOUS
        self.running = True
        
        self.speak("Jarvis activated for continuous operation. Say 'goodbye' to exit.")
        
        try:
            while self.running:
                print("\n" + "="*50)
                print("🤖 Jarvis is listening...")
                
                # Listen for speech
                message = self.listen()
                if not message:
                    time.sleep(1)  # Brief pause before next listen
                    continue
                
                # Process and respond
                response = self.process_message(message)
                if response is None:  # Exit command
                    break
                
                self.speak(response)
                time.sleep(1)  # Brief pause between interactions
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        
        finally:
            self.running = False
            self.speak("Goodbye, sir!")
            self._cleanup()
    
    def run_once(self) -> bool:
        """Process one interaction."""
        try:
            message = self.listen()
            if not message:
                return True  # Continue
            
            response = self.process_message(message)
            if response is None:  # Exit command
                return False  # Stop
            
            self.speak(response)
            return True  # Continue
            
        except Exception as e:
            logger.error(f"Error in single interaction: {e}")
            return True  # Continue despite error
    
    def _cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'audio'):
                self.audio.cleanup()
            logger.info("Jarvis agent cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        if not self.conversation_history:
            return {"total_conversations": 0}
        
        total_conversations = len(self.conversation_history)
        avg_response_time = sum(c.response_time for c in self.conversation_history) / total_conversations
        
        return {
            "total_conversations": total_conversations,
            "average_response_time": round(avg_response_time, 2),
            "ai_available": self.ai.is_available(),
            "current_mode": self.mode.value,
            "personality": self.config.personality
        }
