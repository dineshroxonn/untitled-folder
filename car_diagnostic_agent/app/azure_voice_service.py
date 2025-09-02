# Import with error handling to prevent breaking existing functionality
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SDK_AVAILABLE = True
except ImportError:
    print("Warning: Azure Cognitive Services Speech SDK not available. Voice features will be disabled.")
    AZURE_SDK_AVAILABLE = False
    speechsdk = None

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AzureVoiceService:
    def __init__(self):
        self.subscription_key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        if AZURE_SDK_AVAILABLE and self.subscription_key:
            try:
                self.speech_config = speechsdk.SpeechConfig(
                    subscription=self.subscription_key, 
                    region=self.region
                )
                # Use a professional male voice suitable for a mechanic
                self.speech_config.speech_synthesis_voice_name = "en-US-DavisNeural"
            except Exception as e:
                print(f"Warning: Failed to initialize Azure Speech Config: {e}")
                self.speech_config = None
        else:
            self.speech_config = None
            if not AZURE_SDK_AVAILABLE:
                print("Azure SDK not available - voice features disabled")
            elif not self.subscription_key:
                print("AZURE_SPEECH_KEY not set - voice features disabled")
    
    def is_available(self) -> bool:
        """Check if Azure voice service is configured and available"""
        return self.speech_config is not None
    
    async def speech_to_text(self) -> Optional[str]:
        """Convert speech to text using Azure Speech Services"""
        if not self.is_available():
            return None
            
        try:
            # For server-side speech-to-text, we would need to receive audio data
            # This is a placeholder for potential server-side processing
            # In practice, web applications typically handle speech-to-text in the browser
            print("Speech to text service ready - use frontend for actual recording")
            return None
        except Exception as e:
            print(f"Speech to text error: {e}")
            return None
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech and return audio data"""
        if not self.is_available() or not AZURE_SDK_AVAILABLE:
            return None
            
        try:
            # Create audio configuration for in-memory output
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Return audio data as bytes
                return result.audio_data
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation_details.error_details}")
                return None
                
        except Exception as e:
            print(f"Text to speech error: {e}")
            return None

# Global instance
azure_voice_service = AzureVoiceService()