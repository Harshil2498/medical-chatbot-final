import React from 'react';
import { User, Bot, CheckCircle } from 'lucide-react';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'bot'}`}>
      {/* Icon Section */}
      <div className="icon-container">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>

      {/* Content Section */}
      <div className="message-content">
        <div className="bubble-text">
          {message.content}
        </div>

        {/* Sources Section (RAG) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources-container">
            <p>📚 Sources:</p>
            {message.sources.map((source, idx) => (
              <div key={idx} className="source-item">
                <span className="source-index">{idx + 1}.</span>
                <span className="source-title">{source.title}</span>
                <span className="source-score">
                  ({(source.relevance_score * 100).toFixed(0)}% match)
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Metadata Footer */}
        <div className="message-footer">
          <span className="timestamp">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>

          {!isUser && message.cached && (
            <span className="cache-badge">
              <CheckCircle size={12} /> Cached
            </span>
          )}

          {!isUser && message.confidence && (
            <span className="confidence-score">
              Confidence: {(message.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;