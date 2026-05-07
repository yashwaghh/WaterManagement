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

const isDev = process.env.NODE_ENV !== 'production';

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    if (isDev) console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    if (isDev) console.log(`API Response: ${response.status}`, response.data);
    return response;
  },
  (error) => {
    if (isDev) console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);

// Apply the same logging interceptors to adminClient
adminClient.interceptors.request.use(
  (config) => {
    if (isDev) console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

adminClient.interceptors.response.use(
  (response) => {
    if (isDev) console.log(`API Response: ${response.status}`, response.data);
    return response;
  },
  (error) => {
    if (isDev) console.error('API Error:', error.message);
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
  getReports: (flatId) => apiClient.get(`/reports/${flatId}`),
  getReportForDay: (flatId, day) => apiClient.get(`/reports/${flatId}/day/${day}`),
  getWeeklyReport: (flatId, startDay = 1, endDay = 7) =>
    apiClient.get(`/reports/${flatId}/weekly?start_day=${startDay}&end_day=${endDay}`),

  // PDF Download URLs (direct browser download — not axios)
  getDailyPdfUrl: (flatId, day) => `${API_BASE_URL}/reports/${flatId}/pdf/daily/${day}`,
  getWeeklyPdfUrl: (flatId, startDay = 1, endDay = 7) =>
    `${API_BASE_URL}/reports/${flatId}/pdf/weekly?start_day=${startDay}&end_day=${endDay}`,
  getMonthlyPdfUrl: (flatId, startDay = 1, endDay = 30) =>
    `${API_BASE_URL}/reports/${flatId}/pdf/monthly?start_day=${startDay}&end_day=${endDay}`,

  // Alerts
  getAlerts: () => apiClient.get('/alerts'),

  // Admin Controls (require Authorization header)
  resetDay: () => adminClient.post('/admin/reset-day'),
  resetWeek: () => adminClient.post('/admin/reset-week'),
  toggleSimulation: () => adminClient.post('/admin/toggle-simulation'),
  getAdminState: () => adminClient.get('/admin/state'),

  // Points & Store
  getPoints: (flatId) => apiClient.get(`/points/${flatId}`),
  redeemPoints: (flatId, itemId, itemTitle, pointsCost) =>
    apiClient.post('/redeem', { flat_id: flatId, item_id: itemId, item_title: itemTitle, points_cost: pointsCost }),
};

export default apiService;
