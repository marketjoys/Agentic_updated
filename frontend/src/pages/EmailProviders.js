import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Settings, CheckCircle, XCircle, AlertCircle, Mail, Server, Edit, Trash2, TestTube, Eye, EyeOff, Wifi, WifiOff } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useEscapeKey from '../hooks/useEscapeKey';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Modal Component - Moved outside to prevent re-creation on parent re-renders
const ProviderModal = React.memo(({ 
  show, 
  onClose, 
  onSubmit, 
  title, 
  provider = null,
  formData,
  handleInputChange
}) => {
  // Add escape key functionality
  useEscapeKey(onClose, show);
  
  // Handle background click to close modal
  const handleBackdropClick = useCallback((e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }, [onClose]);

  // Prevent backdrop click from interfering with form interactions
  const handleModalClick = useCallback((e) => {
    e.stopPropagation();
  }, []);

  // Handle form submission
  const handleFormSubmit = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    onSubmit(e);
  }, [onSubmit]);

  if (!show) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={handleBackdropClick}
    >
      <div 
        className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={handleModalClick}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
            type="button"
          >
            <XCircle className="w-6 h-6" />
          </button>
        </div>
        
        <form onSubmit={handleFormSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Provider Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={handleInputChange('name')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                placeholder="Enter provider name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Provider Type</label>
              <select
                value={formData.provider_type}
                onChange={handleInputChange('provider_type')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="gmail">Gmail</option>
                <option value="outlook">Outlook</option>
                <option value="yahoo">Yahoo</option>
                <option value="custom_smtp">Custom SMTP</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Email Address</label>
              <input
                type="email"
                value={formData.email_address}
                onChange={handleInputChange('email_address')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Display Name</label>
              <input
                type="text"
                value={formData.display_name}
                onChange={handleInputChange('display_name')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold mb-3">SMTP Settings</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">SMTP Host</label>
                <input
                  type="text"
                  value={formData.smtp_host}
                  onChange={handleInputChange('smtp_host')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">SMTP Port</label>
                <input
                  type="number"
                  value={formData.smtp_port}
                  onChange={handleInputChange('smtp_port')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-sm font-medium mb-1">SMTP Username</label>
                <input
                  type="text"
                  value={formData.smtp_username}
                  onChange={handleInputChange('smtp_username')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">SMTP Password</label>
                <input
                  type="password"
                  value={formData.smtp_password}
                  onChange={handleInputChange('smtp_password')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>

            <div className="mt-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.smtp_use_tls}
                  onChange={handleInputChange('smtp_use_tls')}
                  className="mr-2"
                />
                Use TLS
              </label>
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold mb-3">IMAP Settings (Optional)</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">IMAP Host</label>
                <input
                  type="text"
                  value={formData.imap_host}
                  onChange={handleInputChange('imap_host')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., imap.gmail.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">IMAP Port</label>
                <input
                  type="number"
                  value={formData.imap_port}
                  onChange={handleInputChange('imap_port')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="993"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-sm font-medium mb-1">IMAP Username</label>
                <input
                  type="text"
                  value={formData.imap_username}
                  onChange={handleInputChange('imap_username')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Usually same as email"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">IMAP Password</label>
                <input
                  type="password"
                  value={formData.imap_password}
                  onChange={handleInputChange('imap_password')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Usually same as SMTP password"
                />
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold mb-3">Rate Limits</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Daily Send Limit</label>
                <input
                  type="number"
                  value={formData.daily_send_limit}
                  onChange={handleInputChange('daily_send_limit')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  min="1"
                  max="2000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Hourly Send Limit</label>
                <input
                  type="number"
                  value={formData.hourly_send_limit}
                  onChange={handleInputChange('hourly_send_limit')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  min="1"
                  max="200"
                />
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_default}
                onChange={handleInputChange('is_default')}
                className="mr-2"
              />
              Set as default provider
            </label>
            
            <label className="flex items-center mt-3">
              <input
                type="checkbox"
                checked={formData.skip_connection_test}
                onChange={handleInputChange('skip_connection_test')}
                className="mr-2"
              />
              Skip connection test (for demo/test purposes)
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {provider ? 'Update' : 'Add'} Provider
            </button>
          </div>
        </form>
      </div>
    </div>
  );
});

const EmailProviders = () => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [testingProvider, setTestingProvider] = useState(null);
  const [togglingImap, setTogglingImap] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    provider_type: 'gmail',
    email_address: '',
    display_name: '',
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_use_tls: true,
    imap_host: '',
    imap_port: 993,
    imap_username: '',
    imap_password: '',
    daily_send_limit: 500,
    hourly_send_limit: 50,
    is_default: false,
    skip_connection_test: false
  });

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/email-providers`);
      setProviders(response.data);
    } catch (error) {
      console.error('Error fetching providers:', error);
      toast.error('Failed to load email providers');
    } finally {
      setLoading(false);
    }
  };

  const handleAddProvider = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${BACKEND_URL}/api/email-providers`, formData);
      toast.success('Email provider added successfully');
      setShowAddModal(false);
      resetForm();
      fetchProviders();
    } catch (error) {
      console.error('Error adding provider:', error);
      toast.error('Failed to add email provider');
    }
  };

  const handleEditProvider = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${BACKEND_URL}/api/email-providers/${selectedProvider.id}`, formData);
      toast.success('Email provider updated successfully');
      setShowEditModal(false);
      setSelectedProvider(null);
      resetForm();
      fetchProviders();
    } catch (error) {
      console.error('Error updating provider:', error);
      toast.error('Failed to update email provider');
    }
  };

  const handleDeleteProvider = async (providerId) => {
    if (window.confirm('Are you sure you want to delete this email provider?')) {
      try {
        await axios.delete(`${BACKEND_URL}/api/email-providers/${providerId}`);
        toast.success('Email provider deleted successfully');
        fetchProviders();
      } catch (error) {
        console.error('Error deleting provider:', error);
        toast.error('Failed to delete email provider');
      }
    }
  };

  const handleTestConnection = async (providerId) => {
    setTestingProvider(providerId);
    try {
      await axios.post(`${BACKEND_URL}/api/email-providers/${providerId}/test`);
      toast.success('Connection test successful');
    } catch (error) {
      console.error('Error testing connection:', error);
      toast.error('Connection test failed');
    } finally {
      setTestingProvider(null);
    }
  };

  const handleSetDefault = async (providerId) => {
    try {
      await axios.post(`${BACKEND_URL}/api/email-providers/${providerId}/set-default`);
      toast.success('Default provider updated');
      fetchProviders();
    } catch (error) {
      console.error('Error setting default provider:', error);
      toast.error('Failed to set default provider');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      provider_type: 'gmail',
      email_address: '',
      display_name: '',
      smtp_host: '',
      smtp_port: 587,
      smtp_username: '',
      smtp_password: '',
      smtp_use_tls: true,
      imap_host: '',
      imap_port: 993,
      imap_username: '',
      imap_password: '',
      daily_send_limit: 500,
      hourly_send_limit: 50,
      is_default: false,
      skip_connection_test: false
    });
  };

  const openEditModal = (provider) => {
    setSelectedProvider(provider);
    setFormData({
      name: provider.name || '',
      provider_type: provider.provider_type || 'gmail',
      email_address: provider.email_address || '',
      display_name: provider.display_name || '',
      smtp_host: provider.smtp_host || '',
      smtp_port: provider.smtp_port || 587,
      smtp_username: provider.smtp_username || '',
      smtp_password: provider.smtp_password || '',
      smtp_use_tls: provider.smtp_use_tls !== undefined ? provider.smtp_use_tls : true,
      imap_host: provider.imap_host || '',
      imap_port: provider.imap_port || 993,
      imap_username: provider.imap_username || '',
      imap_password: provider.imap_password || '',
      daily_send_limit: provider.daily_send_limit || 500,
      hourly_send_limit: provider.hourly_send_limit || 50,
      is_default: provider.is_default || false,
      skip_connection_test: provider.skip_connection_test || false
    });
    setShowEditModal(true);
  };

  const getProviderIcon = (type) => {
    switch (type) {
      case 'gmail':
        return <Mail className="w-5 h-5 text-red-500" />;
      case 'outlook':
        return <Mail className="w-5 h-5 text-blue-500" />;
      case 'yahoo':
        return <Mail className="w-5 h-5 text-purple-500" />;
      default:
        return <Server className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (isActive) => {
    return isActive ? 
      <CheckCircle className="w-5 h-5 text-green-500" /> : 
      <XCircle className="w-5 h-5 text-red-500" />;
  };

  // Handle form input changes with better event handling
  const handleInputChange = useCallback((field) => (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const value = e.target.type === 'checkbox' ? e.target.checked : 
                  e.target.type === 'number' ? (parseInt(e.target.value) || 0) : 
                  e.target.value;
    
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Toggle IMAP monitoring for a provider
  const handleToggleImap = async (providerId) => {
    try {
      setTogglingImap(providerId);
      const response = await axios.put(`${BACKEND_URL}/api/email-providers/${providerId}/toggle-imap`);
      
      if (response.data) {
        toast.success(response.data.message);
        // Update the provider in the local state
        setProviders(prev => prev.map(p => 
          p.id === providerId ? { ...p, imap_enabled: response.data.imap_enabled } : p
        ));
      }
    } catch (error) {
      console.error('Error toggling IMAP:', error);
      toast.error(error.response?.data?.detail || 'Failed to toggle IMAP monitoring');
    } finally {
      setTogglingImap(null);
    }
  };

  // Check IMAP status for a provider
  const checkImapStatus = async (providerId) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/email-providers/${providerId}/imap-status`);
      return response.data;
    } catch (error) {
      console.error('Error checking IMAP status:', error);
      return null;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email Providers</h1>
          <p className="text-gray-600">Manage your email sending and receiving providers</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Add Provider</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {providers.map((provider) => (
          <div key={provider.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {getProviderIcon(provider.provider_type)}
                <div>
                  <h3 className="font-semibold text-gray-900">{provider.name}</h3>
                  <p className="text-sm text-gray-600">{provider.email_address}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {provider.is_default && (
                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                    Default
                  </span>
                )}
                {getStatusIcon(provider.is_active)}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
              <div>
                <p className="text-gray-500">Type</p>
                <p className="font-medium capitalize">{provider.provider_type.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-gray-500">Daily Limit</p>
                <p className="font-medium">{provider.current_daily_count || 0}/{provider.daily_send_limit}</p>
              </div>
              <div>
                <p className="text-gray-500">Hourly Limit</p>
                <p className="font-medium">{provider.current_hourly_count || 0}/{provider.hourly_send_limit}</p>
              </div>
              <div>
                <p className="text-gray-500">IMAP Status</p>
                <div className="flex items-center space-x-1">
                  {provider.imap_enabled ? (
                    <Wifi className="w-4 h-4 text-green-500" />
                  ) : (
                    <WifiOff className="w-4 h-4 text-gray-400" />
                  )}
                  <p className="font-medium">
                    {provider.imap_enabled ? 'Enabled' : 'Disabled'}
                  </p>
                </div>
              </div>
            </div>

            {/* IMAP Toggle Section */}
            {provider.imap_host && provider.imap_username && (
              <div className="border-t pt-3 mb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">IMAP Monitoring</span>
                    {provider.imap_enabled && (
                      <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleToggleImap(provider.id)}
                    disabled={togglingImap === provider.id}
                    className={`px-3 py-1 text-sm rounded-md transition-colors ${
                      provider.imap_enabled
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    } disabled:opacity-50`}
                  >
                    {togglingImap === provider.id ? (
                      'Toggling...'
                    ) : (
                      provider.imap_enabled ? 'Disable' : 'Enable'
                    )}
                  </button>
                </div>
                {provider.imap_enabled && (
                  <p className="text-xs text-gray-500 mt-1">
                    Monitoring emails on {provider.imap_host}:{provider.imap_port || 993}
                  </p>
                )}
              </div>
            )}

            <div className="flex space-x-2">
              <button
                onClick={() => handleTestConnection(provider.id)}
                disabled={testingProvider === provider.id}
                className="flex-1 bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-1"
              >
                <TestTube className="w-4 h-4" />
                <span>{testingProvider === provider.id ? 'Testing...' : 'Test'}</span>
              </button>
              
              <button
                onClick={() => openEditModal(provider)}
                className="bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 flex items-center justify-center"
              >
                <Edit className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleDeleteProvider(provider.id)}
                className="bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 flex items-center justify-center"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              
              {!provider.is_default && (
                <button
                  onClick={() => handleSetDefault(provider.id)}
                  className="bg-gray-600 text-white py-2 px-3 rounded-md hover:bg-gray-700 flex items-center justify-center"
                >
                  <Settings className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {providers.length === 0 && (
        <div className="text-center py-12">
          <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No email providers configured</h3>
          <p className="text-gray-600 mb-4">Add your first email provider to start sending emails</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Add Your First Provider
          </button>
        </div>
      )}

      <ProviderModal
        show={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddProvider}
        title="Add Email Provider"
        formData={formData}
        handleInputChange={handleInputChange}
      />

      <ProviderModal
        show={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSubmit={handleEditProvider}
        title="Edit Email Provider"
        provider={selectedProvider}
        formData={formData}
        handleInputChange={handleInputChange}
      />
    </div>
  );
};

export default EmailProviders;