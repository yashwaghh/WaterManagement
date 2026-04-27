import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const ADMIN_SECRET = process.env.REACT_APP_ADMIN_SECRET || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Admin axios client — attaches Bearer token for protected endpoints
const adminClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    ...(ADMIN_SECRET ? { Authorization: `Bearer ${ADMIN_SECRET}` } : {}),
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

// Apply the same logging interceptors to adminClient
adminClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

adminClient.interceptors.response.use(
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
  getHistory: (flatId, limit = 50) => apiClient.get(`/history/${flatId}?limit=${limit}`),

  // Alerts
  getAlerts: () => apiClient.get('/alerts'),

  // Admin Controls (require Authorization header)
  resetDay: () => adminClient.post('/admin/reset-day'),
  resetWeek: () => adminClient.post('/admin/reset-week'),
  toggleSimulation: () => adminClient.post('/admin/toggle-simulation'),
  getAdminState: () => adminClient.get('/admin/state'),
};

export default apiService;
