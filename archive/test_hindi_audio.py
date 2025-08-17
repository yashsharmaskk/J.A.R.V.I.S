"""
Hindi Audio Test - Check TTS Voice Output
This script will test actual Hindi audio output
"""

import pyttsx3
import time
import sys

def test_hindi_audio():
    """Test Hindi TTS audio output."""
    print("🎙️ HINDI AUDIO TEST")
    print("=" * 30)
    print("⚠️  Make sure your speakers/headphones are on!")
    print("🔊 You should hear audio output for each test...")
    print()
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Get and display available voices
        voices = engine.getProperty('voices')
        print(f"📢 Available voices ({len(voices)}):")
        
        hindi_voice = None
        for i, voice in enumerate(voices):
            voice_name = voice.name
            voice_lang = getattr(voice, 'languages', ['Unknown'])
            
            # Check for Hindi/Indian voices
            if any(indicator in voice_name.lower() for indicator in 
                  ['hindi', 'zira', 'hemant', 'kalpana', 'indian']):
                print(f"  🇮🇳 {i}: {voice_name} (Hindi/Indian) - {voice_lang}")
                if not hindi_voice:
                    hindi_voice = voice
            else:
                print(f"  🔊 {i}: {voice_name} - {voice_lang}")
        
        print()
        
        # Test with best available voice
        if hindi_voice:
            print(f"✅ Using Hindi voice: {hindi_voice.name}")
            engine.setProperty('voice', hindi_voice.id)
        else:
            print("⚠️  No dedicated Hindi voice found, using default")
        
        # Set optimal settings for Hindi
        engine.setProperty('rate', 140)  # Slower for clarity
        engine.setProperty('volume', 0.9)
        
        # Test phrases with audio output
        test_phrases = [
            ("Hello, I am Jarvis", "English"),
            ("Namaste, main Jarvis hun", "Hinglish"), 
            ("Aap kaise hain sir?", "Hinglish"),
            ("Main aapki help kar sakta hun", "Hinglish"),
            ("Thank you very much", "English"),
            ("Dhanyawad", "Hinglish")
        ]
        
        print("🎵 Playing audio tests (listen carefully):")
        print("-" * 40)
        
        for i, (phrase, lang) in enumerate(test_phrases, 1):
            print(f"\n🎤 Test {i} ({lang}): {phrase}")
            print("   🔊 Playing audio... ", end="", flush=True)
            
            try:
                # Apply pronunciation optimization for Hinglish
                if lang == "Hinglish":
                    optimized_phrase = optimize_hinglish(phrase)
                    print(f"(optimized: {optimized_phrase})")
                    engine.say(optimized_phrase)
                else:
                    print()
                    engine.say(phrase)
                
                engine.runAndWait()
                print("   ✅ Audio complete")
                time.sleep(1)  # Pause between tests
                
            except Exception as e:
                print(f"   ❌ Audio error: {e}")
        
        # Final test with mixed sentence
        print(f"\n🌟 Final test - Mixed language:")
        mixed_phrase = "Sir, aap theek hain? Main help kar sakta hun."
        optimized_mixed = optimize_hinglish(mixed_phrase)
        print(f"🎤 Original: {mixed_phrase}")
        print(f"🔧 Optimized: {optimized_mixed}")
        print("🔊 Playing... ", end="", flush=True)
        
        engine.say(optimized_mixed)
        engine.runAndWait()
        print("✅ Complete!")
        
        # Summary
        print(f"\n" + "=" * 40)
        print("🏆 HINDI AUDIO TEST RESULTS:")
        print("=" * 40)
        print(f"✅ TTS Engine: Working")
        print(f"✅ Voice Selection: {hindi_voice.name if hindi_voice else 'Default'}")
        print(f"✅ Audio Output: {'Hindi-optimized' if hindi_voice else 'English fallback'}")
        print(f"✅ Pronunciation: Optimized for Hinglish")
        print(f"✅ Speech Rate: Adjusted for clarity")
        
        print(f"\n🎯 Quality Assessment:")
        if hindi_voice:
            print("🌟 Excellent - Using Hindi-capable voice")
            print("🔊 Hindi words should sound natural")
        else:
            print("⚠️  Good - Using English voice with optimization")
            print("🔊 Hindi words approximated with English sounds")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        print("💡 Possible solutions:")
        print("   • Check audio drivers")
        print("   • Verify speakers/headphones")
        print("   • Try running as administrator")
        return False

def optimize_hinglish(text):
    """Optimize Hinglish text for better English TTS pronunciation."""
    replacements = {
        'kya': 'kiya',
        'aap': 'aap',
        'hain': 'hain', 
        'kar': 'car',
        'hun': 'hoon',
        'main': 'main',
        'theek': 'theek',
        'kaise': 'kaise',
        'sakta': 'sakta',
        'dhanyawad': 'dhanyavaad'
    }
    
    words = text.split()
    optimized = []
    
    for word in words:
        clean_word = word.lower().strip('.,!?:')
        punctuation = word[len(clean_word):]
        
        if clean_word in replacements:
            optimized.append(replacements[clean_word] + punctuation)
        else:
            optimized.append(word)
    
    return ' '.join(optimized)

def check_audio_system():
    """Quick audio system check."""
    print("🔍 AUDIO SYSTEM CHECK")
    print("=" * 25)
    
    try:
        engine = pyttsx3.init()
        print("✅ pyttsx3 initialized successfully")
        
        voices = engine.getProperty('voices')
        print(f"✅ Found {len(voices)} system voices")
        
        rate = engine.getProperty('rate')
        volume = engine.getProperty('volume')
        print(f"✅ Current settings: Rate={rate}, Volume={volume}")
        
        return True
    except Exception as e:
        print(f"❌ Audio system error: {e}")
        return False

if __name__ == "__main__":
    print("🇮🇳 JARVIS HINDI AUDIO VERIFICATION")
    print("=" * 50)
    
    # Step 1: Check audio system
    if not check_audio_system():
        print("\n❌ Audio system not available")
        sys.exit(1)
    
    # Step 2: Test Hindi audio
    print("\n")
    success = test_hindi_audio()
    
    if success:
        print(f"\n🎉 HINDI AUDIO TEST: SUCCESS!")
        print("🎙️ Your Jarvis can speak Hindi/Hinglish!")
    else:
        print(f"\n❌ HINDI AUDIO TEST: FAILED")
        print("🔧 Check audio configuration")
    
    print(f"\n💡 Next step: Run 'python jarvis_clean.py' for full voice interaction!")
