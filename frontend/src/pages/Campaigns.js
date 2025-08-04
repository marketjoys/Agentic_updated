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

const CampaignCard = ({ campaign, onSend, onView }) => {
  console.log('🔍 Campaign card rendered:', campaign);
  console.log('🔍 Campaign status:', campaign.status);
  console.log('🔍 Is draft?', campaign.status === 'draft');
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'paused': return 'bg-orange-100 text-orange-800';
      case 'completed': 
      case 'sent': return 'bg-purple-100 text-purple-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const canSendCampaign = (status) => {
    return status === 'draft';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Play className="h-4 w-4" />;
      case 'draft': return <Pause className="h-4 w-4" />;
      case 'completed':
      case 'sent': return <CheckCircle className="h-4 w-4" />;
      case 'failed': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-secondary-900">{campaign.name}</h3>
          <div className="flex items-center space-x-2">
            {getStatusIcon(campaign.status)}
            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(campaign.status)}`}>
              {campaign.status}
            </span>
          </div>
        </div>
        
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-sm text-secondary-600">
            <Users className="h-4 w-4 mr-2" />
            <span>{campaign.prospect_count || 0} prospects</span>
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
            <button 
              onClick={() => onView(campaign.id)}
              className="p-1 text-secondary-400 hover:text-primary-600 transition-colors"
              title="View Campaign Details"
            >
              <Eye className="h-4 w-4" />
            </button>
            {canSendCampaign(campaign.status) && (
              <button
                onClick={() => onSend(campaign.id)}
                className="p-2 bg-green-100 text-green-600 hover:bg-green-200 hover:text-green-700 rounded-md transition-colors"
                title="Send Campaign"
              >
                <Play className="h-4 w-4" />
              </button>
            )}
            {!canSendCampaign(campaign.status) && campaign.status !== 'draft' && (
              <button
                disabled
                className="p-2 bg-gray-100 text-gray-400 rounded-md cursor-not-allowed"
                title={`Campaign ${campaign.status} - Cannot send again`}
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
    follow_up_schedule_type: 'interval',
    follow_up_intervals: [3, 7, 14],
    follow_up_dates: [],
    follow_up_timezone: 'UTC',
    follow_up_time_window_start: '09:00',
    follow_up_time_window_end: '17:00',
    follow_up_days_of_week: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
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

  const addFollowUpDate = () => {
    const newDate = new Date();
    newDate.setDate(newDate.getDate() + formData.follow_up_dates.length + 1);
    const dateStr = newDate.toISOString().slice(0, 16);
    setFormData(prev => ({
      ...prev,
      follow_up_dates: [...prev.follow_up_dates, dateStr]
    }));
  };

  const updateFollowUpDate = (index, dateValue) => {
    const newDates = [...formData.follow_up_dates];
    newDates[index] = dateValue;
    setFormData(prev => ({
      ...prev,
      follow_up_dates: newDates
    }));
  };

  const removeFollowUpDate = (index) => {
    const newDates = formData.follow_up_dates.filter((_, i) => i !== index);
    setFormData(prev => ({
      ...prev,
      follow_up_dates: newDates
    }));
  };

  const handleDayOfWeekToggle = (day) => {
    const isSelected = formData.follow_up_days_of_week.includes(day);
    if (isSelected) {
      setFormData(prev => ({
        ...prev,
        follow_up_days_of_week: prev.follow_up_days_of_week.filter(d => d !== day)
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        follow_up_days_of_week: [...prev.follow_up_days_of_week, day]
      }));
    }
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
                    {/* Follow-up Schedule Type */}
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Schedule Type
                      </label>
                      <select
                        name="follow_up_schedule_type"
                        value={formData.follow_up_schedule_type}
                        onChange={handleChange}
                        className="input w-full"
                      >
                        <option value="interval">Interval-based (days after last contact)</option>
                        <option value="datetime">Specific date and time</option>
                      </select>
                    </div>

                    {/* Timezone Configuration */}
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Timezone
                      </label>
                      <select
                        name="follow_up_timezone"
                        value={formData.follow_up_timezone}
                        onChange={handleChange}
                        className="input w-full"
                      >
                        <option value="UTC">UTC</option>
                        <option value="America/New_York">Eastern Time</option>
                        <option value="America/Chicago">Central Time</option>
                        <option value="America/Denver">Mountain Time</option>
                        <option value="America/Los_Angeles">Pacific Time</option>
                        <option value="Europe/London">London</option>
                        <option value="Europe/Paris">Paris</option>
                        <option value="Asia/Tokyo">Tokyo</option>
                        <option value="Asia/Shanghai">Shanghai</option>
                        <option value="Asia/Kolkata">India</option>
                      </select>
                    </div>

                    {/* Interval-based Configuration */}
                    {formData.follow_up_schedule_type === 'interval' && (
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
                        <p className="text-xs text-gray-500 mt-1">
                          Days after initial contact or last follow-up
                        </p>
                      </div>
                    )}

                    {/* DateTime-based Configuration */}
                    {formData.follow_up_schedule_type === 'datetime' && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-sm font-medium text-secondary-700">
                            Follow-up Date & Times
                          </label>
                          <button
                            type="button"
                            onClick={addFollowUpDate}
                            className="text-sm bg-blue-100 text-blue-600 px-2 py-1 rounded hover:bg-blue-200"
                          >
                            Add Date
                          </button>
                        </div>
                        <div className="space-y-2 max-h-40 overflow-y-auto">
                          {formData.follow_up_dates.map((date, index) => (
                            <div key={index} className="flex items-center space-x-2">
                              <input
                                type="datetime-local"
                                value={date}
                                onChange={(e) => updateFollowUpDate(index, e.target.value)}
                                className="input flex-1"
                                min={new Date().toISOString().slice(0, 16)}
                              />
                              <button
                                type="button"
                                onClick={() => removeFollowUpDate(index)}
                                className="text-red-600 hover:text-red-800 px-2 py-1"
                                title="Remove date"
                              >
                                ✕
                              </button>
                            </div>
                          ))}
                          {formData.follow_up_dates.length === 0 && (
                            <p className="text-sm text-gray-500">No specific dates set. Click "Add Date" to schedule follow-ups.</p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Time Window Configuration */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-1">
                          Send Time Window Start
                        </label>
                        <input
                          type="time"
                          name="follow_up_time_window_start"
                          value={formData.follow_up_time_window_start}
                          onChange={handleChange}
                          className="input"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-secondary-700 mb-1">
                          Send Time Window End
                        </label>
                        <input
                          type="time"
                          name="follow_up_time_window_end"
                          value={formData.follow_up_time_window_end}
                          onChange={handleChange}
                          className="input"
                        />
                      </div>
                    </div>

                    {/* Days of Week Configuration */}
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Send Days (Select days when follow-ups can be sent)
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => (
                          <button
                            key={day}
                            type="button"
                            onClick={() => handleDayOfWeekToggle(day)}
                            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                              formData.follow_up_days_of_week.includes(day)
                                ? 'bg-primary-100 text-primary-700 border-primary-300'
                                : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                            }`}
                          >
                            {day.charAt(0).toUpperCase() + day.slice(1)}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Follow-up Templates */}
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

