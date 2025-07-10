import React, { useState, useEffect } from 'react';
import { Send, Users, FileText, BarChart3, Activity, TrendingUp } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState({
    prospects: 0,
    templates: 0,
    campaigns: 0,
    intents: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [prospects, templates, campaigns, intents] = await Promise.all([
        apiService.getProspects(0, 1000),
        apiService.getTemplates(),
        apiService.getCampaigns(),
        apiService.getIntents()
      ]);

      setStats({
        prospects: prospects.data.length,
        templates: templates.data.length,
        campaigns: campaigns.data.length,
        intents: intents.data.length
      });
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Prospects',
      value: stats.prospects,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%'
    },
    {
      title: 'Email Templates',
      value: stats.templates,
      icon: FileText,
      color: 'bg-green-500',
      change: '+8%'
    },
    {
      title: 'Active Campaigns',
      value: stats.campaigns,
      icon: Send,
      color: 'bg-purple-500',
      change: '+23%'
    },
    {
      title: 'Intent Configs',
      value: stats.intents,
      icon: BarChart3,
      color: 'bg-orange-500',
      change: '+15%'
    }
  ];

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
        <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
        <div className="flex items-center space-x-2 text-sm text-secondary-600">
          <Activity className="h-4 w-4" />
          <span>Real-time updates</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-600">{card.title}</p>
                    <p className="text-2xl font-bold text-secondary-900">{card.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${card.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="mt-4 flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-600">{card.change}</span>
                  <span className="text-sm text-secondary-500">from last month</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900">Quick Actions</h3>
          </div>
          <div className="card-body space-y-4">
            <button className="w-full btn btn-primary text-left">
              <Send className="h-4 w-4 mr-2" />
              Create New Campaign
            </button>
            <button className="w-full btn btn-secondary text-left">
              <Users className="h-4 w-4 mr-2" />
              Upload Prospects
            </button>
            <button className="w-full btn btn-secondary text-left">
              <FileText className="h-4 w-4 mr-2" />
              Create Template
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-secondary-900">System Status</h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary-600">Email Service</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary-600">AI Service</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-secondary-600">Database</span>
                <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                  Connected
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-secondary-900">Recent Activity</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                <Send className="h-4 w-4 text-primary-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-secondary-900">Campaign "Welcome Series" started</p>
                <p className="text-xs text-secondary-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <Users className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-secondary-900">125 new prospects uploaded</p>
                <p className="text-xs text-secondary-500">5 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                <FileText className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-secondary-900">New template "Follow-up #2" created</p>
                <p className="text-xs text-secondary-500">1 day ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;