"""
Core audio processing module using modern architecture.
"""

import sounddevice as sd
import numpy as np
import whisper
import pyttsx3
import threading
import queue
from typing import Optional, Callable, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AudioData:
    """Container for audio data and metadata."""
    data: np.ndarray
    sample_rate: int
    duration: float
    timestamp: float


class AudioProcessor:
    """Handles audio input/output processing."""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._recording = False
        self._audio_queue = queue.Queue()
        
    def record_audio(self, duration: float = 5.0) -> Optional[AudioData]:
        """Record audio from microphone."""
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            )
            sd.wait()  # Wait for recording to complete
            
            return AudioData(
                data=audio.flatten(),
                sample_rate=self.sample_rate,
                duration=duration,
                timestamp=np.datetime64('now').astype(float)
            )
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    def start_continuous_recording(self, callback: Callable[[AudioData], None]):
        """Start continuous audio recording with callback."""
        # Implementation for continuous recording would go here
        pass


class SpeechRecognizer:
    """Speech-to-text using Whisper."""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(self, audio_data: AudioData) -> Optional[str]:
        """Transcribe audio data to text."""
        try:
            if self._model is None:
                raise RuntimeError("Whisper model not loaded")
            
            result = self._model.transcribe(audio_data.data, fp16=False)
            text = result['text'].strip()
            
            if text:
                logger.info(f"Transcribed: '{text}'")
                return text
            else:
                logger.warning("No speech detected in audio")
                return None
                
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None


class TextToSpeech:
    """Text-to-speech synthesis."""
    
    def __init__(self, rate: int = 180, volume: float = 0.9):
        self.rate = rate
        self.volume = volume
        self._engine = None
        self._speaking_lock = threading.Lock()
        self._init_engine()
    
    def _init_engine(self):
        """Initialize TTS engine."""
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', self.rate)
            self._engine.setProperty('volume', self.volume)
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Convert text to speech."""
        try:
            if not text or not text.strip():
                return False
            
            logger.info(f"Speaking: '{text}'")
            
            with self._speaking_lock:
                self._engine.say(text)
                if blocking:
                    self._engine.runAndWait()
                else:
                    # For non-blocking, would need threading
                    threading.Thread(
                        target=self._engine.runAndWait, 
                        daemon=True
                    ).start()
            
            return True
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def stop(self):
        """Stop current speech."""
        try:
            if self._engine:
                self._engine.stop()
        except Exception as e:
            logger.error(f"Error stopping TTS: {e}")


class AudioManager:
    """High-level audio management coordinating all audio components."""
    
    def __init__(self, config: dict):
        self.processor = AudioProcessor(
            sample_rate=config.get('sample_rate', 16000),
            channels=config.get('channels', 1)
        )
        
        self.recognizer = SpeechRecognizer(
            model_size=config.get('whisper_model', 'base')
        )
        
        self.tts = TextToSpeech(
            rate=config.get('tts_rate', 180),
            volume=config.get('tts_volume', 0.9)
        )
        
        logger.info("Audio manager initialized")
    
    def listen_and_transcribe(self, duration: float = 5.0) -> Optional[str]:
        """Record audio and transcribe to text."""
        audio_data = self.processor.record_audio(duration)
        if audio_data:
            return self.recognizer.transcribe(audio_data)
        return None
    
    def speak_text(self, text: str, blocking: bool = True) -> bool:
        """Convert text to speech."""
        return self.tts.speak(text, blocking)
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            self.tts.stop()
            logger.info("Audio manager cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
