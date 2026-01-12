import React, { useState } from 'react';
import { Save } from 'lucide-react';
import api from '../services/api'; // Import the central api instance
import './VitalsInput.css';

const VitalsInput = ({ onVitalsSubmit }) => {
  const [vitals, setVitals] = useState({
    heart_rate: '',
    blood_pressure_systolic: '',
    blood_pressure_diastolic: '',
    blood_glucose: '',
    temperature: '',
    oxygen_saturation: '',
    weight: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setVitals({
      ...vitals,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // Use the 'api' instance we configured earlier
      const response = await api.post('/digital-twin/vitals', {
        user_id: 'demo_patient',
        heart_rate: vitals.heart_rate ? parseInt(vitals.heart_rate) : null,
        blood_pressure_systolic: vitals.blood_pressure_systolic ? parseInt(vitals.blood_pressure_systolic) : null,
        blood_pressure_diastolic: vitals.blood_pressure_diastolic ? parseInt(vitals.blood_pressure_diastolic) : null,
        blood_glucose: vitals.blood_glucose ? parseFloat(vitals.blood_glucose) : null,
        temperature: vitals.temperature ? parseFloat(vitals.temperature) : null,
        oxygen_saturation: vitals.oxygen_saturation ? parseInt(vitals.oxygen_saturation) : null,
        weight: vitals.weight ? parseFloat(vitals.weight) : null
      });

      setMessage('✅ Vitals saved successfully!');
      // Clear form
      setVitals({
        heart_rate: '',
        blood_pressure_systolic: '',
        blood_pressure_diastolic: '',
        blood_glucose: '',
        temperature: '',
        oxygen_saturation: '',
        weight: ''
      });
      
      // Refresh dashboard if callback exists
      if (onVitalsSubmit) onVitalsSubmit();
    } catch (error) {
      console.error("Vitals Update Error:", error);
      setMessage('❌ Failed to save vitals: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vitals-input-container">
      <h3>📝 Update Vitals</h3>
      <form onSubmit={handleSubmit} className="vitals-form">
        <div className="form-row">
          <div className="form-group">
            <label>Heart Rate (bpm)</label>
            <input
              type="number"
              name="heart_rate"
              value={vitals.heart_rate}
              onChange={handleChange}
              placeholder="e.g. 72"
            />
          </div>

          <div className="form-group">
            <label>Blood Pressure (sys/dia)</label>
            <div className="bp-input-group">
              <input
                type="number"
                name="blood_pressure_systolic"
                value={vitals.blood_pressure_systolic}
                onChange={handleChange}
                placeholder="120"
              />
              <span className="separator">/</span>
              <input
                type="number"
                name="blood_pressure_diastolic"
                value={vitals.blood_pressure_diastolic}
                onChange={handleChange}
                placeholder="80"
              />
            </div>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Blood Glucose (mg/dL)</label>
            <input
              type="number"
              name="blood_glucose"
              value={vitals.blood_glucose}
              onChange={handleChange}
              placeholder="e.g. 95"
            />
          </div>

          <div className="form-group">
            <label>Temperature (°F)</label>
            <input
              type="number"
              step="0.1"
              name="temperature"
              value={vitals.temperature}
              onChange={handleChange}
              placeholder="e.g. 98.6"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Oxygen Saturation (%)</label>
            <input
              type="number"
              name="oxygen_saturation"
              value={vitals.oxygen_saturation}
              onChange={handleChange}
              placeholder="e.g. 98"
            />
          </div>

          <div className="form-group">
            <label>Weight (lbs)</label>
            <input
              type="number"
              step="0.1"
              name="weight"
              value={vitals.weight}
              onChange={handleChange}
              placeholder="e.g. 165"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="save-vitals-btn" disabled={loading}>
            <Save size={18} />
            {loading ? 'Saving...' : 'Save Vitals'}
          </button>
        </div>

        {message && (
          <div className={`form-message ${message.includes('✅') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
};

export default VitalsInput;