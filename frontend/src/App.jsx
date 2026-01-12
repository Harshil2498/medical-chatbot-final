import React from 'react';
import ChatInterface from './components/ChatInterface';
import DigitalTwinDashboard from './components/DigitalTwinDashboard';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <div style={{ width: '100%', maxWidth: '1400px' }}>
        <div className="app-header">
          <h1>🏥 Medical Chatbot MVP</h1>
          <p>AI-Powered Medical Information Assistant with Digital Twin Health Monitoring</p>
        </div>

        <div className="app-content">
          <div className="chat-section">
            <ChatInterface />
          </div>

          <div className="digital-twin-section">
            <DigitalTwinDashboard />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;