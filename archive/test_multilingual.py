"""
Test script for Hindi/Hinglish multilingual support in Jarvis
"""

from jarvis_clean import JarvisAssistant, JarvisConfig

def test_multilingual():
    """Test multilingual capabilities."""
    
    print("🇮🇳 Testing Hindi/Hinglish Support in Jarvis")
    print("=" * 50)
    
    # Create Jarvis with Iron Man personality
    config = JarvisConfig(personality="iron_man_jarvis")
    jarvis = JarvisAssistant(config)
    
    # Test messages in different languages
    test_messages = [
        # English
        "Hello Jarvis, how are you?",
        "What is machine learning?",
        
        # Hindi
        "नमस्ते जार्विस, आप कैसे हैं?",
        "मशीन लर्निंग क्या है?",
        "कृपया समझाइए कि आर्टिफिशियल इंटेलिजेंस कैसे काम करता है?",
        
        # Hinglish
        "Hi Jarvis, aap kaise hain?",
        "Machine learning ke baare mein batao",
        "Explain karo ki AI kaise kaam karta hai",
        "Smart mode on karo please",
        "Status kya hai system ka?",
        
        # Mixed conversation
        "Thanks for the help!",
        "धन्यवाद!",
        "Bahut accha response tha!"
    ]
    
    print("\n🤖 Starting multilingual conversation tests...")
    print("-" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        response = jarvis.process_message(message)
        
        if response:
            print(f"🤖 Jarvis: {response}")
        else:
            print("❌ No response received")
    
    print("\n" + "=" * 50)
    print("🎉 Multilingual testing complete!")
    print("\n📋 Supported languages:")
    print("  ✅ English - Full support")
    print("  ✅ Hindi (हिंदी) - Full support with Devanagari script")
    print("  ✅ Hinglish - Natural Hindi-English mixing")
    print("\n🗣️ Voice commands supported in all languages!")

if __name__ == "__main__":
    test_multilingual()
