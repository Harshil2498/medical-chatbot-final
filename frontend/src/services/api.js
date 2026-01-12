import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API
export const sendChatMessage = async (query, useCache = true) => {
  try {
    const response = await api.post('/chat/query', {
      query,
      use_cache: useCache,
    });
    return response.data;
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
};

// Voice API
export const transcribeAudio = async (audioBlob) => {
  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    const response = await api.post('/voice/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Transcribe error:', error);
    throw error;
  }
};

export const synthesizeSpeech = async (text) => {
  try {
    const response = await api.post('/voice/synthesize', 
      { text },
      { responseType: 'blob' }
    );
    return URL.createObjectURL(response.data);
  } catch (error) {
    console.error('TTS error:', error);
    throw error;
  }
};

// Digital Twin API
export const getLatestVitals = async (userId = 'demo_patient') => {
  try {
    const response = await api.get(`/digital-twin/vitals/${userId}/latest`);
    return response.data;
  } catch (error) {
    console.error('Get vitals error:', error);
    return null;
  }
};

export const getVitalsHistory = async (userId = 'demo_patient', days = 30) => {
  try {
    const response = await api.get(`/digital-twin/vitals/${userId}/history?days=${days}`);
    return response.data;
  } catch (error) {
    console.error('Get vitals history error:', error);
    return [];
  }
};

export const getVitalsSummary = async (userId = 'demo_patient') => {
  try {
    const response = await api.get(`/digital-twin/vitals/${userId}/summary`);
    return response.data;
  } catch (error) {
    console.error('Get vitals summary error:', error);
    return null;
  }
};

export const generateMockVitals = async (userId = 'demo_patient', days = 30) => {
  try {
    const response = await api.post(`/digital-twin/vitals/${userId}/generate-mock?days=${days}`);
    return response.data;
  } catch (error) {
    console.error('Generate mock data error:', error);
    throw error;
  }
};

// Admin API
export const getSystemStats = async () => {
  try {
    const response = await api.get('/admin/stats');
    return response.data;
  } catch (error) {
    console.error('Get stats error:', error);
    throw error;
  }
};

export const clearCache = async () => {
  try {
    const response = await api.post('/admin/cache/clear');
    return response.data;
  } catch (error) {
    console.error('Clear cache error:', error);
    throw error;
  }
};

export default api;