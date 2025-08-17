"""
Test the new LangChain-based Jarvis architecture.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test if all components can be imported."""
    try:
        from config.settings import JarvisConfig, load_config
        print("✅ Config module imported")
        
        # Test config loading
        config = load_config()
        print(f"✅ Config loaded: {config.app_name} v{config.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_audio_fallback():
    """Test basic audio components without external dependencies."""
    try:
        # Test basic structures
        from src.core.audio import AudioData
        import numpy as np
        
        # Create test audio data
        test_audio = AudioData(
            data=np.array([0.1, 0.2, 0.3]),
            sample_rate=16000,
            duration=1.0,
            timestamp=123456789.0
        )
        
        print("✅ Audio data structures work")
        return True
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return False

def test_fallback_responses():
    """Test fallback response system."""
    try:
        from src.core.ai import FallbackResponses
        
        # Test different response categories
        greeting = FallbackResponses.get_response("greeting")
        status = FallbackResponses.get_response("status") 
        thanks = FallbackResponses.get_response("thanks")
        
        print(f"✅ Fallback responses: greeting='{greeting}'")
        print(f"✅ Fallback responses: status='{status}'")
        print(f"✅ Fallback responses: thanks='{thanks}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback responses test failed: {e}")
        return False

def main():
    """Run architecture tests."""
    print("🧪 Testing New Jarvis Architecture")
    print("=" * 40)
    
    tests = [
        ("Configuration System", test_imports),
        ("Audio Structures", test_audio_fallback),
        ("Fallback Responses", test_fallback_responses)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        print("-" * 20)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: CRASHED - {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All architecture tests passed!")
        print("📝 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Start Ollama: ollama serve")
        print("   3. Run Jarvis: python main.py")
    else:
        print("⚠️  Some tests failed - check dependencies")

if __name__ == "__main__":
    main()
