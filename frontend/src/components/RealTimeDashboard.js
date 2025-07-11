import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Wifi, WifiOff, Users, Mail, Target, AlertCircle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const RealTimeDashboard = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');
  const [lastUpdate, setLastUpdate] = useState(null);
  const [usePolling, setUsePolling] = useState(false);
  const [loading, setLoading] = useState(false);

  // Initialize connection (WebSocket first, fallback to polling)
  useEffect(() => {
    const initializeConnection = async () => {
      try {
        // First try WebSocket
        await connectWebSocket();
      } catch (error) {
        console.log('WebSocket failed, falling back to polling');
        setUsePolling(true);
        await startPolling();
      }
    };

    initializeConnection();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  // Polling fallback when WebSocket fails
  useEffect(() => {
    if (usePolling) {
      const interval = setInterval(async () => {
        await fetchMetrics();
      }, 5000); // Poll every 5 seconds

      return () => clearInterval(interval);
    }
  }, [usePolling]);

  const fetchMetrics = async () => {
    try {
      const response = await apiService.get('/api/real-time/dashboard-metrics');
      setMetrics(response.data.metrics);
      setLastUpdate(new Date());
      setIsConnected(true);
      setConnectionStatus('Connected (Polling)');
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setIsConnected(false);
      setConnectionStatus('Disconnected');
    }
  };

  const connectWebSocket = async () => {
    return new Promise((resolve, reject) => {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      // Construct WebSocket URL based on backend URL
      let wsUrl;
      if (backendUrl.startsWith('https://')) {
        wsUrl = backendUrl.replace('https://', 'wss://');
      } else if (backendUrl.startsWith('http://')) {
        wsUrl = backendUrl.replace('http://', 'ws://');
      } else {
        wsUrl = `ws://${backendUrl}`;
      }
      
      const clientId = `dashboard-${Date.now()}`;
      
      try {
        const ws = new WebSocket(`${wsUrl}/api/ws/${clientId}`);
        
        ws.onopen = () => {
          console.log('WebSocket Connected');
          setIsConnected(true);
          setConnectionStatus('Connected (WebSocket)');
          setWebsocket(ws);
          setUsePolling(false);
          
          // Subscribe to events
          ws.send(JSON.stringify({
            type: 'subscribe',
            event_types: ['dashboard_metrics', 'notifications', 'campaign_progress', 'provider_status']
          }));
          
          // Request current metrics
          ws.send(JSON.stringify({
            type: 'get_current_metrics'
          }));
          
          resolve(ws);
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        ws.onclose = () => {
          console.log('WebSocket Disconnected');
          setIsConnected(false);
          setConnectionStatus('Disconnected');
          setWebsocket(null);
          
          // Fallback to polling
          setUsePolling(true);
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket Error:', error);
          setConnectionStatus('Error');
          reject(error);
        };
        
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        setConnectionStatus('Failed to connect');
        reject(error);
      }
    });
  };

  const startPolling = async () => {
    setConnectionStatus('Connecting (Polling)...');
    await fetchMetrics();
  };

  const handleWebSocketMessage = useCallback((data) => {
    switch (data.type) {
      case 'metrics_update':
      case 'current_metrics':
        setMetrics(data.data);
        setLastUpdate(new Date(data.timestamp));
        break;
        
      case 'notifications':
        setNotifications(prev => [...prev, ...data.data]);
        break;
        
      case 'notification':
        setNotifications(prev => [...prev, data.data]);
        break;
        
      case 'campaign_progress':
        console.log('Campaign progress:', data);
        break;
        
      case 'provider_status':
        console.log('Provider status:', data);
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      if (usePolling) {
        await fetchMetrics();
      } else {
        // Try to reconnect WebSocket
        await connectWebSocket();
      }
      toast.success('Dashboard refreshed successfully');
    } catch (error) {
      toast.error('Failed to refresh dashboard');
    } finally {
      setLoading(false);
    }
  };

  const dismissNotification = (index) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Real-Time Dashboard</h1>
        <div className="flex items-center gap-4">
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi className="w-5 h-5 text-green-500" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-500" />
            )}
            <span className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {connectionStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="space-y-2">
          {notifications.slice(-5).map((notification, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border-l-4 ${
                notification.type === 'error' ? 'border-red-500 bg-red-50' :
                notification.type === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                'border-blue-500 bg-blue-50'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium text-gray-900">{notification.title}</h4>
                  <p className="text-sm text-gray-600">{notification.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(notification.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                <button
                  onClick={() => dismissNotification(index)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Prospects</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(metrics.overview?.total_prospects || 0)}
                </p>
              </div>
              <Users className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(metrics.overview?.active_campaigns || 0)}
                </p>
              </div>
              <Target className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Emails Today</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(metrics.overview?.emails_today || 0)}
                </p>
              </div>
              <Mail className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Emails</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(metrics.overview?.total_emails_sent || 0)}
                </p>
              </div>
              <Activity className="w-8 h-8 text-indigo-500" />
            </div>
          </div>
        </div>
      )}

      {/* Provider Status */}
      {metrics && metrics.provider_stats && Object.keys(metrics.provider_stats).length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Email Provider Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(metrics.provider_stats).map(([name, provider]) => (
              <div key={name} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{name}</h4>
                  {getStatusIcon(provider.status)}
                </div>
                <p className="text-sm text-gray-600">Type: {provider.type}</p>
                <p className="text-sm text-gray-600">
                  Usage: {provider.emails_sent_today || 0} / {provider.daily_limit || 'Unlimited'}
                </p>
                {provider.daily_limit && (
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${Math.min(100, (provider.emails_sent_today / provider.daily_limit) * 100)}%`
                      }}
                    ></div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {metrics && metrics.recent_activity && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {metrics.recent_activity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.subject}</p>
                  <p className="text-xs text-gray-500">To: {activity.recipient}</p>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(activity.status)}
                  <span className="text-xs text-gray-500">
                    {activity.created_at ? new Date(activity.created_at).toLocaleTimeString() : 'Unknown'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Update */}
      {lastUpdate && (
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
      )}

      {/* No Data Message */}
      {!metrics && (
        <div className="text-center py-12">
          <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Loading Dashboard</h3>
          <p className="text-gray-600">Connecting to real-time data...</p>
        </div>
      )}
    </div>
  );
};

export default RealTimeDashboard;