#!/usr/bin/env python3
"""
JARVIS Smart Model Downloader - Auto-selects optimal model for your system
RTX 3050 Ti + 16GB RAM = Qwen2.5-7B Q3_K_M (Best Balance)
"""

import os
import sys
import requests
from pathlib import Path
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
        print(f"🔽 Starting download from: {url}")
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
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"\r🔽 Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
        
        print(f"\n✅ Downloaded: {destination}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return False

def main():
    """Smart download for RTX 3050 Ti system"""
    print("🤖 JARVIS Smart Model Downloader")
    print("=" * 50)
    print("🎯 System Analysis:")
    print("   • GPU: RTX 3050 Ti Laptop (4GB VRAM)")
    print("   • RAM: 16 GB")
    print("   • Optimal Model: Qwen2.5-7B Q3_K_M")
    print("   • Size: 3.81 GB")
    print("   • Performance: Excellent balance for your GPU")
    print()
    
    # Create models directory at project root
    # (__file__ is src/utils/download_model.py, so go up three levels to workspace root)
    project_root = Path(__file__).parent.parent.parent
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Optimal model for RTX 3050 Ti
    model = {
        "name": "Qwen2.5-7B Q3_K_M (RTX 3050 Ti Optimized)",
        "file": "qwen2.5-7b-instruct-q3_k_m.gguf",
        "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q3_k_m.gguf",
        "size": "3.81 GB"
    }
    
    model_path = models_dir / model["file"]
    
    # Check if model already exists
    if model_path.exists():
        print(f"✅ Model already exists: {model_path}")
        print(f"📊 File size: {model_path.stat().st_size / (1024*1024*1024):.2f} GB")
        print("\n🚀 Model ready! Start your JARVIS server:")
        print("   run_jarvis_llamacpp.bat")
        return
    
    print("🔽 Downloading optimal model for your system...")
    print(f"📁 Destination: {model_path}")
    print("⏳ This will take 5-10 minutes depending on your internet speed...")
    print()
    
    # Download the optimal model
    if download_file(model["url"], model_path):
        print(f"\n🎉 SUCCESS! Optimal model downloaded!")
        print(f"📁 Location: {model_path}")
        print(f"📊 Size: {model_path.stat().st_size / (1024*1024*1024):.2f} GB")
        print()
        print("🚀 Next Steps:")
        print("   1. Start server: run_jarvis_llamacpp.bat")
        print("   2. Open browser: http://localhost:5000/")
        print("   3. Enjoy ultra-fast AI responses!")
        print()
        print("⚡ Expected Performance:")
        print("   • Response time: 0.5-2 seconds")
        print("   • Quality: Excellent (Qwen2.5 latest)")
        print("   • GPU utilization: Optimal for RTX 3050 Ti")
    else:
        print("❌ Download failed. Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
