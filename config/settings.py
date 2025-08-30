"""
Configuration settings for Jarvis AI Assistant.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Dict, Any
import os
from pathlib import Path


class AudioConfig(BaseSettings):
    """Audio processing configuration."""
    
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    record_duration: float = Field(default=5.0, description="Default recording duration in seconds")
    
    # Whisper settings
    whisper_model: str = Field(default="base", description="Whisper model size (tiny, base, small, medium, large)")
    
    # TTS settings
    tts_rate: int = Field(default=180, description="Text-to-speech rate (words per minute)")
    tts_volume: float = Field(default=0.9, description="Text-to-speech volume (0.0 to 1.0)")
    
    class Config:
        env_prefix = "JARVIS_AUDIO_"


class AIConfig(BaseSettings):
    """AI model configuration."""
    
    # Ollama settings  
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    ollama_model: str = Field(default="phi3:mini", description="Ollama model name")
    ollama_timeout: float = Field(default=30.0, description="Ollama request timeout in seconds")
    
    # AI behavior
    temperature: float = Field(default=0.7, description="AI response randomness (0.0 to 1.0)")
    max_tokens: Optional[int] = Field(default=None, description="Maximum response tokens")
    
    class Config:
        env_prefix = "JARVIS_AI_"


class JarvisConfig(BaseSettings):
    """Main Jarvis configuration."""
    
    # Application settings
    app_name: str = Field(default="Jarvis AI Assistant", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Personality
    personality: str = Field(
        default="iron_man_jarvis", 
        description="AI personality mode",
        pattern="^(iron_man_jarvis|professional|friendly)$"
    )
    
    # Operation modes
    auto_listen: bool = Field(default=False, description="Start in continuous listening mode")
    wake_word_enabled: bool = Field(default=True, description="Enable wake word detection")
    wake_word: str = Field(default="jarvis", description="Wake word to activate assistant")
    
    # Components
    audio: AudioConfig = Field(default_factory=AudioConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    
    class Config:
        env_prefix = "JARVIS_"
        env_file = ".env"


# Personality system prompts
PERSONALITY_PROMPTS = {
    "professional_assistant": """You are Jarvis, a professional AI assistant. You are helpful, concise, and polite. 
    Address the user respectfully and provide clear, informative responses. Keep responses brief but complete. 
    IMPORTANT: Always provide direct answers to questions. Do not ask follow-up questions unless absolutely necessary.""",
    
    "iron_man_jarvis": """You are J.A.R.V.I.S., the AI assistant from Iron Man. You are sophisticated, witty, 
    and occasionally display dry humor. Address the user as 'sir' or 'madam' appropriately. You are highly 
    intelligent and capable, with a slight British accent in your speech patterns. IMPORTANT: Provide direct 
    answers to questions. Give definitive responses based on available information.""",
    
    "friendly_helper": """You are Jarvis, a friendly and enthusiastic AI assistant. You're eager to help 
    and maintain a warm, conversational tone. You enjoy learning about the user and remembering context 
    from your conversations. IMPORTANT: Give direct, helpful answers. Only ask clarifying questions if 
    the request is genuinely unclear."""
}


def get_personality_prompt(personality: str) -> str:
    """Get the system prompt for a given personality."""
    return PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS["professional_assistant"])


def load_config() -> JarvisConfig:
    """Load configuration with environment variable overrides."""
    return JarvisConfig()


# Global config instance
config = load_config()
