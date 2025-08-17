#!/usr/bin/env python3
"""
Jarvis AI Assistant - Main Entry Point

A modern, LangChain-based voice assistant with Ollama integration.
Clean architecture with proper separation of concerns.
"""

import logging
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

from config.settings import JarvisConfig, load_config
from src.agents.jarvis_agent import JarvisAgent, OperationMode

console = Console()


def setup_logging(debug: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    
    # Suppress some noisy loggers
    logging.getLogger("whisper").setLevel(logging.WARNING)
    logging.getLogger("sounddevice").setLevel(logging.WARNING)


def print_banner():
    """Print Jarvis banner."""
    banner = Text("🤖 JARVIS AI ASSISTANT", style="bold cyan")
    subtitle = Text("LangChain-based Voice Assistant with Ollama Integration", style="italic")
    
    console.print(Panel(
        f"{banner}\n{subtitle}",
        border_style="cyan",
        padding=(1, 2)
    ))


def print_status(agent: JarvisAgent):
    """Print system status."""
    stats = agent.get_stats()
    
    ai_status = "🟢 Online" if stats['ai_available'] else "🔴 Offline" 
    
    status_text = f"""
🎤 Audio System: 🟢 Ready
🤖 AI System: {ai_status}
👤 Personality: {stats['personality']}
🔄 Mode: {stats['current_mode']}
"""
    
    console.print(Panel(status_text, title="System Status", border_style="green"))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Jarvis AI Assistant")
    parser.add_argument("--mode", choices=["interactive", "continuous"], 
                       default="interactive", help="Operation mode")
    parser.add_argument("--personality", choices=["professional_assistant", "iron_man_jarvis", "friendly_helper"],
                       help="AI personality")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    
    try:
        # Load configuration
        config = load_config()
        if args.personality:
            config.personality = args.personality
        
        print_banner()
        
        # Initialize Jarvis
        console.print("🚀 Initializing Jarvis...", style="yellow")
        agent = JarvisAgent(config)
        
        # Print system status
        print_status(agent)
        
        # Check prerequisites
        if not agent.ai.is_available():
            console.print("\n⚠️  AI features unavailable. To enable:", style="yellow")
            console.print("   1. Start Ollama: ollama serve")
            console.print("   2. Pull model: ollama pull llama3.1")
            console.print("   Jarvis will operate in basic mode.\n")
        
        # Run in selected mode
        if args.mode == "continuous":
            agent.run_continuous()
        else:
            agent.run_interactive()
            
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="cyan")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
        if args.debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
