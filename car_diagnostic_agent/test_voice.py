#!/usr/bin/env python3
"""
Test script for Azure voice service
"""
import os
import sys
import asyncio

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.azure_voice_service import azure_voice_service

async def test_voice_service():
    print("Testing Azure Voice Service...")
    
    # Check if service is available
    if not azure_voice_service.is_available():
        print("❌ Azure voice service not available - check AZURE_SPEECH_KEY environment variable")
        return
    
    print("✅ Azure voice service is configured")
    
    # Test text to speech
    test_text = "Hello, I am your car diagnostic assistant. Your vehicle has been scanned successfully."
    print(f"Testing text to speech with: '{test_text}'")
    
    audio_data = await azure_voice_service.text_to_speech(test_text)
    if audio_data:
        print("✅ Text to speech successful")
        print(f"Audio data size: {len(audio_data)} bytes")
        
        # Save to file for verification
        with open("/tmp/test_speech.wav", "wb") as f:
            f.write(audio_data)
        print("💾 Audio saved to /tmp/test_speech.wav")
    else:
        print("❌ Text to speech failed")

if __name__ == "__main__":
    asyncio.run(test_voice_service())