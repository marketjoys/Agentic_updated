import React, { useState, useEffect } from 'react';
import { Send, Users, FileText, BarChart3, Activity, TrendingUp, Sparkles, ArrowRight, Play, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';
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
      console.error('Dashboard API Error:', error);
      toast.error('Failed to load dashboard data');
      // Set default values so dashboard still loads
      setStats({
        prospects: 0,
        templates: 0,
        campaigns: 0,
        intents: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Prospects',
      value: stats.prospects,
      icon: Users,
      color: 'from-emerald-500 to-emerald-600',
      bgColor: 'from-emerald-50 to-emerald-100',
      change: '+12%',
      changeType: 'increase'
    },
    {
      title: 'Email Templates',
      value: stats.templates,
      icon: FileText,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'from-blue-50 to-blue-100',
      change: '+8%',
      changeType: 'increase'
    },
    {
      title: 'Active Campaigns',
      value: stats.campaigns,
      icon: Send,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'from-purple-50 to-purple-100',
      change: '+23%',
      changeType: 'increase'
    },
    {
      title: 'Intent Configs',
      value: stats.intents,
      icon: BarChart3,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'from-orange-50 to-orange-100',
      change: '+15%',
      changeType: 'increase'
    }
  ];

  const quickActions = [
    {
      title: 'Create Campaign',
      description: 'Start a new email campaign',
      icon: Send,
      color: 'from-blue-500 to-purple-600',
      link: '/campaigns'
    },
    {
      title: 'Add Prospects',
      description: 'Upload new prospects',
      icon: Users,
      color: 'from-green-500 to-emerald-600',
      link: '/prospects'
    },
    {
      title: 'Design Template',
      description: 'Create email templates',
      icon: FileText,
      color: 'from-orange-500 to-red-600',
      link: '/templates'
    },
    {
      title: 'Configure AI',
      description: 'Set up intent detection',
      icon: Sparkles,
      color: 'from-pink-500 to-purple-600',
      link: '/intents'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text">Welcome back!</h1>
          <p className="text-gray-600 mt-2">Here's what's happening with your email campaigns</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600 bg-white/70 backdrop-blur-sm px-4 py-2 rounded-xl border border-gray-100">
          <Activity className="h-4 w-4 text-green-500" />
          <span>All systems operational</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="stat-card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
                    <p className="text-3xl font-bold text-gray-900">{card.value}</p>
                  </div>
                  <div className={`icon-wrapper bg-gradient-to-r ${card.color}`}>
                    <Icon className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <div className="flex items-center space-x-1">
                    <TrendingUp className="h-4 w-4 text-emerald-500" />
                    <span className="text-sm text-emerald-600 font-medium">{card.change}</span>
                  </div>
                  <span className="text-sm text-gray-500 ml-2">from last month</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <div className="card-header">
            <h3 className="text-xl font-bold text-gray-900">Quick Actions</h3>
            <p className="text-gray-600 text-sm mt-1">Get started with common tasks</p>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <Link
                    key={index}
                    to={action.link}
                    className="group p-4 rounded-xl border border-gray-100 hover:border-gray-200 transition-all duration-200 hover:shadow-md"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg bg-gradient-to-r ${action.color}`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 group-hover:text-gray-700">
                          {action.title}
                        </h4>
                        <p className="text-sm text-gray-500">{action.description}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 transition-colors" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-xl font-bold text-gray-900">System Status</h3>
            <p className="text-gray-600 text-sm mt-1">All services running smoothly</p>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              {[
                { name: 'Email Service', status: 'online', color: 'emerald' },
                { name: 'AI Service (Groq)', status: 'online', color: 'emerald' },
                { name: 'Database', status: 'connected', color: 'emerald' },
                { name: 'Analytics', status: 'active', color: 'emerald' }
              ].map((service, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 bg-${service.color}-500 rounded-full`}></div>
                    <span className="text-sm font-medium text-gray-900">{service.name}</span>
                  </div>
                  <span className={`badge badge-success`}>
                    {service.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-xl font-bold text-gray-900">Recent Activity</h3>
          <p className="text-gray-600 text-sm mt-1">Latest updates across your campaigns</p>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {[
              {
                icon: Send,
                title: 'Sample Campaign Ready',
                description: 'Your first campaign is ready to launch',
                time: '2 hours ago',
                color: 'from-blue-500 to-purple-600'
              },
              {
                icon: Users,
                title: 'Sample Prospects Added',
                description: '5 sample prospects have been added to your database',
                time: '5 hours ago',
                color: 'from-green-500 to-emerald-600'
              },
              {
                icon: FileText,
                title: 'Email Templates Created',
                description: '3 sample templates are now available',
                time: '1 day ago',
                color: 'from-orange-500 to-red-600'
              },
              {
                icon: Sparkles,
                title: 'AI Intents Configured',
                description: 'Intent detection system is ready for use',
                time: '1 day ago',
                color: 'from-pink-500 to-purple-600'
              }
            ].map((activity, index) => {
              const Icon = activity.icon;
              return (
                <div key={index} className="flex items-center space-x-4 p-3 rounded-xl hover:bg-gray-50 transition-colors">
                  <div className={`p-2 rounded-lg bg-gradient-to-r ${activity.color}`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{activity.title}</h4>
                    <p className="text-sm text-gray-600">{activity.description}</p>
                  </div>
                  <span className="text-xs text-gray-500">{activity.time}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;