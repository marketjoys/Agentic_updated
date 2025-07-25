import React, { useState, useEffect } from 'react';
import { Plus, Edit, Eye, FileText, Code, Mail, Palette } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import HTMLTemplateEditor from '../components/HTMLTemplateEditor';

const Templates = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await apiService.getTemplates();
      setTemplates(response.data);
    } catch (error) {
      toast.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTemplate = async (templateData) => {
    try {
      if (editingTemplate) {
        await apiService.updateTemplate(editingTemplate.id, templateData);
        toast.success('Template updated successfully');
      } else {
        await apiService.createTemplate(templateData);
        toast.success('Template created successfully');
      }
      setShowModal(false);
      setEditingTemplate(null);
      loadTemplates();
    } catch (error) {
      toast.error('Failed to save template');
    }
  };

  const handleEditTemplate = (template) => {
    setEditingTemplate(template);
    setShowModal(true);
  };

  const handleNewTemplate = () => {
    setEditingTemplate(null);
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
        <h1 className="text-3xl font-bold text-secondary-900">Email Templates</h1>
        <button
          onClick={handleNewTemplate}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Template
        </button>
      </div>

      {/* Template Types Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-secondary-900">Initial</h3>
                <p className="text-sm text-secondary-600">First contact templates</p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-secondary-900">Follow-up</h3>
                <p className="text-sm text-secondary-600">Sequence templates</p>
              </div>
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <FileText className="h-4 w-4 text-green-600" />
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-secondary-900">Auto-response</h3>
                <p className="text-sm text-secondary-600">AI-generated replies</p>
              </div>
              <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                <FileText className="h-4 w-4 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <TemplateCard
            key={template.id}
            template={template}
            onEdit={handleEditTemplate}
          />
        ))}
      </div>

      {/* Template Modal */}
      <HTMLTemplateEditor
        isOpen={showModal}
        template={editingTemplate}
        onClose={() => {
          setShowModal(false);
          setEditingTemplate(null);
        }}
        onSave={handleSaveTemplate}
      />
    </div>
  );
};

const TemplateCard = ({ template, onEdit }) => {
  const getTypeColor = (type) => {
    switch (type) {
      case 'initial': return 'bg-blue-100 text-blue-800';
      case 'follow_up': return 'bg-green-100 text-green-800';
      case 'auto_response': return 'bg-purple-100 text-purple-800';
      case 'email': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-semibold text-secondary-900">{template.name}</h3>
            {template.is_html_enabled && (
              <div className="flex items-center space-x-1">
                <Code className="h-4 w-4 text-purple-600" />
                <span className="text-xs text-purple-600">HTML</span>
              </div>
            )}
          </div>
          <span className={`px-2 py-1 text-xs rounded-full ${getTypeColor(template.type)}`}>
            {template.type?.replace('_', ' ') || 'Email'}
          </span>
        </div>
        <p className="text-sm text-secondary-600 mb-3">{template.subject}</p>
        <div className="text-sm text-secondary-500 mb-4">
          <div className="max-h-20 overflow-hidden">
            {template.content ? 
              template.content.substring(0, 100) + (template.content.length > 100 ? '...' : '') :
              'No content preview'
            }
          </div>
        </div>
        <div className="flex justify-between items-center">
          <div className="text-xs text-secondary-400 flex items-center space-x-2">
            <span>{template.created_at ? new Date(template.created_at).toLocaleDateString() : 'Unknown date'}</span>
            {template.style_settings?.primaryColor && (
              <div className="flex items-center space-x-1">
                <Palette className="h-3 w-3" />
                <div 
                  className="w-3 h-3 rounded-full border" 
                  style={{ backgroundColor: template.style_settings.primaryColor }}
                ></div>
              </div>
            )}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => onEdit(template)}
              className="p-1 text-secondary-400 hover:text-primary-600 transition-colors"
              title="Edit Template"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button 
              className="p-1 text-secondary-400 hover:text-primary-600 transition-colors"
              title="Preview Template"
            >
              <Eye className="h-4 w-4" />
            </button>
            {template.is_html_enabled && (
              <button 
                className="p-1 text-secondary-400 hover:text-primary-600 transition-colors"
                title="HTML Template"
              >
                <Mail className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const TemplateModal = ({ template, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: template?.name || '',
    subject: template?.subject || '',
    content: template?.content || '',
    type: template?.type || 'initial',
    placeholders: template?.placeholders || []
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const placeholderExamples = [
    '{{first_name}}',
    '{{last_name}}',
    '{{company}}',
    '{{email}}'
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-2xl w-full p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
            {template ? 'Edit Template' : 'Create New Template'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Template Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="input"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Type *
                </label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="input"
                  required
                >
                  <option value="initial">Initial</option>
                  <option value="follow_up">Follow-up</option>
                  <option value="auto_response">Auto-response</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Subject Line *
              </label>
              <input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                className="input"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Email Content *
              </label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleChange}
                rows="8"
                className="input"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Available Placeholders
              </label>
              <div className="flex flex-wrap gap-2">
                {placeholderExamples.map((placeholder, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-secondary-100 text-secondary-700 text-sm rounded"
                  >
                    {placeholder}
                  </span>
                ))}
              </div>
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
                {template ? 'Update' : 'Create'} Template
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Templates;