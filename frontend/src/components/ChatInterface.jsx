
import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2 } from 'lucide-react';
import MessageBubble from './MessageBubble';
import VoiceButton from './VoiceButton';
import LoadingSpinner from './LoadingSpinner';
import { useChat } from '../hooks/useChat';
import './ChatInterface.css';

const ChatInterface = () => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    await sendMessage(inputValue);
    setInputValue('');
  };

  const handleVoiceTranscription = (transcription) => {
    setInputValue(transcription);
  };

  return (
    <div className="chat-interface">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <h2>💬 Medical Assistant Chat</h2>
          <button 
            className="clear-button"
            onClick={clearMessages}
            title="Clear conversation"
          >
            <Trash2 size={18} />
          </button>
        </div>
        <p className="chat-subtitle">Ask me anything about health and medical conditions</p>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="loading-message">
            <LoadingSpinner message="Thinking..." />
          </div>
        )}
        
        {error && (
          <div className="error-message">
            ❌ Error: {error}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-container">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <VoiceButton onTranscription={handleVoiceTranscription} />
          
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a medical question..."
            className="chat-input"
            disabled={isLoading}
          />
          
          <button
            type="submit"
            className="send-button"
            disabled={!inputValue.trim() || isLoading}
          >
            <Send size={20} />
          </button>
        </form>
        
        <p className="disclaimer">
          ⚠️ This is for informational purposes only. Always consult a healthcare professional.
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;