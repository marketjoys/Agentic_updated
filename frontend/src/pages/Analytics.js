import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Mail, Eye, MessageSquare, Clock } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Analytics = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    loadCampaigns();
  }, []);

  useEffect(() => {
    if (selectedCampaign) {
      loadAnalytics(selectedCampaign);
    }
  }, [selectedCampaign]);

  const loadCampaigns = async () => {
    try {
      const response = await apiService.getCampaigns();
      setCampaigns(response.data);
      if (response.data.length > 0) {
        setSelectedCampaign(response.data[0].id);
      }
    } catch (error) {
      toast.error('Failed to load campaigns');
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async (campaignId) => {
    try {
      const response = await apiService.getCampaignAnalytics(campaignId);
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    }
  };

  const calculateRate = (numerator, denominator) => {
    if (denominator === 0) return 0;
    return ((numerator / denominator) * 100).toFixed(1);
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
        <h1 className="text-3xl font-bold text-secondary-900">Analytics</h1>
        <div className="flex items-center space-x-4">
          <select
            value={selectedCampaign}
            onChange={(e) => setSelectedCampaign(e.target.value)}
            className="input w-64"
          >
            <option value="">Select Campaign</option>
            {campaigns.map(campaign => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {analytics ? (
        <>
          {/* Overall Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-secondary-600">Emails Sent</p>
                    <p className="text-2xl font-bold text-secondary-900">{analytics.total_sent}</p>
                  </div>
                  <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Mail className="h-5 w-5 text-blue-600" />
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-sm text-secondary-500">
                    {analytics.total_failed} failed
                  </span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-secondary-600">Open Rate</p>
                    <p className="text-2xl font-bold text-green-600">
                      {calculateRate(analytics.total_opened, analytics.total_sent)}%
                    </p>
                  </div>
                  <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center">
                    <Eye className="h-5 w-5 text-green-600" />
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-sm text-secondary-500">
                    {analytics.total_opened} opened
                  </span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-secondary-600">Reply Rate</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {calculateRate(analytics.total_replied, analytics.total_sent)}%
                    </p>
                  </div>
                  <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <MessageSquare className="h-5 w-5 text-purple-600" />
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-sm text-secondary-500">
                    {analytics.total_replied} replied
                  </span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-secondary-600">Delivery Rate</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {calculateRate(analytics.total_sent, analytics.total_sent + analytics.total_failed)}%
                    </p>
                  </div>
                  <div className="h-10 w-10 bg-orange-100 rounded-full flex items-center justify-center">
                    <TrendingUp className="h-5 w-5 text-orange-600" />
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-sm text-secondary-500">
                    {analytics.total_sent + analytics.total_failed} attempted
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Chart Placeholder */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Email Performance</h3>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Sent</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-secondary-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: '100%'}}></div>
                      </div>
                      <span className="text-sm font-medium">{analytics.total_sent}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Opened</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-secondary-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{width: `${calculateRate(analytics.total_opened, analytics.total_sent)}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{analytics.total_opened}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Replied</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-secondary-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full" 
                          style={{width: `${calculateRate(analytics.total_replied, analytics.total_sent)}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{analytics.total_replied}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Failed</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 bg-secondary-200 rounded-full h-2">
                        <div 
                          className="bg-red-600 h-2 rounded-full" 
                          style={{width: `${calculateRate(analytics.total_failed, analytics.total_sent + analytics.total_failed)}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{analytics.total_failed}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Campaign Summary</h3>
              </div>
              <div className="card-body">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Total Emails</span>
                    <span className="text-sm font-medium">{analytics.total_sent + analytics.total_failed}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Success Rate</span>
                    <span className="text-sm font-medium text-green-600">
                      {calculateRate(analytics.total_sent, analytics.total_sent + analytics.total_failed)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Engagement Rate</span>
                    <span className="text-sm font-medium text-purple-600">
                      {calculateRate(analytics.total_opened + analytics.total_replied, analytics.total_sent)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-secondary-600">Conversion Rate</span>
                    <span className="text-sm font-medium text-orange-600">
                      {calculateRate(analytics.total_replied, analytics.total_sent)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Insights */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-secondary-900">Insights & Recommendations</h3>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h4 className="font-medium text-secondary-900">Performance Insights</h4>
                  {analytics.total_opened > 0 && (
                    <div className="flex items-center space-x-2">
                      <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-secondary-600">
                        Good open rate indicates effective subject lines
                      </span>
                    </div>
                  )}
                  {analytics.total_replied > 0 && (
                    <div className="flex items-center space-x-2">
                      <div className="h-2 w-2 bg-purple-500 rounded-full"></div>
                      <span className="text-sm text-secondary-600">
                        Replies indicate strong content relevance
                      </span>
                    </div>
                  )}
                  {analytics.total_failed > 0 && (
                    <div className="flex items-center space-x-2">
                      <div className="h-2 w-2 bg-red-500 rounded-full"></div>
                      <span className="text-sm text-secondary-600">
                        Check email addresses and SMTP settings
                      </span>
                    </div>
                  )}
                </div>
                <div className="space-y-3">
                  <h4 className="font-medium text-secondary-900">Optimization Tips</h4>
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-secondary-400" />
                    <span className="text-sm text-secondary-600">
                      Send times affect open rates
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <BarChart3 className="h-4 w-4 text-secondary-400" />
                    <span className="text-sm text-secondary-600">
                      A/B test different subject lines
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-secondary-400" />
                    <span className="text-sm text-secondary-600">
                      Personalization improves engagement
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="card">
          <div className="card-body text-center py-12">
            <BarChart3 className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">No Data Available</h3>
            <p className="text-secondary-600">
              {campaigns.length === 0 
                ? 'Create a campaign to view analytics' 
                : 'Select a campaign to view its analytics'
              }
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;