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
      await apiService.createIntent(intentData);
      toast.success('Intent created successfully');
      setShowModal(false);
      setEditingIntent(null);
      loadIntents();
    } catch (error) {
      toast.error('Failed to save intent');
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

const IntentCard = ({ intent, onEdit }) => {
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
    response_template: intent?.response_template || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const intentData = {
      ...formData,
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k)
    };
    onSave(intentData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-2xl w-full p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
            {intent ? 'Edit Intent' : 'Create New Intent'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
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
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Response Template (Optional)
              </label>
              <textarea
                name="response_template"
                value={formData.response_template}
                onChange={handleChange}
                placeholder="Template for automatic responses when this intent is detected..."
                rows="4"
                className="input"
              />
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