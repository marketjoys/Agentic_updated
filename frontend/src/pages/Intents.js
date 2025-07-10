import React, { useState, useEffect } from 'react';
import { Plus, Brain, Edit, Trash2, MessageSquare } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Intents = () => {
  const [intents, setIntents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingIntent, setEditingIntent] = useState(null);

  useEffect(() => {
    loadIntents();
  }, []);

  const loadIntents = async () => {
    try {
      const response = await apiService.getIntents();
      setIntents(response.data);
    } catch (error) {
      toast.error('Failed to load intents');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveIntent = async (intentData) => {
    try {
      if (editingIntent) {
        await apiService.updateIntent(editingIntent.id, intentData);
        toast.success('Intent updated successfully');
      } else {
        await apiService.createIntent(intentData);
        toast.success('Intent created successfully');
      }
      setShowModal(false);
      setEditingIntent(null);
      loadIntents();
    } catch (error) {
      toast.error('Failed to save intent');
    }
  };

  const handleDeleteIntent = async (intentId) => {
    if (!window.confirm('Are you sure you want to delete this intent?')) return;
    
    try {
      await apiService.deleteIntent(intentId);
      toast.success('Intent deleted successfully');
      loadIntents();
    } catch (error) {
      toast.error('Failed to delete intent');
    }
  };

  const handleEditIntent = (intent) => {
    setEditingIntent(intent);
    setShowModal(true);
  };

  const handleNewIntent = () => {
    setEditingIntent(null);
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Intent Management</h1>
          <p className="text-secondary-600 mt-1">
            Configure AI intent classification for automatic responses
          </p>
        </div>
        <button
          onClick={handleNewIntent}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Intent
        </button>
      </div>

      {/* Intent Info */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center mb-3">
            <Brain className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold text-secondary-900">How Intent Classification Works</h3>
          </div>
          <p className="text-sm text-secondary-600 mb-4">
            When an email is received, the AI analyzes the content and classifies it based on the intents you've configured. 
            Each intent should have a clear name and detailed description to help the AI understand when to trigger it.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-secondary-600">Positive Response</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-red-500 rounded-full"></div>
              <span className="text-sm text-secondary-600">Negative Response</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-yellow-500 rounded-full"></div>
              <span className="text-sm text-secondary-600">Question/Inquiry</span>
            </div>
          </div>
        </div>
      </div>

      {/* Intents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {intents.map((intent) => (
          <IntentCard
            key={intent.id}
            intent={intent}
            onEdit={handleEditIntent}
            onDelete={handleDeleteIntent}
          />
        ))}
      </div>

      {/* No Intents Message */}
      {intents.length === 0 && (
        <div className="card">
          <div className="card-body text-center py-12">
            <Brain className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Intents Configured</h3>
            <p className="text-secondary-600 mb-4">
              Create your first intent to enable AI-powered automatic responses
            </p>
            <button
              onClick={handleNewIntent}
              className="btn btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Intent
            </button>
          </div>
        </div>
      )}

      {/* Intent Modal */}
      {showModal && (
        <IntentModal
          intent={editingIntent}
          onClose={() => {
            setShowModal(false);
            setEditingIntent(null);
          }}
          onSave={handleSaveIntent}
        />
      )}
    </div>
  );
};

const IntentCard = ({ intent, onEdit, onDelete }) => {
  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-secondary-900">{intent.name}</h3>
          <div className="flex space-x-1">
            <button
              onClick={() => onEdit(intent)}
              className="p-1 text-secondary-400 hover:text-primary-600"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button className="p-1 text-secondary-400 hover:text-red-600">
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <p className="text-sm text-secondary-600 mb-4">
          {intent.description}
        </p>
        
        {intent.keywords && intent.keywords.length > 0 && (
          <div className="mb-4">
            <p className="text-xs text-secondary-500 mb-2">Keywords:</p>
            <div className="flex flex-wrap gap-1">
              {intent.keywords.slice(0, 3).map((keyword, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded"
                >
                  {keyword}
                </span>
              ))}
              {intent.keywords.length > 3 && (
                <span className="px-2 py-1 bg-secondary-100 text-secondary-600 text-xs rounded">
                  +{intent.keywords.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <div className="text-xs text-secondary-400">
            Created {new Date(intent.created_at).toLocaleDateString()}
          </div>
          <div className="flex items-center space-x-1">
            <MessageSquare className="h-4 w-4 text-secondary-400" />
            <span className="text-xs text-secondary-400">AI Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const IntentModal = ({ intent, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: intent?.name || '',
    description: intent?.description || '',
    keywords: intent?.keywords?.join(', ') || '',
    primary_template_id: intent?.primary_template_id || '',
    fallback_template_id: intent?.fallback_template_id || '',
    auto_respond: intent?.auto_respond || true,
    response_delay_min: intent?.response_delay_min || 5,
    response_delay_max: intent?.response_delay_max || 60,
    confidence_threshold: intent?.confidence_threshold || 0.7,
    escalate_to_human: intent?.escalate_to_human || false
  });

  const [templates, setTemplates] = useState([]);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await apiService.getTemplates();
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const intentData = {
      ...formData,
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k)
    };
    onSave(intentData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const autoResponseTemplates = templates.filter(t => t.type === 'auto_response');

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-3xl w-full p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
            {intent ? 'Edit Intent' : 'Create New Intent'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Intent Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., Positive Response, Not Interested, Request Info"
                  className="input"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Confidence Threshold
                </label>
                <select
                  name="confidence_threshold"
                  value={formData.confidence_threshold}
                  onChange={handleChange}
                  className="input"
                >
                  <option value={0.5}>50% (Low)</option>
                  <option value={0.6}>60% (Medium-Low)</option>
                  <option value={0.7}>70% (Medium)</option>
                  <option value={0.8}>80% (High)</option>
                  <option value={0.9}>90% (Very High)</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe what kind of emails should trigger this intent..."
                rows="3"
                className="input"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Keywords (Optional)
              </label>
              <input
                type="text"
                name="keywords"
                value={formData.keywords}
                onChange={handleChange}
                placeholder="interested, yes, tell me more, not interested, no thanks"
                className="input"
              />
              <p className="text-xs text-secondary-500 mt-1">
                Separate keywords with commas. These help the AI identify this intent.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Primary Template
                </label>
                <select
                  name="primary_template_id"
                  value={formData.primary_template_id}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select primary template</option>
                  {autoResponseTemplates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Fallback Template
                </label>
                <select
                  name="fallback_template_id"
                  value={formData.fallback_template_id}
                  onChange={handleChange}
                  className="input"
                >
                  <option value="">Select fallback template</option>
                  {autoResponseTemplates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Response Delay (Min)
                </label>
                <input
                  type="number"
                  name="response_delay_min"
                  value={formData.response_delay_min}
                  onChange={handleChange}
                  min="1"
                  max="60"
                  className="input"
                />
                <p className="text-xs text-secondary-500 mt-1">Minutes</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Response Delay (Max)
                </label>
                <input
                  type="number"
                  name="response_delay_max"
                  value={formData.response_delay_max}
                  onChange={handleChange}
                  min="1"
                  max="120"
                  className="input"
                />
                <p className="text-xs text-secondary-500 mt-1">Minutes</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  name="auto_respond"
                  checked={formData.auto_respond}
                  onChange={handleChange}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-secondary-700">Auto-respond to this intent</span>
              </label>
              
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  name="escalate_to_human"
                  checked={formData.escalate_to_human}
                  onChange={handleChange}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-secondary-700">Escalate to human</span>
              </label>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
              >
                {intent ? 'Update' : 'Create'} Intent
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Intents;