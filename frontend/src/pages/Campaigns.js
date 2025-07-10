import React, { useState, useEffect } from 'react';
import { Plus, Play, Pause, Send, Calendar, Users, Eye } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [campaignsResponse, templatesResponse] = await Promise.all([
        apiService.getCampaigns(),
        apiService.getTemplates()
      ]);
      setCampaigns(campaignsResponse.data);
      setTemplates(templatesResponse.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampaign = async (campaignData) => {
    try {
      await apiService.createCampaign(campaignData);
      toast.success('Campaign created successfully');
      setShowModal(false);
      loadData();
    } catch (error) {
      toast.error('Failed to create campaign');
    }
  };

  const handleSendCampaign = async (campaignId) => {
    try {
      const response = await apiService.sendCampaign(campaignId);
      toast.success(response.data.message);
      loadData();
    } catch (error) {
      toast.error('Failed to send campaign');
    }
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
        <h1 className="text-3xl font-bold text-secondary-900">Campaigns</h1>
        <button
          onClick={() => setShowModal(true)}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Campaign
        </button>
      </div>

      {/* Campaign Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Total Campaigns</p>
                <p className="text-2xl font-bold text-secondary-900">{campaigns.length}</p>
              </div>
              <Send className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {campaigns.filter(c => c.status === 'active').length}
                </p>
              </div>
              <Play className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Draft</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {campaigns.filter(c => c.status === 'draft').length}
                </p>
              </div>
              <Pause className="h-8 w-8 text-yellow-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Completed</p>
                <p className="text-2xl font-bold text-purple-600">
                  {campaigns.filter(c => c.status === 'completed').length}
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Campaigns List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {campaigns.map((campaign) => (
          <CampaignCard
            key={campaign.id}
            campaign={campaign}
            onSend={handleSendCampaign}
          />
        ))}
      </div>

      {/* Create Campaign Modal */}
      {showModal && (
        <CreateCampaignModal
          templates={templates}
          onClose={() => setShowModal(false)}
          onSave={handleCreateCampaign}
        />
      )}
    </div>
  );
};

const CampaignCard = ({ campaign, onSend }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'paused': return 'bg-orange-100 text-orange-800';
      case 'completed': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-secondary-900">{campaign.name}</h3>
          <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(campaign.status)}`}>
            {campaign.status}
          </span>
        </div>
        
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-secondary-600">
            <Users className="h-4 w-4 mr-2" />
            <span>{campaign.prospect_count} prospects</span>
          </div>
          <div className="flex items-center text-sm text-secondary-600">
            <Send className="h-4 w-4 mr-2" />
            <span>Max {campaign.max_emails} emails</span>
          </div>
          {campaign.schedule && (
            <div className="flex items-center text-sm text-secondary-600">
              <Calendar className="h-4 w-4 mr-2" />
              <span>{new Date(campaign.schedule).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="text-xs text-secondary-400">
            Created {new Date(campaign.created_at).toLocaleDateString()}
          </div>
          <div className="flex space-x-2">
            <button className="p-1 text-secondary-400 hover:text-primary-600">
              <Eye className="h-4 w-4" />
            </button>
            {campaign.status === 'draft' && (
              <button
                onClick={() => onSend(campaign.id)}
                className="p-1 text-secondary-400 hover:text-green-600"
              >
                <Play className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const CreateCampaignModal = ({ templates, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    template_id: '',
    max_emails: 1000,
    schedule: '',
    follow_up_intervals: [3, 7, 14],
    follow_up_templates: []
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const campaignData = {
      ...formData,
      schedule: formData.schedule ? new Date(formData.schedule).toISOString() : null
    };
    onSave(campaignData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const initialTemplates = templates.filter(t => t.type === 'initial');
  const followUpTemplates = templates.filter(t => t.type === 'follow_up');

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-2xl w-full p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Create New Campaign</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Campaign Name *
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
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Initial Template *
                </label>
                <select
                  name="template_id"
                  value={formData.template_id}
                  onChange={handleChange}
                  className="input"
                  required
                >
                  <option value="">Select template</option>
                  {initialTemplates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Max Emails
                </label>
                <input
                  type="number"
                  name="max_emails"
                  value={formData.max_emails}
                  onChange={handleChange}
                  className="input"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Schedule (Optional)
              </label>
              <input
                type="datetime-local"
                name="schedule"
                value={formData.schedule}
                onChange={handleChange}
                className="input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Follow-up Intervals (days)
              </label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  placeholder="3"
                  className="input w-20"
                  defaultValue="3"
                />
                <input
                  type="number"
                  placeholder="7"
                  className="input w-20"
                  defaultValue="7"
                />
                <input
                  type="number"
                  placeholder="14"
                  className="input w-20"
                  defaultValue="14"
                />
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
                Create Campaign
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Campaigns;