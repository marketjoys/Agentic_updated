import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
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
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
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
  sendCampaign: (id) => api.post(`/api/campaigns/${id}/send`),

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
};

export default api;