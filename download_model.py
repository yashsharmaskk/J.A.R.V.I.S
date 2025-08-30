#!/usr/bin/env python3
"""
JARVIS Model Downloader - Download GGUF models for llama-cpp-python
Downloads optimized models for maximum performance
"""

import os
import sys
import requests
from pathlib import Path
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_file(url, destination):
    """Download a file with progress tracking"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r🔽 Progress: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", end='', flush=True)
        
        print(f"\n✅ Downloaded: {destination}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

def merge_files(part_files, output_file):
    """Merge multiple part files into one"""
    try:
        with open(output_file, 'wb') as outfile:
            for part_file in part_files:
                if part_file.exists():
                    with open(part_file, 'rb') as infile:
                        outfile.write(infile.read())
                    # Clean up part file
                    part_file.unlink()
                else:
                    logger.error(f"❌ Part file not found: {part_file}")
                    return False
        
        logger.info(f"✅ Merged into: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Merge failed: {e}")
        return False

def main():
    """Main downloader function"""
    print("🤖 JARVIS Model Downloader")
    print("=" * 50)
    
    # Create models directory
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Available models (optimized for speed and quality)
    models = {
        "1": {
            "name": "Qwen2.5-7B Q4_K_M (⭐ RECOMMENDED - Best Balance)",
            "file": "qwen2.5-7b-instruct-q4_k_m.gguf",
            "urls": [
                "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf",
                "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf"
            ],
            "size": "4.7 GB",
            "description": "Latest Qwen2.5 model with excellent quality and speed"
        },
        "2": {
            "name": "Qwen2.5-7B Q2_K (Fastest)",
            "file": "qwen2.5-7b-instruct-q2_k.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q2_k.gguf",
            "size": "3.02 GB",
            "description": "Smallest size, fastest inference"
        },
        "3": {
            "name": "Qwen2.5-7B Q3_K_M (Good Balance)",
            "file": "qwen2.5-7b-instruct-q3_k_m.gguf",
            "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q3_k_m.gguf",
            "size": "3.81 GB",
            "description": "Medium size with good quality"
        },
        "4": {
            "name": "Phi-3 Mini Q4_K_M (Alternative)",
            "file": "Phi-3-mini-4k-instruct-q4_k_m.gguf",
            "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_k_m.gguf",
            "size": "2.4 GB",
            "description": "Compact Microsoft model"
        },
        "5": {
            "name": "TinyLlama (Testing Only)",
            "file": "tinyllama-1.1b-chat-v1.0.q4_0.gguf",
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_0.gguf",
            "size": "669 MB",
            "description": "Ultra-fast but basic responses"
        }
    }
    
    print("📥 Available models:")
    for key, model in models.items():
        print(f"   {key}. {model['name']} ({model['size']})")
        print(f"      {model['description']}")
    
    print("\n💡 Recommendations:")
    print("   • Option 1: Qwen2.5-7B Q4_K_M - Latest, best quality")
    print("   • Option 2: Qwen2.5-7B Q2_K - Fastest responses")
    print("   • Option 3: Qwen2.5-7B Q3_K_M - Good balance")
    print("   • Option 4: Phi-3 Mini - Smaller, efficient")
    
    # Get user choice
    choice = input(f"\n🎯 Select model (1-{len(models)}) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("👋 Goodbye!")
        return
    
    if choice not in models:
        print("❌ Invalid choice!")
        return
    
    selected_model = models[choice]
    model_path = models_dir / selected_model["file"]
    
    # Check if model already exists
    if model_path.exists():
        print(f"✅ Model already exists: {model_path}")
        overwrite = input("🔄 Download again? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("👍 Using existing model.")
            return
    
    print(f"\n🔽 Downloading: {selected_model['name']}")
    print(f"📁 To: {model_path}")
    print(f"📊 Size: {selected_model['size']}")
    print("⏳ This may take several minutes...")
    
    success = False
    
    # Handle multi-part downloads
    if 'urls' in selected_model:
        print(f"📦 Multi-part download ({len(selected_model['urls'])} parts)")
        part_files = []
        
        for i, url in enumerate(selected_model['urls'], 1):
            part_name = f"{selected_model['file']}.part{i:02d}"
            part_path = models_dir / part_name
            part_files.append(part_path)
            
            print(f"\n🔽 Downloading part {i}/{len(selected_model['urls'])}: {part_name}")
            if not download_file(url, part_path):
                print("❌ Part download failed!")
                return
        
        # Merge parts
        print(f"\n🔧 Merging {len(part_files)} parts...")
        success = merge_files(part_files, model_path)
        
    else:
        # Single file download
        success = download_file(selected_model["url"], model_path)
    
    if success:
        print(f"\n🎉 Success! Model downloaded to: {model_path}")
        print(f"\n🚀 Now restart your JARVIS server to use the new model!")
        print(f"   python jarvis_web_server_llamacpp.py")
    else:
        print("❌ Download failed. Please try again.")

if __name__ == "__main__":
    main()
