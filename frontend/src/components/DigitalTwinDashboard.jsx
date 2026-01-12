import VitalsInput from './VitalsInput';
import React, { useState, useEffect } from 'react';
import { Activity, Heart, Droplet, Wind, RefreshCw } from 'lucide-react';
import VitalsChart from './VitalsChart';
import AlertPanel from './AlertPanel';
import LoadingSpinner from './LoadingSpinner';
import { getLatestVitals, getVitalsHistory, generateMockVitals, getVitalsSummary } from '../services/api';
import './DigitalTwinDashboard.css';

const DigitalTwinDashboard = () => {
  const [latestVitals, setLatestVitals] = useState(null);
  const [vitalsHistory, setVitalsHistory] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try to get existing data
      const latest = await getLatestVitals();
      
      if (!latest) {
        // Generate mock data if none exists
        await generateMockVitals('demo_patient', 30);
      }
      
      // Load all data
      const [vitals, history, summaryData] = await Promise.all([
        getLatestVitals(),
        getVitalsHistory('demo_patient', 30),
        getVitalsSummary('demo_patient')
      ]);
      
      setLatestVitals(vitals);
      setVitalsHistory(history);
      setSummary(summaryData);
    } catch (err) {
      setError(err.message);
      console.error('Error loading vitals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading health data..." />;
  }

  if (error) {
    return (
      <div className="error-state">
        <p>❌ Error loading data: {error}</p>
        <button onClick={loadData} className="retry-button">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  if (!latestVitals) {
    return <div className="error-state">No health data available</div>;
  }

  return (
    <div className="digital-twin-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-header-content">
          <h2>🏥 Digital Twin Dashboard</h2>
          <button onClick={loadData} className="refresh-button" title="Refresh data">
            <RefreshCw size={18} />
          </button>
        </div>
        <p className="dashboard-subtitle">Real-time health monitoring</p>
      </div>

      <div className="dashboard-content">
        {/* Alerts */}
        {summary?.alerts && <AlertPanel alerts={summary.alerts} />}

        {/* Current Vitals Cards */}
        <div className="vitals-grid">
          <div className="vital-card">
            <div className="vital-icon heart">
              <Heart size={24} />
            </div>
            <div className="vital-info">
              <span className="vital-label">Heart Rate</span>
              <span className="vital-value">
                {latestVitals.heart_rate || '--'}
                <span className="vital-unit">bpm</span>
              </span>
              <span className="vital-status normal">Normal</span>
            </div>
          </div>

          <div className="vital-card">
            <div className="vital-icon pressure">
              <Activity size={24} />
            </div>
            <div className="vital-info">
              <span className="vital-label">Blood Pressure</span>
              <span className="vital-value">
                {latestVitals.blood_pressure_systolic}/{latestVitals.blood_pressure_diastolic}
                <span className="vital-unit">mmHg</span>
              </span>
              <span className={`vital-status ${latestVitals.blood_pressure_systolic > 130 ? 'warning' : 'normal'}`}>
                {latestVitals.blood_pressure_systolic > 130 ? 'Elevated' : 'Normal'}
              </span>
            </div>
          </div>

          <div className="vital-card">
            <div className="vital-icon glucose">
              <Droplet size={24} />
            </div>
            <div className="vital-info">
              <span className="vital-label">Blood Glucose</span>
              <span className="vital-value">
                {latestVitals.blood_glucose || '--'}
                <span className="vital-unit">mg/dL</span>
              </span>
              <span className="vital-status normal">Normal</span>
            </div>
          </div>

          <div className="vital-card">
            <div className="vital-icon oxygen">
              <Wind size={24} />
            </div>
            <div className="vital-info">
              <span className="vital-label">Oxygen Sat.</span>
              <span className="vital-value">
                {latestVitals.oxygen_saturation || '--'}
                <span className="vital-unit">%</span>
              </span>
              <span className="vital-status normal">Normal</span>
            </div>
          </div>
        </div>

        {/* Charts */}
        {vitalsHistory.length > 0 && (
          <div className="charts-section">
            <VitalsChart
              data={vitalsHistory}
              dataKey="heart_rate"
              title="Heart Rate Trend"
              color="#e74c3c"
              unit="bpm"
            />
            
            <VitalsChart
              data={vitalsHistory}
              dataKey="blood_pressure_systolic"
              title="Blood Pressure (Systolic)"
              color="#3498db"
              unit="mmHg"
            />
            
            <VitalsChart
              data={vitalsHistory}
              dataKey="blood_glucose"
              title="Blood Glucose Levels"
              color="#f39c12"
              unit="mg/dL"
            />
          </div>
        )}

        {/* Summary Stats */}
        {summary?.['30_day_averages'] && (
          <div className="summary-stats">
            <h4>30-Day Averages</h4>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Avg Heart Rate</span>
                <span className="stat-value">{summary['30_day_averages'].heart_rate} bpm</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg BP (Systolic)</span>
                <span className="stat-value">{summary['30_day_averages'].blood_pressure_systolic} mmHg</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Glucose</span>
                <span className="stat-value">{summary['30_day_averages'].blood_glucose} mg/dL</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DigitalTwinDashboard;