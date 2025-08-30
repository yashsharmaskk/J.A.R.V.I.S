#!/usr/bin/env python3
"""
JARVIS Streaming Whisper Integration
Real-time speech recognition using OpenAI Whisper
"""

import os
import sys
import asyncio
import json
import logging
import wave
import tempfile
import threading
import time
from pathlib import Path
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import whisper
    import pyaudio
    WHISPER_AVAILABLE = True
    logger.info("✅ Whisper and PyAudio available")
except ImportError as e:
    WHISPER_AVAILABLE = False
    logger.error(f"❌ Whisper/PyAudio not available: {e}")

class StreamingWhisperRecognizer:
    def __init__(self, model_name="small"):
        # Initialize model and audio attributes
        self.model_name = model_name
        self.model = None
        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_buffer = []
        self._recording_thread = None
        # Temporary directory for audio processing
        self.temp_dir = Path(tempfile.gettempdir()) / "jarvis_whisper"
        self.temp_dir.mkdir(exist_ok=True)

        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Whisper prefers 16kHz
        self.RECORD_SECONDS = 3  # Seconds to record before processing

        # Load Whisper model and initialize audio
        self._load_model()
        self._init_audio()
    
    def _load_model(self):
        """Load Whisper model with aggressive GPU utilization"""
        try:
            logger.info(f"🔥 Loading Whisper {self.model_name} model...")
            
            # Check GPU availability and force GPU usage if possible
            try:
                import torch
                cuda_available = torch.cuda.is_available()
                if cuda_available:
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory
                    gpu_memory_allocated = torch.cuda.memory_allocated(0)
                    gpu_memory_free = gpu_memory - gpu_memory_allocated
                    
                    logger.info(f"🎮 GPU: {gpu_name}")
                    logger.info(f"📊 GPU Memory: {gpu_memory_free/1e9:.1f}GB free of {gpu_memory/1e9:.1f}GB total")
                    
                    # Force GPU usage for better performance
                    logger.info(f"🚀 Loading {self.model_name} model on GPU for maximum performance...")
                    self.model = whisper.load_model(self.model_name, device="cuda")
                    logger.info(f"✅ Whisper {self.model_name} model loaded on GPU successfully!")
                    
                    # Log final GPU memory usage
                    final_memory = torch.cuda.memory_allocated(0)
                    whisper_memory = final_memory - gpu_memory_allocated
                    logger.info(f"📊 Whisper using {whisper_memory/1e6:.0f}MB GPU memory")
                    return
                    
                else:
                    logger.warning("⚠️ CUDA not available for Whisper, using CPU...")
            except Exception as torch_e:
                logger.warning(f"⚠️ GPU check failed: {torch_e}, falling back to CPU...")
            
            # Fallback to CPU
            logger.info(f"💻 Loading {self.model_name} model on CPU...")
            self.model = whisper.load_model(self.model_name, device="cpu")
            logger.info(f"✅ Whisper {self.model_name} model loaded on CPU successfully!")
                
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model '{self.model_name}': {e}")
            # Don't try fallback here - let the caller handle it
            self.model = None
            raise e
    
    def _init_audio(self):
        """Initialize PyAudio"""
        try:
            logger.info("🔄 Initializing audio system...")
            self.audio = pyaudio.PyAudio()
            # Select default input device
            try:
                default_info = self.audio.get_default_input_device_info()
                self.input_device_index = default_info.get('index')
                logger.info(f"ℹ️ Default input device index: {self.input_device_index} - {default_info.get('name')}")
            except Exception:
                self.input_device_index = None
                logger.warning("⚠️ Could not get default input device, using system default")
            # Test if we can access microphone
            stream_args = dict(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            if self.input_device_index is not None:
                stream_args['input_device_index'] = self.input_device_index
            test_stream = self.audio.open(**stream_args)
            test_stream.close()
            
            logger.info("✅ Audio system initialized and microphone accessible")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize audio: {e}")
            logger.error("❌ Make sure your microphone is connected and accessible")
            self.audio = None
    
    def start_recording(self):
        """Start recording audio stream"""
        if not self.audio or not self.model:
            logger.error("❌ Audio or Whisper model not available")
            return False
        
        try:
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            self.is_recording = True
            self.audio_buffer = []
            # Start background thread to read audio chunks
            self._recording_thread = threading.Thread(target=self._record_loop, daemon=True)
            self._recording_thread.start()
            logger.info("🎤 Started recording...")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording and process audio"""
        if not self.is_recording:
            return ""
        
        # Stop background recording thread
        self.is_recording = False
        if self._recording_thread:
            self._recording_thread.join(timeout=0.1)
        
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            
            # Ensure at least one chunk is recorded
            if not self.audio_buffer:
                try:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    self.audio_buffer.append(data)
                    logger.info("ℹ️ Captured one chunk on fallback read")
                except Exception as e:
                    logger.warning(f"⚠️ Fallback read failed: {e}")
            if not self.audio_buffer:
                logger.warning("⚠️ No audio data recorded after fallback")
                return ""
            logger.info(f"ℹ️ Recorded {len(self.audio_buffer)} audio chunks")
            
            # Convert audio data to numpy array
            audio_data = np.frombuffer(b''.join(self.audio_buffer), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
            
            # Process with Whisper
            logger.info("🔄 Processing audio with Whisper...")
            result = self.model.transcribe(audio_data, language="en", fp16=False)
            
            text = result["text"].strip()
            logger.info(f"🎯 Transcribed: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Error processing audio: {e}")
            return ""
    
    def record_chunk(self):
        """Record a chunk of audio data"""
        if not self.stream or not self.is_recording:
            return
        
        try:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.audio_buffer.append(data)
        except Exception as e:
            logger.error(f"❌ Error reading audio chunk: {e}")
    
    def _record_loop(self):
        """Background loop to continuously record audio chunks"""
        # Continuously read audio chunks while recording
        interval = self.CHUNK / float(self.RATE)
        while self.is_recording:
            try:
                self.record_chunk()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"❌ Error in recording loop: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass

# Global Whisper instance
whisper_recognizer = None

def initialize_whisper(model_name="base"):
    """Initialize Whisper recognizer"""
    global whisper_recognizer
    
    if not WHISPER_AVAILABLE:
        logger.error("❌ Whisper not available - install with: pip install openai-whisper pyaudio")
        return False
    
    try:
        logger.info(f"🔄 Initializing Whisper {model_name} model...")
        whisper_recognizer = StreamingWhisperRecognizer(model_name)
        
        if whisper_recognizer.model is None:
            logger.error("❌ Whisper model failed to load")
            return False
            
        if whisper_recognizer.audio is None:
            logger.error("❌ Audio system failed to initialize - check microphone permissions")
            return False
            
        logger.info(f"✅ Whisper {model_name} model loaded and ready")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Whisper: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

def start_whisper_recording():
    """Start Whisper recording"""
    global whisper_recognizer
    
    if not whisper_recognizer:
        return False
    
    return whisper_recognizer.start_recording()

def stop_whisper_recording():
    """Stop Whisper recording and get transcription"""
    global whisper_recognizer
    
    if not whisper_recognizer:
        return ""
    
    return whisper_recognizer.stop_recording()

def record_whisper_chunk():
    """Record a chunk for continuous listening"""
    global whisper_recognizer
    
    if whisper_recognizer and whisper_recognizer.is_recording:
        whisper_recognizer.record_chunk()

if __name__ == "__main__":
    # Test Whisper integration
    print("🤖 Testing Whisper Integration")
    print("=" * 40)
    
    if initialize_whisper("base"):
        print("✅ Whisper initialized successfully")
        print("🎤 Recording for 5 seconds...")
        
        start_whisper_recording()
        
        # Record for 5 seconds
        for i in range(5 * 16):  # 16 chunks per second
            record_whisper_chunk()
            time.sleep(1/16)
        
        text = stop_whisper_recording()
        print(f"🎯 Result: {text}")
        
        whisper_recognizer.cleanup()
    else:
        print("❌ Whisper initialization failed")
