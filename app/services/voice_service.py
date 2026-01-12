import whisper
import pyttsx3
import os
from typing import Optional
import tempfile


class VoiceService:
    """Handles speech-to-text and text-to-speech"""
    
    def __init__(self, whisper_model_size: str = "base"):
        print(f"🎤 Loading Whisper model ({whisper_model_size})...")
        try:
            self.whisper_model = whisper.load_model(whisper_model_size)
            print("✅ Whisper model loaded!")
        except Exception as e:
            print(f"⚠️  Warning: Could not load Whisper model: {e}")
            self.whisper_model = None
        
        print("🔊 Initializing TTS engine...")
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            print("✅ TTS engine initialized!")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize TTS: {e}")
            self.tts_engine = None
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Convert speech to text using Whisper"""
        if not self.whisper_model:
            return "Error: Whisper model not loaded"
        
        print(f"🎤 Transcribing audio: {audio_file_path}")
        
        try:
            result = self.whisper_model.transcribe(audio_file_path)
            text = result["text"].strip()
            print(f"✅ Transcription: {text}")
            return text
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return f"Error: {str(e)}"
    
    def synthesize_speech(
        self, 
        text: str, 
        output_path: Optional[str] = None
    ) -> str:
        """Convert text to speech"""
        if not self.tts_engine:
            return "Error: TTS engine not initialized"
        
        print(f"🔊 Synthesizing speech for: {text[:50]}...")
        
        if not output_path:
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix='.mp3'
            )
            output_path = temp_file.name
            temp_file.close()
        
        try:
            self.tts_engine.save_to_file(text, output_path)
            self.tts_engine.runAndWait()
            print(f"✅ Audio saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return f"Error: {str(e)}"
    
    def speak(self, text: str):
        """Speak text immediately"""
        if not self.tts_engine:
            print("TTS engine not available")
            return
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ Speak error: {e}")