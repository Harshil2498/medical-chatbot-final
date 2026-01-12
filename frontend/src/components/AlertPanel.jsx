import React from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import './AlertPanel.css';

const AlertPanel = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="alert-panel no-alerts">
        <CheckCircle size={20} />
        <span>All vitals within normal range</span>
      </div>
    );
  }

  return (
    <div className="alert-panel has-alerts">
      <div className="alert-header">
        <AlertCircle size={20} />
        <span className="alert-title">Health Alerts ({alerts.length})</span>
      </div>
      <ul className="alert-list">
        {alerts.map((alert, idx) => (
          <li key={idx} className="alert-item">
            {alert}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AlertPanel;