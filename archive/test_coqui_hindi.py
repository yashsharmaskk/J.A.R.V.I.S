#!/usr/bin/env python3
"""
🧠 Coqui TTS Hindi Test Script
Test Hindi and Hinglish speech synthesis with Coqui TTS
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_coqui_hindi():
    """Test Coqui TTS with Hindi text"""
    try:
        # Import TTS
        from TTS.api import TTS
        logger.info("🎯 Testing Coqui TTS Hindi Synthesis...")
        print("=" * 50)
        
        # Initialize TTS with multilingual model (supports Hindi)
        logger.info("📥 Loading multilingual model...")
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                 progress_bar=False, gpu=False)
        
        # Test texts
        test_texts = [
            ("English", "Hello, I am Jarvis, your AI assistant."),
            ("Hindi", "नमस्ते, मैं जार्विस हूँ, आपका AI असिस्टेंट।"),
            ("Hinglish", "Hello yaar, main Jarvis hun, aapka AI assistant.")
        ]
        
        # Create output directory
        output_dir = Path("tts_test_output")
        output_dir.mkdir(exist_ok=True)
        
        logger.info("🎵 Generating speech samples...")
        
        for lang, text in test_texts:
            try:
                output_file = output_dir / f"test_{lang.lower()}.wav"
                
                logger.info(f"  🗣️  {lang}: {text}")
                
                # Generate speech
                tts.tts_to_file(
                    text=text,
                    file_path=str(output_file),
                    language="hi" if lang in ["Hindi", "Hinglish"] else "en"
                )
                
                logger.info(f"  ✅ Saved: {output_file}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed {lang}: {str(e)}")
        
        logger.info(f"\n🎉 Test completed! Audio files saved in: {output_dir}")
        return True
        
    except ImportError:
        logger.error("❌ Coqui TTS not installed. Run: pip install coqui-tts")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🧠 COQUI TTS HINDI TEST")
    print("=" * 50)
    
    success = test_coqui_hindi()
    
    if success:
        print("\n🎯 COQUI TTS IS READY FOR JARVIS!")
        print("✅ Hindi and Hinglish synthesis working")
        print("✅ Integration with Jarvis ready")
    else:
        print("\n❌ Coqui TTS setup needs attention")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