const ViewCampaignModal = ({ campaign, onClose }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800 border-green-200';
      case 'draft': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'paused': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'completed': 
      case 'sent': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Play className="h-5 w-5" />;
      case 'draft': return <Pause className="h-5 w-5" />;
      case 'completed':
      case 'sent': return <CheckCircle className="h-5 w-5" />;
      case 'failed': return <XCircle className="h-5 w-5" />;
      default: return <AlertCircle className="h-5 w-5" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-secondary-900">
              Campaign Details
            </h3>
            <button
              onClick={onClose}
              className="text-secondary-400 hover:text-secondary-600 transition-colors"
            >
              <XCircle className="h-6 w-6" />
            </button>
          </div>

          {/* Campaign Header */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-semibold text-secondary-900">
                {campaign.name}
              </h4>
              <div className={`flex items-center space-x-2 px-3 py-2 rounded-full border ${getStatusColor(campaign.status)}`}>
                {getStatusIcon(campaign.status)}
                <span className="font-medium capitalize">{campaign.status}</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {campaign.prospect_count || 0}
                </div>
                <div className="text-sm text-secondary-600">Prospects</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {campaign.analytics?.total_sent || 0}
                </div>
                <div className="text-sm text-secondary-600">Emails Sent</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {campaign.analytics?.success_rate?.toFixed(1) || 0}%
                </div>
                <div className="text-sm text-secondary-600">Success Rate</div>
              </div>
            </div>
          </div>

          {/* Campaign Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Basic Info */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-semibold text-secondary-900 mb-3">Campaign Information</h5>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Created:</span>
                  <span className="text-secondary-900">
                    {new Date(campaign.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Max Emails:</span>
                  <span className="text-secondary-900">{campaign.max_emails}</span>
                </div>
                {campaign.schedule && (
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Scheduled:</span>
                    <span className="text-secondary-900">
                      {new Date(campaign.schedule).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Analytics */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-semibold text-secondary-900 mb-3">Email Analytics</h5>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Total Emails:</span>
                  <span className="text-secondary-900">{campaign.analytics?.total_emails || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-600">Sent:</span>
                  <span className="text-green-700 font-medium">{campaign.analytics?.total_sent || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-red-600">Failed:</span>
                  <span className="text-red-700 font-medium">{campaign.analytics?.total_failed || 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Template Information */}
          {campaign.template && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h5 className="font-semibold text-secondary-900 mb-3">Template</h5>
              <div className="space-y-2">
                <div className="text-sm text-secondary-600">
                  <strong>Name:</strong> {campaign.template.name}
                </div>
                <div className="text-sm text-secondary-600">
                  <strong>Subject:</strong> {campaign.template.subject}
                </div>
                <div className="text-sm text-secondary-600">
                  <strong>Type:</strong> {campaign.template.type}
                </div>
              </div>
            </div>
          )}

          {/* Target Lists */}
          {campaign.lists && campaign.lists.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h5 className="font-semibold text-secondary-900 mb-3">Target Lists</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {campaign.lists.map((list) => (
                  <div key={list.id} className="flex items-center space-x-3 p-2 bg-white rounded border">
                    <div 
                      className="w-4 h-4 rounded-full" 
                      style={{ backgroundColor: list.color }}
                    ></div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-secondary-900">{list.name}</div>
                      <div className="text-xs text-secondary-600">
                        {list.prospect_count} prospects
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Email Records */}
          {campaign.email_records && campaign.email_records.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h5 className="font-semibold text-secondary-900 mb-3">
                Email Records ({campaign.email_records.length})
              </h5>
              <div className="max-h-64 overflow-y-auto">
                <div className="space-y-2">
                  {campaign.email_records.slice(0, 10).map((record, index) => (
                    <div key={record.id || index} className="flex items-center justify-between p-2 bg-white rounded border text-sm">
                      <div className="flex-1">
                        <div className="font-medium text-secondary-900">
                          {record.recipient_email}
                        </div>
                        <div className="text-xs text-secondary-600">
                          {record.subject}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          record.status === 'sent' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {record.status}
                        </span>
                        {record.sent_at && (
                          <span className="text-xs text-secondary-400">
                            {new Date(record.sent_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                  {campaign.email_records.length > 10 && (
                    <div className="text-center text-sm text-secondary-600 p-2">
                      ... and {campaign.email_records.length - 10} more records
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Close Button */}
          <div className="flex justify-end pt-4 border-t">
            <button
              onClick={onClose}
              className="btn btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Campaigns;