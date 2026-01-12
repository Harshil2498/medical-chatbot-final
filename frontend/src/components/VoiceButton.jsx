import React, { useState } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import AudioRecorder from '../services/audioRecorder';
import { transcribeAudio, synthesizeSpeech } from '../services/api';
import './VoiceButton.css';

const VoiceButton = ({ onTranscription }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recorder] = useState(() => new AudioRecorder());
  const [isPlaying, setIsPlaying] = useState(false);

  const handleVoiceInput = async (e) => {
    // Optional: Prevent any event bubbling just to be extra safe
    e.stopPropagation(); 
    
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      const audioBlob = await recorder.stopRecording();
      
      if (audioBlob) {
        try {
          const result = await transcribeAudio(audioBlob);
          if (result.transcription) {
            onTranscription(result.transcription);
          }
        } catch (error) {
          console.error('Transcription error:', error);
          alert('Failed to transcribe audio. Please try again.');
        }
      }
    } else {
      // Start recording
      try {
        await recorder.startRecording();
        setIsRecording(true);
      } catch (error) {
        console.error('Recording error:', error);
        alert('Microphone access denied. Please enable microphone permissions.');
      }
    }
  };

  return (
    <div className="voice-controls">
      <button
        type="button" // ⬅️ THIS IS THE FIX
        onClick={handleVoiceInput}
        className={`voice-button ${isRecording ? 'recording' : ''}`}
        title={isRecording ? 'Stop Recording' : 'Start Voice Input'}
      >
        {isRecording ? (
          <>
            <MicOff size={20} />
            <span className="recording-indicator">Recording...</span>
          </>
        ) : (
          <Mic size={20} />
        )}
      </button>
    </div>
  );
};

export default VoiceButton;