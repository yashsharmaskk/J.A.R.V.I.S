"""
LangChain-based AI integration for Jarvis.
"""

import logging
from typing import Optional, Dict, Any, List
from langchain_ollama import OllamaLLM
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.callbacks.base import BaseCallbackHandler
import requests
import time

logger = logging.getLogger(__name__)


class JarvisCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for Jarvis AI interactions."""
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        logger.info("🤔 Jarvis is thinking...")
    
    def on_llm_end(self, response, **kwargs) -> None:
        logger.info("✅ Jarvis response generated")
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        logger.error(f"❌ AI error: {error}")


class OllamaHealthCheck:
    """Health monitoring for Ollama service."""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 5.0):
        self.base_url = base_url
        self.timeout = timeout
        self.last_check = 0
        self.check_interval = 30  # seconds
        self._is_healthy = False
    
    def is_healthy(self, force_check: bool = False) -> bool:
        """Check if Ollama service is healthy."""
        current_time = time.time()
        
        if not force_check and (current_time - self.last_check) < self.check_interval:
            return self._is_healthy
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            self._is_healthy = response.status_code == 200
            self.last_check = current_time
            
            if self._is_healthy:
                logger.debug("✅ Ollama service is healthy")
            else:
                logger.warning(f"⚠️ Ollama returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self._is_healthy = False
            self.last_check = current_time
            logger.warning(f"❌ Ollama health check failed: {e}")
        
        return self._is_healthy
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            if not self.is_healthy():
                return []
            
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
        
        return []


class JarvisAI:
    """LangChain-based AI agent for Jarvis."""
    
    def __init__(self, config: dict):
        self.config = config
        self.ollama_url = config.get('ollama_base_url', 'http://localhost:11434')
        self.model_name = config.get('ollama_model', 'phi3:mini')
        self.temperature = config.get('temperature', 0.7)
        self.timeout = config.get('ollama_timeout', 30.0)
        
        # Health monitoring
        self.health_check = OllamaHealthCheck(self.ollama_url, self.timeout)
        
        # LangChain components
        self._llm = None
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Remember last 10 exchanges
            return_messages=True
        )
        
        self.callback_handler = JarvisCallbackHandler()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LangChain Ollama LLM."""
        try:
            if not self.health_check.is_healthy():
                logger.warning("Ollama not available - AI features disabled")
                return
            
            self._llm = OllamaLLM(
                base_url=self.ollama_url,
                model=self.model_name,
                temperature=self.temperature,
                callbacks=[self.callback_handler],
                timeout=self.timeout
            )
            
            # Test the connection
            test_response = self._llm.invoke("Hello")
            if test_response:
                logger.info(f"✅ Connected to {self.model_name} via Ollama")
            else:
                logger.error("❌ Failed to get test response from LLM")
                self._llm = None
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            self._llm = None
    
    def is_available(self) -> bool:
        """Check if AI is available."""
        return self._llm is not None and self.health_check.is_healthy()
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Send a chat message and get AI response."""
        try:
            if not self.is_available():
                logger.warning("AI not available - attempting reconnection")
                self._initialize_llm()
                if not self.is_available():
                    return None
            
            # Build the full prompt
            conversation_history = self.memory.chat_memory.messages
            
            # Construct messages for context
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history
            for msg in conversation_history:
                messages.append(msg)
            
            # Add current user message
            user_message = HumanMessage(content=message)
            messages.append(user_message)
            
            # Create prompt string from messages
            prompt_parts = []
            if system_prompt:
                prompt_parts.append(f"System: {system_prompt}")
            
            for msg in conversation_history:
                if isinstance(msg, HumanMessage):
                    prompt_parts.append(f"Human: {msg.content}")
                elif isinstance(msg, AIMessage):
                    prompt_parts.append(f"Assistant: {msg.content}")
            
            prompt_parts.append(f"Human: {message}")
            prompt_parts.append("Assistant:")
            
            full_prompt = "\n".join(prompt_parts)
            
            # Get AI response
            response = self._llm.invoke(full_prompt)
            
            if response:
                # Store in memory
                self.memory.chat_memory.add_user_message(message)
                self.memory.chat_memory.add_ai_message(response)
                
                logger.info(f"AI Response: {response[:100]}...")
                return response.strip()
            else:
                logger.warning("Empty response from AI")
                return None
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            # Try to reconnect on error
            self._llm = None
            return None
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No conversation history"
        
        return f"Conversation with {len(messages)} messages"
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to Ollama."""
        logger.info("🔄 Attempting to reconnect to Ollama...")
        self.health_check._is_healthy = False  # Force health check
        self._initialize_llm()
        return self.is_available()


class FallbackResponses:
    """Fallback responses when AI is not available."""
    
    RESPONSES = {
        "greeting": [
            "Hello sir, how can I help you?",
            "Good day! I'm here to assist you.",
            "Hello! How may I be of service?"
        ],
        
        "status": [
            "I'm functioning optimally, thank you for asking!",
            "All systems operational, sir.",
            "I'm doing well, ready to assist you."
        ],
        
        "time": "The current time is {time}, sir.",
        
        "thanks": [
            "You're welcome, sir!",
            "Happy to help!",
            "My pleasure to assist you."
        ],
        
        "unknown": [
            "I understand, sir. How else may I assist you?",
            "I'm here to help with whatever you need.",
            "How may I be of further assistance?"
        ],
        
        "ai_unavailable": [
            "My AI capabilities are currently offline, but I'm still here to help with basic functions.",
            "I'm operating in basic mode at the moment, sir.",
            "My advanced AI features are temporarily unavailable."
        ]
    }
    
    @classmethod
    def get_response(cls, category: str, **kwargs) -> str:
        """Get a fallback response."""
        responses = cls.RESPONSES.get(category, cls.RESPONSES["unknown"])
        
        if isinstance(responses, list):
            import random
            response = random.choice(responses)
        else:
            response = responses
        
        # Format with any provided kwargs
        try:
            return response.format(**kwargs)
        except (KeyError, ValueError):
            return response
