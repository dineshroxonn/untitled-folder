import { useState, useRef, useEffect } from 'react';

interface UseVoiceReturn {
  isSpeaking: boolean;
  isListening: boolean;
  speakText: (text: string) => Promise<boolean>;
  startListening: () => void;
  stopListening: () => void;
  voiceAvailable: boolean;
  checkVoiceStatus: () => Promise<boolean>;
}

export const useVoice = (): UseVoiceReturn => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceAvailable, setVoiceAvailable] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<any>(null);

  // Check if voice service is available
  const checkVoiceStatus = async (): Promise<boolean> => {
    try {
      const response = await fetch('/api/voice-status');
      const data = await response.json();
      setVoiceAvailable(data.available);
      return data.available;
    } catch (error) {
      console.error('Failed to check voice status:', error);
      setVoiceAvailable(false);
      return false;
    }
  };

  // Initialize voice status check and speech recognition
  useEffect(() => {
    checkVoiceStatus();
    
    // Initialize speech recognition if available
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
    }
    
    return () => {
      // Cleanup
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
      }
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const speakText = async (text: string): Promise<boolean> => {
    console.log('Attempting to speak text:', text);
    if (!voiceAvailable || !text.trim()) {
      console.log('Voice not available or text is empty');
      return false;
    }

    try {
      setIsSpeaking(true);
      console.log('Calling backend text-to-speech endpoint');
      
      // Call the backend text-to-speech endpoint
      const response = await fetch('/api/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get audio data as blob
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      console.log('Audio data received, playing audio');
      
      // Play the audio
      return new Promise((resolve) => {
        if (audioRef.current) {
          audioRef.current.pause();
        }
        
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        
        audio.onended = () => {
          console.log('Audio playback finished');
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
          resolve(true);
        };
        
        audio.onerror = () => {
          console.log('Audio playback error');
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
          resolve(false);
        };
        
        audio.play().catch((error) => {
          console.error('Failed to play audio:', error);
          setIsSpeaking(false);
          URL.revokeObjectURL(audioUrl);
          resolve(false);
        });
      });
    } catch (error) {
      console.error('Text to speech error:', error);
      setIsSpeaking(false);
      return false;
    }
  };

  const startListening = () => {
    console.log('Starting speech recognition');
    if (recognitionRef.current) {
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        console.log('Speech recognition result:', transcript);
        // Dispatch a custom event with the transcript
        window.dispatchEvent(new CustomEvent('speechResult', { detail: transcript }));
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
      };
      
      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started');
        setIsListening(true);
      };
      
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Failed to start speech recognition:', error);
        setIsListening(false);
      }
    }
  };

  const stopListening = () => {
    console.log('Stopping speech recognition');
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  return {
    isSpeaking,
    isListening,
    speakText,
    startListening,
    stopListening,
    voiceAvailable,
    checkVoiceStatus
  };
};