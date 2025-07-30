import React, { useState, useEffect } from 'react';
import { Plus, Settings, Edit, Trash2, Play, Star, Code, TestTube } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import useEscapeKey from '../hooks/useEscapeKey';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const SystemPrompts = () => {
  const [prompts, setPrompts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [testInput, setTestInput] = useState('');
  const [testResult, setTestResult] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    prompt_text: '',
    prompt_type: 'general',
    temperature: 0.7,
    max_tokens: 1000,
    is_active: true,
    is_default: false
  });

  const promptTypes = [
    { value: 'general', label: 'General AI Behavior' },
    { value: 'intent_classification', label: 'Intent Classification' },
    { value: 'response_generation', label: 'Response Generation' },
    { value: 'response_verification', label: 'Response Verification' },
    { value: 'personalization', label: 'Personalization' }
  ];

  const defaultPrompts = {
    general: `You are a professional AI assistant that helps with email communication. Always be:
- Professional and courteous
- Clear and concise
- Helpful and informative
- Respectful of the recipient's time`,
    
    intent_classification: `You are an expert email intent classifier. Your job is to analyze incoming emails and classify them into specific intents.

Guidelines:
- Analyze the email content and subject line carefully
- Look for multiple intents in a single email
- Assign confidence scores based on clarity of intent
- Consider context and tone
- Return results in valid JSON format`,
    
    response_generation: `You are an expert email response generator. Create professional, personalized responses that:
- Address all points mentioned in the original email
- Use appropriate tone and style
- Include relevant personalization
- Maintain conversation context
- End with appropriate call-to-action`,
    
    response_verification: `You are a quality assurance expert for email responses. Evaluate responses for:
- Accuracy and relevance
- Professional tone
- Appropriate personalization
- Context alignment
- Overall quality and effectiveness`,
    
    personalization: `You are a personalization expert. Enhance email content by:
- Using prospect's name and company appropriately
- Adding relevant industry insights
- Incorporating job-title specific language
- Including location-based references when relevant
- Making content more compelling and targeted`
  };

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/system-prompts`);
      setPrompts(response.data);
    } catch (error) {
      console.error('Error fetching prompts:', error);
      toast.error('Failed to load system prompts');
    } finally {
      setLoading(false);
    }
  };

  const handleAddPrompt = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${BACKEND_URL}/api/system-prompts`, formData);
      toast.success('System prompt added successfully');
      setShowAddModal(false);
      resetForm();
      fetchPrompts();
    } catch (error) {
      console.error('Error adding prompt:', error);
      toast.error('Failed to add system prompt');
    }
  };

  const handleEditPrompt = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${BACKEND_URL}/api/system-prompts/${selectedPrompt.id}`, formData);
      toast.success('System prompt updated successfully');
      setShowEditModal(false);
      setSelectedPrompt(null);
      resetForm();
      fetchPrompts();
    } catch (error) {
      console.error('Error updating prompt:', error);
      toast.error('Failed to update system prompt');
    }
  };

  const handleDeletePrompt = async (promptId) => {
    if (window.confirm('Are you sure you want to delete this system prompt?')) {
      try {
        await axios.delete(`${BACKEND_URL}/api/system-prompts/${promptId}`);
        toast.success('System prompt deleted successfully');
        fetchPrompts();
      } catch (error) {
        console.error('Error deleting prompt:', error);
        toast.error('Failed to delete system prompt');
      }
    }
  };

  const handleTestPrompt = async () => {
    if (!testInput.trim()) {
      toast.error('Please enter test input');
      return;
    }

    setTestLoading(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/api/system-prompts/${selectedPrompt.id}/test`, {
        input: testInput,
        temperature: selectedPrompt.temperature,
        max_tokens: selectedPrompt.max_tokens
      });
      setTestResult(response.data.result);
    } catch (error) {
      console.error('Error testing prompt:', error);
      toast.error('Failed to test prompt');
      setTestResult('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setTestLoading(false);
    }
  };

  const handleSetDefault = async (promptId, promptType) => {
    try {
      await axios.post(`${BACKEND_URL}/api/system-prompts/${promptId}/set-default`);
      toast.success(`Default ${promptType} prompt updated`);
      fetchPrompts();
    } catch (error) {
      console.error('Error setting default prompt:', error);
      toast.error('Failed to set default prompt');
    }
  };

  const handleCreateDefaults = async () => {
    try {
      await axios.post(`${BACKEND_URL}/api/system-prompts/create-defaults`);
      toast.success('Default prompts created successfully');
      fetchPrompts();
    } catch (error) {
      console.error('Error creating defaults:', error);
      toast.error('Failed to create default prompts');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      prompt_text: '',
      prompt_type: 'general',
      temperature: 0.7,
      max_tokens: 1000,
      is_active: true,
      is_default: false
    });
  };

  const openEditModal = (prompt) => {
    setSelectedPrompt(prompt);
    setFormData({
      name: prompt.name,
      description: prompt.description,
      prompt_text: prompt.prompt_text,
      prompt_type: prompt.prompt_type,
      temperature: prompt.temperature,
      max_tokens: prompt.max_tokens,
      is_active: prompt.is_active,
      is_default: prompt.is_default
    });
    setShowEditModal(true);
  };

  const openTestModal = (prompt) => {
    setSelectedPrompt(prompt);
    setTestInput('');
    setTestResult('');
    setShowTestModal(true);
  };

  const loadDefaultPrompt = (type) => {
    setFormData({
      ...formData,
      prompt_text: defaultPrompts[type] || '',
      name: formData.name || `Default ${promptTypes.find(t => t.value === type)?.label}`,
      description: formData.description || `Default system prompt for ${type}`
    });
  };

  const PromptModal = ({ show, onClose, onSubmit, title, isEdit = false }) => {
    // Add escape key functionality
    useEscapeKey(onClose, show);
    
    if (!show) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-md"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Prompt Type</label>
                <select
                  value={formData.prompt_type}
                  onChange={(e) => {
                    setFormData({...formData, prompt_type: e.target.value});
                  }}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  {promptTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="block text-sm font-medium">Prompt Text</label>
                <button
                  type="button"
                  onClick={() => loadDefaultPrompt(formData.prompt_type)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Load Default Template
                </button>
              </div>
              <textarea
                value={formData.prompt_text}
                onChange={(e) => setFormData({...formData, prompt_text: e.target.value})}
                onKeyDown={(e) => {
                  // Allow typing and prevent modal close on Escape when editing
                  if (e.key === 'Escape') {
                    e.stopPropagation();
                  }
                }}
                rows={12}
                className="w-full px-3 py-2 border rounded-md font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="Enter your system prompt here..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Temperature</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                  value={formData.temperature}
                  onChange={(e) => setFormData({...formData, temperature: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 border rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">Higher values = more creative, lower = more deterministic</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Max Tokens</label>
                <input
                  type="number"
                  min="50"
                  max="4000"
                  value={formData.max_tokens}
                  onChange={(e) => setFormData({...formData, max_tokens: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">Maximum response length</p>
              </div>
            </div>

            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="mr-2"
                />
                Active
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_default}
                  onChange={(e) => setFormData({...formData, is_default: e.target.checked})}
                  className="mr-2"
                />
                Set as default for this type
              </label>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {isEdit ? 'Update' : 'Add'} Prompt
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const TestModal = ({ show, onClose, prompt }) => {
    // Add escape key functionality
    useEscapeKey(onClose, show);
    
    if (!show || !prompt) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Test Prompt: {prompt.name}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Test Input</label>
              <textarea
                value={testInput}
                onChange={(e) => setTestInput(e.target.value)}
                onKeyDown={(e) => {
                  // Allow typing and prevent modal close on Escape when editing
                  if (e.key === 'Escape') {
                    e.stopPropagation();
                  }
                }}
                rows={4}
                className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your test input here..."
              />
            </div>

            <div>
              <button
                onClick={handleTestPrompt}
                disabled={testLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>{testLoading ? 'Testing...' : 'Test Prompt'}</span>
              </button>
            </div>

            {testResult && (
              <div>
                <label className="block text-sm font-medium mb-1">Result</label>
                <div className="bg-gray-100 p-4 rounded-md">
                  <pre className="whitespace-pre-wrap text-sm">{testResult}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
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
          <h1 className="text-2xl font-bold text-gray-900">System Prompts</h1>
          <p className="text-gray-600">Configure AI behavior and response patterns</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleCreateDefaults}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
          >
            <Settings className="w-4 h-4" />
            <span>Create Defaults</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Prompt</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {prompts.map((prompt) => (
          <div key={prompt.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                  <span>{prompt.name}</span>
                  {prompt.is_default && <Star className="w-4 h-4 text-yellow-500" />}
                </h3>
                <p className="text-sm text-gray-600 mt-1">{prompt.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded ${
                  prompt.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {prompt.is_active ? 'Active' : 'Inactive'}
                </span>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                  {promptTypes.find(t => t.value === prompt.prompt_type)?.label}
                </span>
              </div>
            </div>

            <div className="bg-gray-50 p-3 rounded-md mb-4">
              <p className="text-sm text-gray-700 line-clamp-3 font-mono">
                {prompt.prompt_text}
              </p>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-4">
              <div>
                <p className="font-medium">Temperature</p>
                <p>{prompt.temperature}</p>
              </div>
              <div>
                <p className="font-medium">Max Tokens</p>
                <p>{prompt.max_tokens}</p>
              </div>
              <div>
                <p className="font-medium">Used</p>
                <p>{prompt.usage_count || 0} times</p>
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={() => openTestModal(prompt)}
                className="flex-1 bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 flex items-center justify-center space-x-1"
              >
                <TestTube className="w-4 h-4" />
                <span>Test</span>
              </button>
              
              <button
                onClick={() => openEditModal(prompt)}
                className="bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 flex items-center justify-center"
              >
                <Edit className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleDeletePrompt(prompt.id)}
                className="bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 flex items-center justify-center"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              
              {!prompt.is_default && (
                <button
                  onClick={() => handleSetDefault(prompt.id, prompt.prompt_type)}
                  className="bg-yellow-600 text-white py-2 px-3 rounded-md hover:bg-yellow-700 flex items-center justify-center"
                >
                  <Star className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {prompts.length === 0 && (
        <div className="text-center py-12">
          <Code className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No system prompts configured</h3>
          <p className="text-gray-600 mb-4">Add your first system prompt to configure AI behavior</p>
          <div className="flex justify-center space-x-3">
            <button
              onClick={handleCreateDefaults}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
            >
              Create Default Prompts
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Add Custom Prompt
            </button>
          </div>
        </div>
      )}

      <PromptModal
        show={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddPrompt}
        title="Add System Prompt"
      />

      <PromptModal
        show={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSubmit={handleEditPrompt}
        title="Edit System Prompt"
        isEdit={true}
      />

      <TestModal
        show={showTestModal}
        onClose={() => setShowTestModal(false)}
        prompt={selectedPrompt}
      />
    </div>
  );
};

export default SystemPrompts;