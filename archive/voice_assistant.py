import speech_recognition as sr
import pyttsx3
import whisper
import threading
import queue
import time
import numpy as np


class VoiceAssistant:
    """
    A simple voice assistant that listens for speech, converts it to text using Whisper,
    and responds with text-to-speech. Responds to 'Hello Jarvis' with a greeting.
    """
    
    def __init__(self, model_size="tiny"):
        """
        Initialize the voice assistant.
        
        Args:
            model_size (str): Size of the Whisper model to load ('tiny', 'base', 'small', etc.)
        """
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)  # Adjust speech rate
        self.tts_engine.setProperty('volume', 0.9)  # Adjust volume
        
        # Load Whisper model
        print(f"Loading Whisper model ({model_size})...")
        self.whisper_model = whisper.load_model(model_size)
        print("Whisper model loaded successfully!")
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.listening = False
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Ready to listen!")
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to be spoken
        """
        print(f"Jarvis: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def process_audio_with_whisper(self, audio_data):
        """
        Process audio data using Whisper for speech recognition.
        
        Args:
            audio_data: Audio data from speech_recognition
            
        Returns:
            str: Transcribed text or None if recognition failed
        """
        try:
            # Convert audio data to numpy array
            audio_np = np.frombuffer(audio_data.get_wav_data(), dtype=np.int16).astype(np.float32) / 32768.0
            
            # Use Whisper to transcribe
            result = self.whisper_model.transcribe(audio_np, fp16=False)
            text = result['text'].strip()
            
            if text:
                print(f"You said: {text}")
                return text
            
        except Exception as e:
            print(f"Error processing audio with Whisper: {e}")
            
        return None
    
    def process_command(self, text):
        """
        Process the recognized text and respond accordingly.
        
        Args:
            text (str): The recognized text
        """
        text_lower = text.lower().strip()
        
        if "hello jarvis" in text_lower:
            self.speak("Hello sir, how can I help you?")
        elif "goodbye" in text_lower or "exit" in text_lower or "quit" in text_lower:
            self.speak("Goodbye sir!")
            return False  # Signal to stop listening
        elif "how are you" in text_lower:
            self.speak("I'm doing well, thank you for asking!")
        elif "what time is it" in text_lower:
            current_time = time.strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
        else:
            # Default response for unrecognized commands
            self.speak("I heard you, but I'm not sure how to help with that yet.")
        
        return True  # Continue listening
    
    def listen_continuously(self):
        """
        Continuously listen for audio and process it.
        """
        print("Listening for commands... Say 'Hello Jarvis' to get started!")
        
        while self.listening:
            try:
                # Listen for audio with timeout
                with self.microphone as source:
                    # Listen for audio with a shorter timeout and phrase time limit
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Process the audio in a separate thread to avoid blocking
                threading.Thread(target=self._process_audio_thread, args=(audio,)).start()
                
            except sr.WaitTimeoutError:
                # Timeout is normal, continue listening
                pass
            except Exception as e:
                print(f"Error during listening: {e}")
                time.sleep(0.1)
    
    def _process_audio_thread(self, audio):
        """
        Process audio in a separate thread.
        
        Args:
            audio: Audio data to process
        """
        # Use Whisper for more accurate transcription
        text = self.process_audio_with_whisper(audio)
        
        if text:
            # Process the command
            continue_listening = self.process_command(text)
            if not continue_listening:
                self.stop_listening()
    
    def start_listening(self):
        """
        Start the voice assistant and begin listening for commands.
        """
        self.listening = True
        self.speak("Voice assistant activated. Say 'Hello Jarvis' to begin.")
        
        # Start listening in a separate thread
        listen_thread = threading.Thread(target=self.listen_continuously)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Keep the main thread alive
        try:
            while self.listening:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop_listening()
    
    def stop_listening(self):
        """
        Stop the voice assistant.
        """
        self.listening = False
        print("Voice assistant stopped.")


def main():
    """
    Main function to run the voice assistant.
    """
    try:
        # Create and start the voice assistant
        assistant = VoiceAssistant(model_size="tiny")  # Use "base" or "small" for better accuracy
        assistant.start_listening()
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have a microphone connected and the required packages installed.")


if __name__ == "__main__":
    main()
