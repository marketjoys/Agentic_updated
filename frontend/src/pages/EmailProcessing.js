import React, { useState, useEffect } from 'react';
import { Play, Pause, Brain, MessageSquare, TrendingUp, AlertCircle, CheckCircle, Mail, Eye, Send, Settings, Activity, Users, Clock, StopCircle, RotateCcw } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const EmailProcessing = () => {
  const [processingStatus, setProcessingStatus] = useState('stopped');
  const [followUpEngineStatus, setFollowUpEngineStatus] = useState('stopped');
  const [analytics, setAnalytics] = useState({
    total_threads: 0,
    processed_emails: 0,
    auto_responses_sent: 0,
    processing_status: 'stopped'
  });
  const [followUpDashboard, setFollowUpDashboard] = useState({
    imap_monitoring: {},
    follow_up_stats: {},
    system_status: {}
  });
  const [imapScanStatus, setImapScanStatus] = useState({
    last_scan: null,
    statistics_24h: {},
    processor_status: {}
  });
  const [threads, setThreads] = useState([]);
  const [imapLogs, setImapLogs] = useState([]);
  const [prospectResponses, setProspectResponses] = useState([]);
  const [healthCheck, setHealthCheck] = useState({});
  const [loading, setLoading] = useState(true);
  const [showTestModal, setShowTestModal] = useState(false);
  const [showImapLogsModal, setShowImapLogsModal] = useState(false);
  const [showResponsesModal, setShowResponsesModal] = useState(false);
  const [showThreadAnalysisModal, setShowThreadAnalysisModal] = useState(false);
  const [selectedThread, setSelectedThread] = useState(null);
  const [threadAnalysis, setThreadAnalysis] = useState(null);
  const [selectedProspectId, setSelectedProspectId] = useState('');

  useEffect(() => {
    loadData();
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [
        statusResponse,
        analyticsResponse,
        threadsResponse,
        followUpDashboardResponse,
        followUpEngineStatusResponse,
        healthCheckResponse,
        imapScanStatusResponse
      ] = await Promise.all([
        apiService.getProcessingStatus(),
        apiService.getProcessingAnalytics(),
        apiService.getThreads(),
        apiService.getFollowUpDashboard(),
        apiService.getFollowUpEngineStatus(),
        apiService.getFollowUpHealthCheck(),
        apiService.getImapScanStatus()
      ]);

      setProcessingStatus(statusResponse.data.status);
      setAnalytics(analyticsResponse.data);
      setThreads(threadsResponse.data);
      setFollowUpDashboard(followUpDashboardResponse.data);
      setFollowUpEngineStatus(followUpEngineStatusResponse.data.status);
      setHealthCheck(healthCheckResponse.data);
      setImapScanStatus(imapScanStatusResponse.data);
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load monitoring data');
    } finally {
      setLoading(false);
    }
  };

  const handleStartProcessing = async () => {
    try {
      await apiService.startEmailProcessing();
      toast.success('Email processing started successfully');
      setProcessingStatus('running');
      loadData();
    } catch (error) {
      toast.error('Failed to start email processing');
    }
  };

  const handleStopProcessing = async () => {
    try {
      await apiService.stopEmailProcessing();
      toast.success('Email processing stopped');
      setProcessingStatus('stopped');
      loadData();
    } catch (error) {
      toast.error('Failed to stop email processing');
    }
  };

  const handleStartFollowUpEngine = async () => {
    try {
      await apiService.startFollowUpEngine();
      toast.success('Follow-up engine started successfully');
      setFollowUpEngineStatus('running');
      loadData();
    } catch (error) {
      toast.error('Failed to start follow-up engine');
    }
  };

  const handleStopFollowUpEngine = async () => {
    try {
      await apiService.stopFollowUpEngine();
      toast.success('Follow-up engine stopped');
      setFollowUpEngineStatus('stopped');
      loadData();
    } catch (error) {
      toast.error('Failed to stop follow-up engine');
    }
  };

  const handleViewThread = (thread) => {
    setSelectedThread(thread);
  };

  const handleShowImapLogs = async () => {
    try {
      const response = await apiService.getImapLogs(24);
      setImapLogs(response.data.logs);
      setShowImapLogsModal(true);
    } catch (error) {
      toast.error('Failed to load IMAP logs');
    }
  };

  const handleShowResponses = async () => {
    try {
      const response = await apiService.getProspectResponses(7);
      setProspectResponses(response.data.responses);
      setShowResponsesModal(true);
    } catch (error) {
      toast.error('Failed to load prospect responses');
    }
  };

  const handleAnalyzeThread = async () => {
    if (!selectedProspectId) {
      toast.error('Please enter a prospect ID');
      return;
    }

    try {
      const response = await apiService.analyzeProspectThread(selectedProspectId);
      setThreadAnalysis(response.data);
      setShowThreadAnalysisModal(true);
    } catch (error) {
      toast.error('Failed to analyze thread');
    }
  };

  const handleForceStopFollowUp = async (prospectId) => {
    try {
      await apiService.forceStopFollowUp(prospectId);
      toast.success('Follow-ups stopped for prospect');
      loadData();
    } catch (error) {
      toast.error('Failed to stop follow-ups');
    }
  };

  const handleRestartFollowUp = async (prospectId) => {
    try {
      await apiService.restartFollowUp(prospectId);
      toast.success('Follow-ups restarted for prospect');
      loadData();
    } catch (error) {
      toast.error('Failed to restart follow-ups');
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">AI Email Processing & Follow-Up Monitoring</h1>
          <p className="text-secondary-600 mt-1">
            Comprehensive monitoring of email processing and intelligent follow-up systems
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowTestModal(true)}
            className="btn btn-secondary"
          >
            <Brain className="h-4 w-4 mr-2" />
            Test AI
          </button>
          <button
            onClick={handleShowImapLogs}
            className="btn btn-secondary"
          >
            <Activity className="h-4 w-4 mr-2" />
            IMAP Logs
          </button>
          <button
            onClick={handleShowResponses}
            className="btn btn-secondary"
          >
            <Users className="h-4 w-4 mr-2" />
            Responses
          </button>
        </div>
      </div>

      {/* Enhanced Auto Responder Status Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Auto Responder Status Card */}
        <div className="col-span-2 card">
          <div className="card-header">
            <h3 className="text-xl font-bold text-secondary-900 flex items-center">
              <Brain className="h-6 w-6 mr-2 text-blue-600" />
              Auto Responder Status
            </h3>
            <p className="text-sm text-secondary-600 mt-1">
              Real-time monitoring of automatic email response system
            </p>
          </div>
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-3 rounded-full ${
                  processingStatus === 'running' 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-red-100 text-red-600'
                }`}>
                  {processingStatus === 'running' ? 
                    <CheckCircle className="h-6 w-6" /> : 
                    <AlertCircle className="h-6 w-6" />
                  }
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-secondary-900">
                    Email Processing Engine
                  </h4>
                  <p className="text-sm text-secondary-600">
                    {processingStatus === 'running' 
                      ? 'Monitoring IMAP and generating automatic responses'
                      : 'Auto responder is currently stopped'
                    }
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`px-4 py-2 rounded-full text-sm font-medium ${
                  processingStatus === 'running' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {processingStatus === 'running' ? 'ACTIVE' : 'STOPPED'}
                </div>
                {processingStatus === 'running' ? (
                  <button
                    onClick={handleStopProcessing}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg border"
                    title="Stop Auto Responder"
                  >
                    <Pause className="h-5 w-5" />
                  </button>
                ) : (
                  <button
                    onClick={handleStartProcessing}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-lg border"
                    title="Start Auto Responder"
                  >
                    <Play className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>
            
            {/* IMAP Scan Information */}
            <div className="border-t pt-4">
              <h5 className="text-sm font-semibold text-secondary-700 mb-3">Last IMAP Scan Activity</h5>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-lg font-bold text-secondary-900">
                    {followUpDashboard.imap_monitoring?.emails_processed_24h || 0}
                  </div>
                  <div className="text-secondary-600">Emails Scanned (24h)</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-lg font-bold text-secondary-900">
                    {followUpDashboard.imap_monitoring?.threads_active_24h || 0}
                  </div>
                  <div className="text-secondary-600">Active Threads (24h)</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-lg font-bold text-secondary-900">
                    {analytics.auto_responses_sent || 0}
                  </div>
                  <div className="text-secondary-600">Auto Responses Sent</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* IMAP Connection Status */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-bold text-secondary-900 flex items-center">
              <Mail className="h-5 w-5 mr-2 text-purple-600" />
              IMAP Monitor
            </h3>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Connection Status</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  processingStatus === 'running' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {processingStatus === 'running' ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Last Scan</span>
                <span className="text-sm font-medium text-secondary-900">
                  {followUpDashboard.system_status?.last_updated 
                    ? new Date(followUpDashboard.system_status.last_updated).toLocaleTimeString()
                    : 'Never'
                  }
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Scan Frequency</span>
                <span className="text-sm font-medium text-secondary-900">
                  {processingStatus === 'running' ? '30 seconds' : 'Stopped'}
                </span>
              </div>
            </div>
            
            <div className="mt-4">
              <button
                onClick={handleShowImapLogs}
                className="w-full btn btn-secondary text-sm"
              >
                <Activity className="h-4 w-4 mr-2" />
                View IMAP Logs
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Follow-up Engine Status */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${
                  followUpEngineStatus === 'running' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {followUpEngineStatus === 'running' ? 
                    <Clock className="h-5 w-5" /> : 
                    <StopCircle className="h-5 w-5" />
                  }
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900">
                    Follow-up Engine
                  </h3>
                  <p className="text-sm text-secondary-600">
                    {followUpEngineStatus === 'running' 
                      ? 'Sending scheduled follow-ups'
                      : 'Follow-up engine is stopped'
                    }
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  followUpEngineStatus === 'running' 
                    ? 'bg-blue-100 text-blue-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {followUpEngineStatus.toUpperCase()}
                </div>
                {followUpEngineStatus === 'running' ? (
                  <button
                    onClick={handleStopFollowUpEngine}
                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                  >
                    <Pause className="h-4 w-4" />
                  </button>
                ) : (
                  <button
                    onClick={handleStartFollowUpEngine}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    <Play className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Total Threads</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.total_threads}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Processed Emails</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.processed_emails}</p>
              </div>
              <Mail className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Auto Responses</p>
                <p className="text-2xl font-bold text-secondary-900">{analytics.auto_responses_sent}</p>
              </div>
              <Send className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-secondary-600">Follow-up Rate</p>
                <p className="text-2xl font-bold text-secondary-900">
                  {followUpDashboard.follow_up_stats?.response_rate || 0}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-emerald-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Follow-up Monitoring Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* IMAP Monitoring */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-xl font-bold text-secondary-900">IMAP Monitoring</h3>
            <p className="text-sm text-secondary-600 mt-1">
              Real-time email scanning statistics
            </p>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Emails Processed (24h)</span>
                <span className="font-semibold text-secondary-900">
                  {followUpDashboard.imap_monitoring?.emails_processed_24h || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Active Threads (24h)</span>
                <span className="font-semibold text-secondary-900">
                  {followUpDashboard.imap_monitoring?.threads_active_24h || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Responses (24h)</span>
                <span className="font-semibold text-secondary-900">
                  {followUpDashboard.imap_monitoring?.prospects_responded_24h || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Follow-up Statistics */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-xl font-bold text-secondary-900">Follow-up Statistics</h3>
            <p className="text-sm text-secondary-600 mt-1">
              Follow-up performance metrics
            </p>
          </div>
          <div className="card-body">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Active Follow-ups</span>
                <span className="font-semibold text-secondary-900">
                  {followUpDashboard.follow_up_stats?.active_follow_ups || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Stopped Follow-ups</span>
                <span className="font-semibold text-secondary-900">
                  {followUpDashboard.follow_up_stats?.stopped_follow_ups || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-secondary-600">Response Rate</span>
                <span className="font-semibold text-secondary-900">
                  {followUpDashboard.follow_up_stats?.response_rate || 0}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Thread Analysis Tool */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-xl font-bold text-secondary-900">Thread Analysis Tool</h3>
          <p className="text-sm text-secondary-600 mt-1">
            Analyze specific prospect threads for follow-up effectiveness
          </p>
        </div>
        <div className="card-body">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <input
                type="text"
                value={selectedProspectId}
                onChange={(e) => setSelectedProspectId(e.target.value)}
                placeholder="Enter prospect ID to analyze..."
                className="input"
              />
            </div>
            <button
              onClick={handleAnalyzeThread}
              className="btn btn-primary"
            >
              <Eye className="h-4 w-4 mr-2" />
              Analyze Thread
            </button>
          </div>
        </div>
      </div>

      {/* Conversation Threads */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-xl font-bold text-secondary-900">Recent Conversation Threads</h3>
          <p className="text-sm text-secondary-600 mt-1">
            Active email conversations with AI responses
          </p>
        </div>
        <div className="card-body">
          {threads.length === 0 ? (
            <div className="text-center py-8">
              <MessageSquare className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-secondary-900 mb-2">No Threads Yet</h4>
              <p className="text-secondary-600">
                Start email processing to see conversation threads appear here
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {threads.slice(0, 5).map((thread) => (
                <EnhancedThreadCard
                  key={thread.id}
                  thread={thread}
                  onViewThread={handleViewThread}
                  onForceStopFollowUp={handleForceStopFollowUp}
                  onRestartFollowUp={handleRestartFollowUp}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Test Modal */}
      {showTestModal && (
        <TestModal
          onClose={() => setShowTestModal(false)}
        />
      )}

      {/* IMAP Logs Modal */}
      {showImapLogsModal && (
        <ImapLogsModal
          logs={imapLogs}
          onClose={() => setShowImapLogsModal(false)}
        />
      )}

      {/* Responses Modal */}
      {showResponsesModal && (
        <ResponsesModal
          responses={prospectResponses}
          onClose={() => setShowResponsesModal(false)}
        />
      )}

      {/* Thread Analysis Modal */}
      {showThreadAnalysisModal && threadAnalysis && (
        <ThreadAnalysisModal
          analysis={threadAnalysis}
          onClose={() => setShowThreadAnalysisModal(false)}
          onForceStopFollowUp={handleForceStopFollowUp}
          onRestartFollowUp={handleRestartFollowUp}
        />
      )}

      {/* Thread Detail Modal */}
      {selectedThread && (
        <ThreadDetailModal
          thread={selectedThread}
          onClose={() => setSelectedThread(null)}
        />
      )}
    </div>
  );
};

const EnhancedThreadCard = ({ thread, onViewThread, onForceStopFollowUp, onRestartFollowUp }) => {
  const messageCount = thread.messages?.length || 0;
  const lastMessage = thread.messages?.[messageCount - 1];
  const aiResponses = thread.messages?.filter(m => m.ai_generated)?.length || 0;
  const sentByUs = thread.messages?.filter(m => m.sent_by_us)?.length || 0;

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="flex items-center space-x-4">
        <div className="p-2 bg-blue-100 rounded-full">
          <MessageSquare className="h-4 w-4 text-blue-600" />
        </div>
        <div>
          <h4 className="font-medium text-secondary-900">
            Thread {thread.id.substring(0, 8)}...
          </h4>
          <p className="text-sm text-secondary-600">
            {messageCount} messages • {aiResponses} AI responses • {sentByUs} sent by us
          </p>
          {lastMessage && (
            <p className="text-xs text-secondary-500 mt-1">
              Last activity: {new Date(lastMessage.timestamp).toLocaleString()}
            </p>
          )}
        </div>
      </div>
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onForceStopFollowUp(thread.prospect_id)}
          className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded"
          title="Force stop follow-ups"
        >
          <StopCircle className="h-4 w-4" />
        </button>
        <button
          onClick={() => onRestartFollowUp(thread.prospect_id)}
          className="p-2 text-green-400 hover:text-green-600 hover:bg-green-50 rounded"
          title="Restart follow-ups"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
        <button
          onClick={() => onViewThread(thread)}
          className="p-2 text-secondary-400 hover:text-primary-600"
        >
          <Eye className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

const ImapLogsModal = ({ logs, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-secondary-900">
              IMAP Scan Logs (Last 24 Hours)
            </h3>
            <button
              onClick={onClose}
              className="text-secondary-400 hover:text-secondary-600"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            {logs.length === 0 ? (
              <p className="text-center text-secondary-500 py-8">
                No IMAP logs found
              </p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-medium text-secondary-900">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                    <span className="text-xs text-secondary-500">
                      {log.scan_duration_seconds}s
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-secondary-600">New Emails:</span>
                      <span className="font-medium ml-2">{log.new_emails_found}</span>
                    </div>
                    <div>
                      <span className="text-secondary-600">Processed:</span>
                      <span className="font-medium ml-2">{log.emails_processed}</span>
                    </div>
                    <div>
                      <span className="text-secondary-600">Errors:</span>
                      <span className="font-medium ml-2">{log.errors?.length || 0}</span>
                    </div>
                  </div>
                  {log.errors && log.errors.length > 0 && (
                    <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-700">
                      {log.errors.map((error, i) => (
                        <div key={i}>{error}</div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ResponsesModal = ({ responses, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-secondary-900">
              Recent Prospect Responses (Last 7 Days)
            </h3>
            <button
              onClick={onClose}
              className="text-secondary-400 hover:text-secondary-600"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            {responses.length === 0 ? (
              <p className="text-center text-secondary-500 py-8">
                No recent responses found
              </p>
            ) : (
              responses.map((response, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-medium text-secondary-900">
                        {response.prospect.email}
                      </h4>
                      <p className="text-sm text-secondary-600">
                        {response.prospect.first_name} {response.prospect.last_name}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded ${
                      response.response_type === 'manual' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {response.response_type}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-secondary-600">Follow-ups sent:</span>
                      <span className="font-medium ml-2">{response.follow_up_history.length}</span>
                    </div>
                    <div>
                      <span className="text-secondary-600">Responded:</span>
                      <span className="font-medium ml-2">
                        {new Date(response.prospect.responded_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ThreadAnalysisModal = ({ analysis, onClose, onForceStopFollowUp, onRestartFollowUp }) => {
  const { prospect, analysis: threadAnalysis, messages, follow_up_history } = analysis;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-5xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-secondary-900">
              Thread Analysis - {prospect.email}
            </h3>
            <button
              onClick={onClose}
              className="text-secondary-400 hover:text-secondary-600"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-6">
            {/* Prospect Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-secondary-900 mb-2">Prospect Details</h4>
                <p className="text-sm text-secondary-600">
                  <span className="font-medium">Name:</span> {prospect.first_name} {prospect.last_name}
                </p>
                <p className="text-sm text-secondary-600">
                  <span className="font-medium">Company:</span> {prospect.company}
                </p>
                <p className="text-sm text-secondary-600">
                  <span className="font-medium">Status:</span> {prospect.follow_up_status}
                </p>
              </div>
              
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-secondary-900 mb-2">Thread Analytics</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-secondary-600">Total Messages:</span>
                    <span className="font-medium ml-2">{threadAnalysis.total_messages}</span>
                  </div>
                  <div>
                    <span className="text-secondary-600">Sent by Us:</span>
                    <span className="font-medium ml-2">{threadAnalysis.sent_by_us}</span>
                  </div>
                  <div>
                    <span className="text-secondary-600">Received:</span>
                    <span className="font-medium ml-2">{threadAnalysis.received_from_prospect}</span>
                  </div>
                  <div>
                    <span className="text-secondary-600">Follow-ups:</span>
                    <span className="font-medium ml-2">{threadAnalysis.follow_up_count}</span>
                  </div>
                </div>
                {threadAnalysis.response_time_seconds && (
                  <p className="text-sm text-secondary-600 mt-2">
                    <span className="font-medium">Response Time:</span> {Math.round(threadAnalysis.response_time_seconds / 3600)}h
                  </p>
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="flex space-x-4">
              <button
                onClick={() => onForceStopFollowUp(prospect.id)}
                className="btn btn-secondary"
              >
                <StopCircle className="h-4 w-4 mr-2" />
                Force Stop Follow-ups
              </button>
              <button
                onClick={() => onRestartFollowUp(prospect.id)}
                className="btn btn-primary"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Restart Follow-ups
              </button>
            </div>

            {/* Messages */}
            <div>
              <h4 className="font-semibold text-secondary-900 mb-4">Thread Messages</h4>
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg ${
                      message.sent_by_us 
                        ? 'bg-blue-50 border border-blue-200' 
                        : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          message.sent_by_us 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {message.sent_by_us ? 'Sent by Us' : 'Received'}
                        </span>
                        {message.is_follow_up && (
                          <span className="px-2 py-1 text-xs rounded bg-purple-100 text-purple-800">
                            Follow-up #{message.follow_up_sequence}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-secondary-500">
                        {new Date(message.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-secondary-900">{message.subject}</p>
                    <p className="text-xs text-secondary-600 mt-1">
                      {message.content.substring(0, 100)}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const TestModal = ({ onClose }) => {
  const [testData, setTestData] = useState({
    subject: '',
    content: '',
    prospect_id: ''
  });
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    if (!testData.content) {
      toast.error('Email content is required');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.testIntentClassification(testData);
      setTestResult(response.data);
      toast.success('AI classification completed');
    } catch (error) {
      toast.error('Failed to test classification');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-3xl w-full p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">
            Test AI Classification
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Email Subject
              </label>
              <input
                type="text"
                value={testData.subject}
                onChange={(e) => setTestData({...testData, subject: e.target.value})}
                className="input"
                placeholder="Enter email subject..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1">
                Email Content *
              </label>
              <textarea
                value={testData.content}
                onChange={(e) => setTestData({...testData, content: e.target.value})}
                className="input"
                rows="6"
                placeholder="Enter email content to test..."
              />
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={handleTest}
                disabled={loading}
                className="btn btn-primary"
              >
                {loading ? 'Testing...' : 'Test Classification'}
              </button>
              <button
                onClick={onClose}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
          
          {testResult && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-secondary-900 mb-3">Test Results</h4>
              
              <div className="space-y-3">
                <div>
                  <h5 className="font-medium text-secondary-700">Classified Intents:</h5>
                  {testResult.classified_intents?.map((intent, index) => (
                    <div key={index} className="ml-4 p-2 bg-white rounded border">
                      <div className="flex justify-between">
                        <span className="font-medium">{intent.intent_name}</span>
                        <span className="text-sm text-green-600">
                          {(intent.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm text-secondary-600">{intent.reasoning}</p>
                    </div>
                  ))}
                </div>
                
                {testResult.sentiment_analysis && (
                  <div>
                    <h5 className="font-medium text-secondary-700">Sentiment Analysis:</h5>
                    <div className="ml-4 p-2 bg-white rounded border">
                      <div className="flex space-x-4">
                        <span>Sentiment: <strong>{testResult.sentiment_analysis.sentiment}</strong></span>
                        <span>Urgency: <strong>{testResult.sentiment_analysis.urgency}</strong></span>
                        <span>Emotion: <strong>{testResult.sentiment_analysis.emotion_detected}</strong></span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ThreadDetailModal = ({ thread, onClose }) => {
  const messages = thread.messages || [];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black opacity-30"></div>
        <div className="relative bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-secondary-900">
              Thread Details - {thread.id.substring(0, 8)}...
            </h3>
            <button
              onClick={onClose}
              className="text-secondary-400 hover:text-secondary-600"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg ${
                  message.type === 'sent' 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      message.type === 'sent' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {message.type === 'sent' ? 'Sent' : 'Received'}
                    </span>
                    {message.ai_generated && (
                      <span className="px-2 py-1 text-xs rounded bg-purple-100 text-purple-800">
                        AI Generated
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-secondary-500">
                    {new Date(message.timestamp).toLocaleString()}
                  </span>
                </div>
                
                <div className="mb-2">
                  <p className="font-medium text-secondary-900">{message.subject}</p>
                </div>
                
                <div className="text-sm text-secondary-600">
                  <div dangerouslySetInnerHTML={{ __html: message.content }} />
                </div>
              </div>
            ))}
            
            {messages.length === 0 && (
              <p className="text-center text-secondary-500 py-8">
                No messages in this thread yet
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailProcessing;