import os
import tempfile
import wave
import threading
import time
import subprocess
from pathlib import Path

try:
    import pyttsx3
except ImportError:
    print("pyttsx3 not found. Installing...")
    subprocess.check_call(["pip", "install", "pyttsx3"])
    import pyttsx3

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    print("sounddevice and numpy not found. Installing...")
    subprocess.check_call(["pip", "install", "sounddevice", "numpy"])
    import sounddevice as sd
    import numpy as np

try:
    import whisper
except ImportError:
    print("whisper not found. Installing...")
    subprocess.check_call(["pip", "install", "openai-whisper"])
    import whisper


class SimpleVoiceAssistant:
    """
    A simplified voice assistant that uses sounddevice instead of pyaudio
    for better Windows compatibility.
    """
    
    def __init__(self, model_size="tiny"):
        """
        Initialize the voice assistant.
        
        Args:
            model_size (str): Size of the Whisper model to load
        """
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Load Whisper model
        print(f"Loading Whisper model ({model_size})...")
        self.whisper_model = whisper.load_model(model_size)
        print("Whisper model loaded successfully!")
        
        # Audio settings
        self.sample_rate = 16000
        self.duration = 5  # seconds to record
        self.listening = False
        
        print("Voice Assistant ready!")
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to be spoken
        """
        print(f"Jarvis: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def record_audio(self):
        """
        Record audio from the microphone.
        
        Returns:
            numpy.ndarray: Audio data
        """
        print("🎤 Listening... (speak now)")
        audio = sd.rec(int(self.duration * self.sample_rate), 
                      samplerate=self.sample_rate, 
                      channels=1, 
                      dtype='float32')
        sd.wait()  # Wait until recording is finished
        print("🔇 Recording finished")
        return audio.flatten()
    
    def transcribe_audio(self, audio_data):
        """
        Transcribe audio using Whisper.
        
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
                print(f"You said: {text}")
                return text
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            
        return ""
    
    def process_command(self, text):
        """
        Process the recognized text and respond accordingly.
        
        Args:
            text (str): The recognized text
            
        Returns:
            bool: True to continue listening, False to stop
        """
        text_lower = text.lower().strip()
        
        if "hello jarvis" in text_lower:
            self.speak("Hello sir, how can I help you?")
        elif "goodbye" in text_lower or "exit" in text_lower or "quit" in text_lower:
            self.speak("Goodbye sir!")
            return False
        elif "how are you" in text_lower:
            self.speak("I'm doing well, thank you for asking!")
        elif "what time is it" in text_lower:
            current_time = time.strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
        elif "thank you" in text_lower:
            self.speak("You're welcome!")
        elif text_lower:  # If there's text but no specific command
            self.speak("I heard you, but I'm not sure how to help with that yet.")
        
        return True
    
    def listen_once(self):
        """
        Listen for one command and process it.
        
        Returns:
            bool: True to continue, False to stop
        """
        try:
            # Record audio
            audio_data = self.record_audio()
            
            # Transcribe the audio
            text = self.transcribe_audio(audio_data)
            
            if text:
                # Process the command
                return self.process_command(text)
            else:
                print("No speech detected, try speaking louder or closer to the microphone.")
                
        except Exception as e:
            print(f"Error during listening: {e}")
            
        return True
    
    def start_interactive_mode(self):
        """
        Start interactive mode where user presses Enter to record.
        """
        self.speak("Voice assistant activated. Press Enter to speak, or type 'quit' to exit.")
        
        while True:
            try:
                user_input = input("\n🎤 Press Enter to start recording (or 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.speak("Goodbye!")
                    break
                
                # Listen for one command
                continue_listening = self.listen_once()
                if not continue_listening:
                    break
                    
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def start_continuous_mode(self):
        """
        Start continuous listening mode.
        """
        self.listening = True
        self.speak("Voice assistant activated. Say 'Hello Jarvis' to begin. Say 'goodbye' to stop.")
        
        while self.listening:
            try:
                print("\n" + "="*50)
                print("🎤 Ready to listen...")
                
                # Listen for one command
                continue_listening = self.listen_once()
                if not continue_listening:
                    self.listening = False
                    break
                
                # Small delay between recordings
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nShutting down...")
                self.listening = False
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)


def main():
    """
    Main function to run the voice assistant.
    """
    print("=" * 60)
    print("🎤 JARVIS Simple Voice Assistant")
    print("=" * 60)
    print()
    
    try:
        # Create the voice assistant
        assistant = SimpleVoiceAssistant(model_size="tiny")
        
        print("\nChoose mode:")
        print("1. Interactive mode (press Enter to record)")
        print("2. Continuous mode (always listening)")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            assistant.start_interactive_mode()
        else:
            assistant.start_continuous_mode()
            
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("- Make sure you have a microphone connected")
        print("- Check that your microphone permissions are enabled")
        print("- Try running: pip install sounddevice numpy openai-whisper pyttsx3")


if __name__ == "__main__":
    main()
