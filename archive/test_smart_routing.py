"""
Test the smart model routing system.

This script demonstrates how Jarvis automatically selects:
- phi3 for simple conversations
- llama3.1 for complex topics
"""

import sys
from pathlib import Path
import time

# Add the current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_routing():
    """Test the smart model routing functionality."""
    try:
        from jarvis_clean import JarvisConfig, OllamaAI
        
        print("🧪 Testing Smart Model Routing")
        print("=" * 40)
        
        # Initialize AI system
        config = JarvisConfig()
        ai = OllamaAI(config)
        
        if not ai.is_available():
            print("❌ Ollama not available - start with 'ollama serve'")
            return
        
        # Test conversations that should use different models
        test_cases = [
            # Simple conversations (should use phi3)
            {
                "message": "Hello Jarvis, how are you?",
                "expected_model": "phi3",
                "category": "Simple Greeting"
            },
            {
                "message": "What time is it?",
                "expected_model": "phi3", 
                "category": "Basic Question"
            },
            {
                "message": "Thanks for your help!",
                "expected_model": "phi3",
                "category": "Gratitude"
            },
            
            # Complex topics (should use llama3.1)
            {
                "message": "Explain how quantum computing works and its advantages over classical computing",
                "expected_model": "llama3.1",
                "category": "Complex Science"
            },
            {
                "message": "Help me understand the differences between machine learning algorithms and when to use each one",
                "expected_model": "llama3.1", 
                "category": "Technical Analysis"
            },
            {
                "message": "Write a detailed plan for learning Python programming from beginner to advanced level",
                "expected_model": "llama3.1",
                "category": "Detailed Planning"
            }
        ]
        
        correct_predictions = 0
        
        for i, test_case in enumerate(test_cases, 1):
            message = test_case["message"]
            expected = test_case["expected_model"]
            category = test_case["category"]
            
            print(f"\n--- Test {i}: {category} ---")
            print(f"💬 Message: {message[:60]}{'...' if len(message) > 60 else ''}")
            
            # Test model selection logic
            selected_model = ai._select_model(message)
            is_correct = selected_model == expected
            
            if is_correct:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"{status} Expected: {expected} | Selected: {selected_model}")
            
            # Actually send the message to see the routing in action
            print("📤 Sending to AI...")
            start_time = time.time()
            response = ai.chat(message)
            response_time = time.time() - start_time
            
            if response:
                print(f"✅ Response received in {response_time:.2f}s")
                print(f"🤖 Response preview: {response[:100]}{'...' if len(response) > 100 else ''}")
            else:
                print("❌ No response received")
            
            print("-" * 40)
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        accuracy = (correct_predictions / len(test_cases)) * 100
        print(f"\n📊 ROUTING ACCURACY: {correct_predictions}/{len(test_cases)} ({accuracy:.1f}%)")
        
        if accuracy >= 80:
            print("🎉 Smart routing working well!")
        else:
            print("⚠️  Routing logic may need adjustment")
        
        # Show conversation history with model info
        print(f"\n📚 Conversation History ({len(ai.conversation_history)} messages):")
        for i, conv in enumerate(ai.conversation_history[-3:], 1):  # Show last 3
            model = conv.get('model', 'unknown')
            user_msg = conv['user'][:50] + '...' if len(conv['user']) > 50 else conv['user']
            print(f"  {i}. [{model}] {user_msg}")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_manual_switching():
    """Test manual model switching commands."""
    print(f"\n🔧 Testing Manual Model Switching")
    print("=" * 40)
    
    try:
        from jarvis_clean import JarvisAssistant, JarvisConfig
        
        config = JarvisConfig()
        assistant = JarvisAssistant(config)
        
        if not assistant.ai.is_available():
            print("❌ AI not available")
            return
        
        # Test switching commands
        switch_commands = [
            "use smart mode",
            "switch to phi", 
            "status report"
        ]
        
        for command in switch_commands:
            print(f"\n💬 Command: '{command}'")
            response = assistant.process_message(command)
            print(f"🤖 Response: {response}")
    
    except Exception as e:
        print(f"❌ Manual switching test failed: {e}")

def main():
    """Run all routing tests."""
    test_model_routing()
    test_manual_switching()
    
    print(f"\n🎯 Key Benefits of Smart Routing:")
    print("• ⚡ phi3: Fast responses for simple chats (~2.2GB)")
    print("• 🧠 llama3.1: Deep analysis for complex topics (~4.9GB)")
    print("• 🤖 Automatic selection based on message complexity")
    print("• 🔧 Manual override with voice commands")
    print("• 📈 Optimal performance and resource usage")

if __name__ == "__main__":
    main()
