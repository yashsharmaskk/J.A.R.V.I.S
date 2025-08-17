"""
Simple Coqui TTS Test
"""

def test_coqui():
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS imported successfully!")
        
        # List available models
        print("📦 Listing available models...")
        models = TTS.list_models()
        
        # Find Hindi/multilingual models
        hindi_models = [m for m in models if 'multilingual' in m or 'hi' in m]
        print(f"🇮🇳 Found {len(hindi_models)} Hindi/multilingual models")
        
        for model in hindi_models[:3]:  # Show first 3
            print(f"   • {model}")
        
        # Test loading a simple model
        print("\n🧪 Testing model loading...")
        simple_models = [
            "tts_models/multilingual/multi-dataset/your_tts",
            "tts_models/en/ljspeech/tacotron2-DDC"
        ]
        
        for model in simple_models:
            try:
                print(f"📥 Loading {model}...")
                tts = TTS(model_name=model)
                print(f"✅ {model} loaded successfully!")
                return tts, model
            except Exception as e:
                print(f"⚠️  {model} failed: {e}")
                continue
        
        print("❌ No models could be loaded")
        return None, None
        
    except ImportError as e:
        print(f"❌ Coqui TTS not installed: {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    print("🧠 COQUI TTS INSTALLATION TEST")
    print("=" * 35)
    
    tts, model = test_coqui()
    
    if tts:
        print(f"\n🎉 SUCCESS! Coqui TTS is ready!")
        print(f"📦 Loaded model: {model}")
        print(f"🇮🇳 Ready for premium Hindi voice synthesis!")
    else:
        print(f"\n❌ FAILED! Coqui TTS installation issues")
        print(f"💡 Try: pip install --upgrade TTS")
