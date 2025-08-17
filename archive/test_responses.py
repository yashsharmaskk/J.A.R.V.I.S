"""
Test Jarvis multilingual responses
"""
from jarvis_clean import JarvisAssistant, JarvisConfig

def test_responses():
    print("🤖 Jarvis Multilingual Test")
    print("=" * 30)
    
    # Create Jarvis
    config = JarvisConfig(personality="iron_man_jarvis")
    jarvis = JarvisAssistant(config)
    
    # Test different languages
    tests = [
        ("Hello Jarvis", "English"),
        ("नमस्ते जार्विस", "Hindi"),  
        ("Aap kaise hain?", "Hinglish"),
        ("Smart mode on karo", "Hinglish Command"),
        ("Status kya hai?", "Hinglish Status")
    ]
    
    for message, lang in tests:
        print(f"\n📝 {lang}: {message}")
        response = jarvis.process_message(message)
        print(f"🤖 Response: {response}")
    
    print("\n✅ All multilingual tests complete!")

if __name__ == "__main__":
    test_responses()
