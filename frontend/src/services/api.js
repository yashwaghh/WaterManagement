import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status}`, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health
  checkHealth: () => apiClient.get('/health'),

  // Config
  getConfig: () => apiClient.get('/config'),

  // Leaderboard & Rankings
  getLeaderboard: () => apiClient.get('/leaderboard'),
  getWeeklySummary: () => apiClient.get('/weekly-summary'),
  getFlats: () => apiClient.get('/flats'),

  // Analytics
  getAnalytics: (flatId) => apiClient.get(`/analytics/${flatId}`),

  // Admin Controls
  resetDay: () => apiClient.post('/admin/reset-day'),
  resetWeek: () => apiClient.post('/admin/reset-week'),
  toggleSimulation: () => apiClient.post('/admin/toggle-simulation'),
  getAdminState: () => apiClient.get('/admin/state'),
};

export default apiService;
