"""
JARVIS Voice Assistant - Main Implementation

A Python class that can:
1. Listen for speech using a microphone
2. Convert speech to text using OpenAI's Whisper
3. Respond with text-to-speech
4. Specifically responds to "Hello Jarvis" with "Hello sir, how can I help you?"

Requirements:
- pyttsx3 (text-to-speech)
- openai-whisper (speech recognition)
- sounddevice (microphone input)
- numpy (audio processing)
"""

import subprocess
import sys
import time
import threading

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

import pyttsx3
import whisper
import sounddevice as sd
import numpy as np


class JarvisVoiceAssistant:
    """
    A voice assistant that listens for speech, converts it to text using Whisper,
    and responds with text-to-speech. Responds to "Hello Jarvis" with a greeting.
    """
    
    def __init__(self, model_size="tiny"):
        """
        Initialize the voice assistant.
        
        Args:
            model_size (str): Whisper model size ('tiny', 'base', 'small', etc.)
        """
        print("🚀 Initializing Jarvis Voice Assistant...")
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level
        
        # Load Whisper model
        print(f"📥 Loading Whisper model ({model_size})...")
        self.whisper_model = whisper.load_model(model_size)
        
        # Audio settings
        self.sample_rate = 16000  # Sample rate for recording
        self.record_duration = 4  # Seconds to record
        self.listening = False
        
        print("✅ Jarvis is ready!")
    
    def speak(self, text):
        """
        Convert text to speech and speak it.
        
        Args:
            text (str): Text to speak
        """
        print(f"🗣️  Jarvis: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """
        Record audio from microphone.
        
        Returns:
            numpy.ndarray: Audio data
        """
        print("🎤 Listening... (speak now)")
        
        # Record audio
        audio = sd.rec(
            int(self.record_duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait for recording to complete
        
        print("🔇 Recording complete")
        return audio.flatten()
    
    def speech_to_text(self, audio_data):
        """
        Convert audio to text using Whisper.
        
        Args:
            audio_data (numpy.ndarray): Audio data
            
        Returns:
            str: Transcribed text
        """
        try:
            # Use Whisper to transcribe
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
    
    def process_command(self, text):
        """
        Process voice command and generate response.
        
        Args:
            text (str): The transcribed text
            
        Returns:
            bool: True to continue listening, False to stop
        """
        text_lower = text.lower().strip()
        
        if "hello jarvis" in text_lower:
            self.speak("Hello sir, how can I help you?")
            
        elif "goodbye" in text_lower or "exit" in text_lower or "stop" in text_lower:
            self.speak("Goodbye sir!")
            return False
            
        elif "how are you" in text_lower:
            self.speak("I'm doing well, thank you for asking!")
            
        elif "what time is it" in text_lower or "time" in text_lower:
            current_time = time.strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            
        elif "thank you" in text_lower or "thanks" in text_lower:
            self.speak("You're welcome!")
            
        elif text.strip():  # If there's text but no recognized command
            self.speak("I heard you, but I'm not sure how to help with that.")
        
        return True
    
    def run_once(self):
        """
        Listen for one command and respond.
        
        Returns:
            bool: True to continue, False to stop
        """
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
        """
        Run in interactive mode - press Enter to record.
        """
        self.speak("Voice assistant activated. Press Enter to speak, or type quit to exit.")
        
        while True:
            try:
                user_input = input("\n🎤 Press Enter to record (or 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.speak("Goodbye!")
                    break
                
                # Listen and respond
                continue_listening = self.run_once()
                if not continue_listening:
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                self.speak("Goodbye!")
                break
    
    def run_continuous(self):
        """
        Run in continuous mode - automatically listens.
        """
        self.listening = True
        self.speak("Voice assistant activated. Say Hello Jarvis to begin.")
        
        while self.listening:
            try:
                print("\n" + "="*40)
                
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
                self.speak("Goodbye!")
                break


def main():
    """Main function to run Jarvis."""
    print("🎤 JARVIS Voice Assistant")
    print("=" * 40)
    
    try:
        # Create Jarvis instance
        jarvis = JarvisVoiceAssistant(model_size="tiny")
        
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
        print("- Microphone permissions enabled")
        print("- All required packages installed")


if __name__ == "__main__":
    main()
