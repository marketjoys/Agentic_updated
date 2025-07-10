import React, { useState, useEffect } from 'react';
import { Play, Pause, Brain, MessageSquare, TrendingUp, AlertCircle, CheckCircle, Mail, Eye, Send } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const EmailProcessing = () => {
  const [processingStatus, setProcessingStatus] = useState('stopped');
  const [analytics, setAnalytics] = useState({
    total_threads: 0,
    processed_emails: 0,
    auto_responses_sent: 0,
    processing_status: 'stopped'
  });
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTestModal, setShowTestModal] = useState(false);
  const [selectedThread, setSelectedThread] = useState(null);

  useEffect(() => {
    loadData();
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statusResponse, analyticsResponse, threadsResponse] = await Promise.all([
        apiService.getProcessingStatus(),
        apiService.getProcessingAnalytics(),
        apiService.getThreads()
      ]);

      setProcessingStatus(statusResponse.data.status);
      setAnalytics(analyticsResponse.data);
      setThreads(threadsResponse.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartProcessing = async () => {
    try {
      const response = await apiService.startEmailProcessing();
      toast.success('Email processing started successfully');
      setProcessingStatus('running');
      loadData();
    } catch (error) {
      toast.error('Failed to start email processing');
    }
  };

  const handleStopProcessing = async () => {
    try {
      const response = await apiService.stopEmailProcessing();
      toast.success('Email processing stopped');
      setProcessingStatus('stopped');
      loadData();
    } catch (error) {
      toast.error('Failed to stop email processing');
    }
  };

  const handleViewThread = (thread) => {
    setSelectedThread(thread);
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
          <h1 className="text-3xl font-bold text-secondary-900">AI Email Processing</h1>
          <p className="text-secondary-600 mt-1">
            Automatic email monitoring and intelligent response system
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
          {processingStatus === 'running' ? (
            <button
              onClick={handleStopProcessing}
              className="btn btn-secondary"
            >
              <Pause className="h-4 w-4 mr-2" />
              Stop Processing
            </button>
          ) : (
            <button
              onClick={handleStartProcessing}
              className="btn btn-primary"
            >
              <Play className="h-4 w-4 mr-2" />
              Start Processing
            </button>
          )}
        </div>
      </div>

      {/* Status Card */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-full ${
                processingStatus === 'running' 
                  ? 'bg-green-100 text-green-600' 
                  : 'bg-red-100 text-red-600'
              }`}>
                {processingStatus === 'running' ? 
                  <CheckCircle className="h-5 w-5" /> : 
                  <AlertCircle className="h-5 w-5" />
                }
              </div>
              <div>
                <h3 className="text-lg font-semibold text-secondary-900">
                  Email Processing Status
                </h3>
                <p className="text-sm text-secondary-600">
                  {processingStatus === 'running' 
                    ? 'System is actively monitoring emails and generating responses'
                    : 'Email processing is currently stopped'
                  }
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                processingStatus === 'running' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {processingStatus.toUpperCase()}
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
                <p className="text-sm text-secondary-600">Success Rate</p>
                <p className="text-2xl font-bold text-secondary-900">
                  {analytics.processed_emails > 0 
                    ? Math.round((analytics.auto_responses_sent / analytics.processed_emails) * 100)
                    : 0}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-emerald-600" />
            </div>
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
                <ThreadCard
                  key={thread.id}
                  thread={thread}
                  onViewThread={handleViewThread}
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

const ThreadCard = ({ thread, onViewThread }) => {
  const messageCount = thread.messages?.length || 0;
  const lastMessage = thread.messages?.[messageCount - 1];
  const aiResponses = thread.messages?.filter(m => m.ai_generated)?.length || 0;

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
            {messageCount} messages • {aiResponses} AI responses
          </p>
          {lastMessage && (
            <p className="text-xs text-secondary-500 mt-1">
              Last activity: {new Date(lastMessage.timestamp).toLocaleString()}
            </p>
          )}
        </div>
      </div>
      <button
        onClick={() => onViewThread(thread)}
        className="p-2 text-secondary-400 hover:text-primary-600"
      >
        <Eye className="h-4 w-4" />
      </button>
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