import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging and auth
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    
    // Add auth token to all requests
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // If we get a 401 error, try to refresh the token
    if (error.response?.status === 401) {
      console.log('Received 401 error, attempting token refresh...');
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const refreshResponse = await axios.post(`${API_BASE_URL}/api/auth/refresh`);
          const { access_token } = refreshResponse.data;
          
          localStorage.setItem('token', access_token);
          
          // Retry the original request with the new token
          const originalRequest = error.config;
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
          
          return axios(originalRequest);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          localStorage.removeItem('token');
          window.location.href = '/'; // Redirect to login
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const apiService = {
  // Health check
  healthCheck: () => api.get('/api/health'),

  // Prospects
  getProspects: (skip = 0, limit = 100) => 
    api.get(`/api/prospects?skip=${skip}&limit=${limit}`),
  createProspect: (prospect) => api.post('/api/prospects', prospect),
  uploadProspects: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/prospects/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Templates
  getTemplates: () => api.get('/api/templates'),
  createTemplate: (template) => api.post('/api/templates', template),
  getTemplate: (id) => api.get(`/api/templates/${id}`),
  updateTemplate: (id, template) => api.put(`/api/templates/${id}`, template),

  // Campaigns
  getCampaigns: () => api.get('/api/campaigns'),
  createCampaign: (campaign) => api.post('/api/campaigns', campaign),
  getCampaign: (id) => api.get(`/api/campaigns/${id}`),
  sendCampaign: (id, sendRequest = {}) => {
    console.log('📡 sendCampaign called with id:', id, 'sendRequest:', sendRequest);
    
    // Default send request parameters
    const defaultSendRequest = {
      send_immediately: true,
      email_provider_id: "",
      max_emails: 1000,
      schedule_type: "immediate",
      start_time: null,
      follow_up_enabled: true,
      follow_up_intervals: [3, 7, 14],
      follow_up_templates: []
    };
    
    // Merge with provided parameters
    const finalSendRequest = { ...defaultSendRequest, ...sendRequest };
    
    console.log('📤 Final send request:', finalSendRequest);
    console.log('🎯 Making POST request to:', `/api/campaigns/${id}/send`);
    
    return api.post(`/api/campaigns/${id}/send`, finalSendRequest);
  },

  // Intents
  getIntents: () => api.get('/api/intents'),
  createIntent: (intent) => api.post('/api/intents', intent),
  getIntent: (id) => api.get(`/api/intents/${id}`),
  updateIntent: (id, intent) => api.put(`/api/intents/${id}`, intent),
  deleteIntent: (id) => api.delete(`/api/intents/${id}`),

  // Analytics
  getCampaignAnalytics: (campaignId) => api.get(`/api/analytics/campaign/${campaignId}`),

  // Prospect Lists
  getLists: () => api.get('/api/lists'),
  createList: (list) => api.post('/api/lists', list),
  getList: (id) => api.get(`/api/lists/${id}`),
  updateList: (id, list) => api.put(`/api/lists/${id}`, list),
  deleteList: (id) => api.delete(`/api/lists/${id}`),
  addProspectsToList: (listId, prospectIds) => api.post(`/api/lists/${listId}/prospects`, prospectIds),
  removeProspectsFromList: (listId, prospectIds) => api.delete(`/api/lists/${listId}/prospects`, { data: prospectIds }),

  // Email Processing
  startEmailProcessing: () => api.post('/api/email-processing/start'),
  stopEmailProcessing: () => api.post('/api/email-processing/stop'),
  getProcessingStatus: () => api.get('/api/email-processing/status'),
  getProcessingAnalytics: () => api.get('/api/email-processing/analytics'),
  testIntentClassification: (data) => api.post('/api/email-processing/test-classification', data),
  testResponseGeneration: (data) => api.post('/api/email-processing/test-response', data),

  // Threads
  getThreads: () => api.get('/api/threads'),
  getThread: (id) => api.get(`/api/threads/${id}`),
  getThreadByProspect: (prospectId) => api.get(`/api/threads/prospect/${prospectId}`),
  addMessageToThread: (threadId, messageData) => api.post(`/api/threads/${threadId}/messages`, messageData),

  // Email Providers
  getEmailProviders: () => api.get('/api/email-providers'),
  createEmailProvider: (provider) => api.post('/api/email-providers', provider),
  updateEmailProvider: (id, provider) => api.put(`/api/email-providers/${id}`, provider),
  deleteEmailProvider: (id) => api.delete(`/api/email-providers/${id}`),
  setDefaultEmailProvider: (id) => api.post(`/api/email-providers/${id}/set-default`),
  testEmailProvider: (id) => api.post(`/api/email-providers/${id}/test-connection`),

  // Follow-up Monitoring
  getFollowUpDashboard: () => api.get('/api/follow-up-monitoring/dashboard'),
  getImapLogs: (hours = 24) => api.get(`/api/follow-up-monitoring/imap-logs?hours=${hours}`),
  getProspectResponses: (days = 7) => api.get(`/api/follow-up-monitoring/prospect-responses?days=${days}`),
  analyzeProspectThread: (prospectId) => api.get(`/api/follow-up-monitoring/thread-analysis/${prospectId}`),
  forceStopFollowUp: (prospectId) => api.post(`/api/follow-up-monitoring/force-stop-follow-up/${prospectId}`),
  restartFollowUp: (prospectId) => api.post(`/api/follow-up-monitoring/restart-follow-up/${prospectId}`),
  getFollowUpHealthCheck: () => api.get('/api/follow-up-monitoring/health-check'),

  // Smart Follow-up Engine
  startFollowUpEngine: () => api.post('/api/follow-up-engine/start'),
  stopFollowUpEngine: () => api.post('/api/follow-up-engine/stop'),
  getFollowUpEngineStatus: () => api.get('/api/follow-up-engine/status'),
  getFollowUpStatistics: () => api.get('/api/follow-up-engine/statistics'),
  processEmailResponse: (responseData) => api.post('/api/follow-up-engine/process-response', responseData),
};

export default api;