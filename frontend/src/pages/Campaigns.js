import React, { useState, useEffect } from 'react';
import { Plus, Play, Pause, Send, Calendar, Users, Eye, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    console.log('🔄 Starting loadData...');
    
    // Add a small delay to ensure proper initialization
    await new Promise(resolve => setTimeout(resolve, 100));
    
    try {
      console.log('🔄 Loading campaigns and templates...');
      
      // Load campaigns and templates separately to better handle errors
      const campaignsResponse = await apiService.getCampaigns();
      console.log('📊 Campaigns response:', campaignsResponse.data);
      
      const templatesResponse = await apiService.getTemplates();
      console.log('📝 Templates response:', templatesResponse.data);
      
      console.log('🔄 Setting state...');
      
      // Ensure data is valid before setting state
      if (campaignsResponse.data && Array.isArray(campaignsResponse.data)) {
        setCampaigns(campaignsResponse.data);
        console.log('✅ Campaigns state set successfully');
      } else {
        console.warn('⚠️ Invalid campaigns data:', campaignsResponse.data);
        setCampaigns([]);
      }
      
      if (templatesResponse.data && Array.isArray(templatesResponse.data)) {
        setTemplates(templatesResponse.data);
        console.log('✅ Templates state set successfully');
      } else {
        console.warn('⚠️ Invalid templates data:', templatesResponse.data);
        setTemplates([]);
      }
      
      console.log('✅ Data loaded successfully');
      console.log('🔄 Setting loading to false...');
    } catch (error) {
      console.error('❌ Error loading data:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      // Set empty arrays on error to prevent undefined state
      setCampaigns([]);
      setTemplates([]);
      
      toast.error('Failed to load data: ' + (error.response?.data?.detail || error.message));
    } finally {
      console.log('🔄 Finally block: setting loading to false');
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

  const handleViewCampaign = async (campaignId) => {
    console.log('👁️ handleViewCampaign called with campaignId:', campaignId);
    
    try {
      console.log('📡 Fetching campaign details via API...');
      const response = await apiService.getCampaign(campaignId);
      console.log('✅ Campaign details fetched successfully:', response.data);
      
      setSelectedCampaign(response.data);
      setShowViewModal(true);
    } catch (error) {
      console.error('❌ Failed to fetch campaign details:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      const errorMessage = error.response?.data?.detail || 'Failed to fetch campaign details';
      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-right',
      });
    }
  };

  const handleSendCampaign = async (campaignId) => {
    console.log('🚀 handleSendCampaign called with campaignId:', campaignId);
    
    try {
      console.log('📡 Sending campaign via API...');
      const response = await apiService.sendCampaign(campaignId);
      console.log('✅ Campaign sent successfully:', response.data);
      
      // Enhanced success message with details
      const result = response.data;
      const successMessage = `Campaign sent successfully! ${result.total_sent} emails sent, ${result.total_failed} failed.`;
      
      toast.success(successMessage, {
        duration: 6000,
        position: 'top-right',
      });
      
      loadData();
    } catch (error) {
      console.error('❌ Campaign sending failed:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      const errorMessage = error.response?.data?.detail || 'Failed to send campaign';
      toast.error(errorMessage, {
        duration: 8000,
        position: 'top-right',
      });
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
                  {campaigns.filter(c => c.status === 'completed' || c.status === 'sent').length}
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
            onView={handleViewCampaign}
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

      {/* View Campaign Modal */}
      {showViewModal && selectedCampaign && (
        <ViewCampaignModal
          campaign={selectedCampaign}
          onClose={() => {
            setShowViewModal(false);
            setSelectedCampaign(null);
          }}
        />
      )}
    </div>
  );
};

const CampaignCard = ({ campaign, onSend }) => {
  console.log('🔍 Campaign card rendered:', campaign);
  console.log('🔍 Campaign status:', campaign.status);
  console.log('🔍 Is draft?', campaign.status === 'draft');
  
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
                className="p-2 bg-green-100 text-green-600 hover:bg-green-200 hover:text-green-700 rounded-md transition-colors"
                title="Send Campaign"
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
  const [lists, setLists] = useState([]);
  const [emailProviders, setEmailProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    template_id: '',
    list_ids: [],
    email_provider_id: '',
    max_emails: 1000,
    schedule_type: 'immediate',
    start_time: '',
    follow_up_enabled: true,
    follow_up_intervals: [3, 7, 14],
    follow_up_templates: []
  });

  useEffect(() => {
    loadModalData();
  }, []);

  const loadModalData = async () => {
    try {
      const [listsResponse, providersResponse] = await Promise.all([
        apiService.getLists(),
        apiService.getEmailProviders()
      ]);
      setLists(listsResponse.data);
      setEmailProviders(providersResponse.data);
    } catch (error) {
      toast.error('Failed to load campaign data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.list_ids.length === 0) {
      toast.error('Please select at least one prospect list');
      return;
    }
    if (!formData.email_provider_id) {
      toast.error('Please select an email provider');
      return;
    }
    
    const campaignData = {
      ...formData,
      start_time: formData.start_time ? new Date(formData.start_time).toISOString() : null,
      follow_up_intervals: formData.follow_up_intervals.filter(interval => interval > 0)
    };
    onSave(campaignData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleListSelection = (listId) => {
    setFormData(prev => ({
      ...prev,
      list_ids: prev.list_ids.includes(listId)
        ? prev.list_ids.filter(id => id !== listId)
        : [...prev.list_ids, listId]
    }));
  };

  const handleFollowUpTemplateSelection = (templateId) => {
    setFormData(prev => ({
      ...prev,
      follow_up_templates: prev.follow_up_templates.includes(templateId)
        ? prev.follow_up_templates.filter(id => id !== templateId)
        : [...prev.follow_up_templates, templateId]
    }));
  };

  const handleIntervalChange = (index, value) => {
    const newIntervals = [...formData.follow_up_intervals];
    newIntervals[index] = parseInt(value) || 0;
    setFormData(prev => ({
      ...prev,
      follow_up_intervals: newIntervals
    }));
  };

  const initialTemplates = templates.filter(t => t.type === 'initial');
  const followUpTemplates = templates.filter(t => t.type === 'follow_up');

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex items-center justify-center min-h-screen px-4">
          <div className="fixed inset-0 bg-black opacity-30"></div>
          <div className="relative bg-white rounded-lg max-w-2xl w-full p-6">
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Create New Campaign</h3>
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Basic Information */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-3">Basic Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    placeholder="Enter campaign name"
                  />
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
                    max="10000"
                  />
                </div>
              </div>
            </div>

            {/* Email Provider Selection */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-3">Email Provider *</h4>
              <select
                name="email_provider_id"
                value={formData.email_provider_id}
                onChange={handleChange}
                className="input w-full"
                required
              >
                <option value="">Select email provider</option>
                {emailProviders.map(provider => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name} ({provider.email_address})
                  </option>
                ))}
              </select>
              {emailProviders.length === 0 && (
                <p className="text-sm text-orange-600 mt-2">
                  No email providers configured. Please add an email provider first.
                </p>
              )}
            </div>

            {/* Template Selection */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-3">Initial Template *</h4>
              <select
                name="template_id"
                value={formData.template_id}
                onChange={handleChange}
                className="input w-full"
                required
              >
                <option value="">Select initial template</option>
                {initialTemplates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Prospect Lists Selection */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-3">Target Prospect Lists *</h4>
              <div className="max-h-32 overflow-y-auto space-y-2">
                {lists.map(list => (
                  <label key={list.id} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.list_ids.includes(list.id)}
                      onChange={() => handleListSelection(list.id)}
                      className="h-4 w-4 text-primary-600 rounded"
                    />
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: list.color }}
                      ></div>
                      <span className="text-sm text-secondary-700">
                        {list.name} ({list.prospect_count} prospects)
                      </span>
                    </div>
                  </label>
                ))}
              </div>
              {lists.length === 0 && (
                <p className="text-sm text-orange-600">
                  No prospect lists available. Please create prospect lists first.
                </p>
              )}
              {formData.list_ids.length > 0 && (
                <p className="text-sm text-green-600 mt-2">
                  {formData.list_ids.length} list(s) selected
                </p>
              )}
            </div>

            {/* Scheduling */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-3">Scheduling</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Schedule Type
                  </label>
                  <select
                    name="schedule_type"
                    value={formData.schedule_type}
                    onChange={handleChange}
                    className="input"
                  >
                    <option value="immediate">Send Immediately</option>
                    <option value="scheduled">Schedule for Later</option>
                  </select>
                </div>
                
                {formData.schedule_type === 'scheduled' && (
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">
                      Start Time *
                    </label>
                    <input
                      type="datetime-local"
                      name="start_time"
                      value={formData.start_time}
                      onChange={handleChange}
                      className="input"
                      required={formData.schedule_type === 'scheduled'}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Follow-up Configuration */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-secondary-900 mb-3">Follow-up Configuration</h4>
              <div className="space-y-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    name="follow_up_enabled"
                    checked={formData.follow_up_enabled}
                    onChange={handleChange}
                    className="h-4 w-4 text-primary-600 rounded"
                  />
                  <span className="text-sm text-secondary-700">Enable Follow-up Emails</span>
                </label>

                {formData.follow_up_enabled && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Follow-up Intervals (days)
                      </label>
                      <div className="flex space-x-2">
                        {formData.follow_up_intervals.map((interval, index) => (
                          <input
                            key={index}
                            type="number"
                            value={interval}
                            onChange={(e) => handleIntervalChange(index, e.target.value)}
                            className="input w-20"
                            min="1"
                            max="30"
                            placeholder={`Day ${index + 1}`}
                          />
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Follow-up Templates (Optional)
                      </label>
                      <div className="max-h-24 overflow-y-auto space-y-2">
                        {followUpTemplates.map(template => (
                          <label key={template.id} className="flex items-center space-x-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={formData.follow_up_templates.includes(template.id)}
                              onChange={() => handleFollowUpTemplateSelection(template.id)}
                              className="h-4 w-4 text-primary-600 rounded"
                            />
                            <span className="text-sm text-secondary-700">{template.name}</span>
                          </label>
                        ))}
                      </div>
                      {followUpTemplates.length === 0 && (
                        <p className="text-sm text-gray-500">No follow-up templates available</p>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
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