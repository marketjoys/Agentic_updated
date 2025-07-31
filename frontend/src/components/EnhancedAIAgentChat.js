// Enhanced Voice/Chat Interface for AI Agent with Confirmation Flow
import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { 
  Send, Mic, MicOff, MessageCircle, Volume2, VolumeX, Settings, 
  CheckCircle, AlertCircle, Zap, History
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import api from '../services/api';

const EnhancedAIAgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  
  // Enhanced features
  const [useEnhancedFlow, setUseEnhancedFlow] = useState(true);
  const [conversationState, setConversationState] = useState('analyzing');
  const [pendingAction, setPendingAction] = useState(null);
  const [contextInfo, setContextInfo] = useState({});
  const [turnLimit, setTurnLimit] = useState(10);
  const [showSettings, setShowSettings] = useState(false);
  
  const messagesEndRef = useRef(null);
  const websocketRef = useRef(null);
  const welcomeMessageInitialized = useRef(false);
  
  // Memoize welcome message to prevent recreation
  const welcomeMessage = useMemo(() => ({
    id: 'welcome',
    type: 'agent',
    content: useEnhancedFlow 
      ? "Hello! I'm your Enhanced AI assistant with confirmation flow. I'll ask for your confirmation before performing any actions. Tell me what you'd like to do!" 
      : "Hello! I'm your AI assistant. I can help you manage campaigns, prospects, templates, and much more. Just tell me what you'd like to do in natural language!",
    suggestions: [
      "Show me all my campaigns",
      "Create a new campaign named Summer Sale",
      "Add John Smith from TechCorp",
      "What are my analytics?",
      "Set turn limit to 25"
    ],
    timestamp: new Date(),
    conversationState: 'analyzing'
  }), [useEnhancedFlow]);

  // Initialize session ID only once
  useEffect(() => {
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  // Initialize welcome message only once
  useEffect(() => {
    if (!welcomeMessageInitialized.current) {
      setMessages([welcomeMessage]);
      setSuggestions(welcomeMessage.suggestions);
      welcomeMessageInitialized.current = true;
    }
  }, [welcomeMessage]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);
  
  const connectWebSocket = useCallback(() => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const wsUrl = backendUrl.replace('http', 'ws') + `/api/ai-agent/ws/${sessionId}?enhanced=${useEnhancedFlow}`;
      
      if (websocketRef.current) {
        websocketRef.current.close();
      }
      
      websocketRef.current = new WebSocket(wsUrl);
      
      websocketRef.current.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
        toast.success('Connected to Enhanced AI Agent');
      };
      
      websocketRef.current.onmessage = (event) => {
        const response = JSON.parse(event.data);
        
        const agentMessage = {
          id: `agent_${Date.now()}`,
          type: 'agent',
          content: response.response,
          actionTaken: response.action_taken,
          data: response.data,
          suggestions: response.suggestions || [],
          conversationState: response.conversation_state,
          pendingAction: response.pending_action,
          contextInfo: response.context_info,
          timestamp: new Date(response.timestamp)
        };
        
        setMessages(prev => [...prev, agentMessage]);
        setSuggestions(response.suggestions || []);
        setConversationState(response.conversation_state || 'analyzing');
        setPendingAction(response.pending_action);
        setContextInfo(response.context_info || {});
        setIsLoading(false);
      };
      
      websocketRef.current.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
      };
      
      websocketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setIsLoading(false);
        toast.error('Connection error');
      };
      
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      toast.error('Failed to connect to AI Agent');
    }
  }, [sessionId, useEnhancedFlow]);
  
  const sendMessage = useCallback(async (message) => {
    if (!message.trim()) return;
    
    // Add user message
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      if (isConnected && websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        // Send via WebSocket
        websocketRef.current.send(JSON.stringify({
          message: message,
          user_id: 'default',
          use_enhanced_flow: useEnhancedFlow,
          context: {}
        }));
      } else {
        // Send via HTTP API
        const response = await api.post('/api/ai-agent/chat', {
          message: message,
          user_id: 'default',
          session_id: sessionId,
          use_enhanced_flow: useEnhancedFlow,
          context: {}
        });
        
        const agentMessage = {
          id: `agent_${Date.now()}`,
          type: 'agent',
          content: response.data.response,
          actionTaken: response.data.action_taken,
          data: response.data.data,
          suggestions: response.data.suggestions || [],
          conversationState: response.data.conversation_state,
          pendingAction: response.data.pending_action,
          contextInfo: response.data.context_info,
          timestamp: new Date(response.data.timestamp)
        };
        
        setMessages(prev => [...prev, agentMessage]);
        setSuggestions(response.data.suggestions || []);
        setConversationState(response.data.conversation_state || 'analyzing');
        setPendingAction(response.data.pending_action);
        setContextInfo(response.data.context_info || {});
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error(`Failed to send message: ${error.message}`);
      setIsLoading(false);
      
      const errorMessage = {
        id: `error_${Date.now()}`,
        type: 'agent',
        content: `I apologize, but I'm having trouble processing your request right now. Error: ${error.message}. Please try again.`,
        timestamp: new Date(),
        conversationState: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  }, [isConnected, sessionId, useEnhancedFlow]);
  
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  }, [sendMessage, inputMessage]);
  
  const handleSuggestionClick = useCallback((suggestion) => {
    sendMessage(suggestion);
  }, [sendMessage]);
  
  const updateTurnLimit = useCallback(async (newLimit) => {
    try {
      await api.post('/api/ai-agent/set-turn-limit', {
        session_id: sessionId,
        max_turns: newLimit
      });
      setTurnLimit(newLimit);
      toast.success(`Turn limit updated to ${newLimit}`);
    } catch (error) {
      toast.error('Failed to update turn limit');
    }
  }, [sessionId]);
  
  const loadConversationHistory = useCallback(async () => {
    try {
      const response = await api.get(`/api/ai-agent/conversation-history/${sessionId}`);
      toast.success('Conversation history loaded');
    } catch (error) {
      toast.error('Failed to load conversation history');
    }
  }, [sessionId]);
  
  const clearConversation = useCallback(async () => {
    try {
      await api.delete(`/api/ai-agent/sessions/${sessionId}?enhanced=${useEnhancedFlow}`);
      setMessages([welcomeMessage]);
      setSuggestions(welcomeMessage.suggestions);
      setConversationState('analyzing');
      setPendingAction(null);
      setContextInfo({});
      toast.success('Conversation cleared');
    } catch (error) {
      toast.error('Failed to clear conversation');
    }
  }, [sessionId, useEnhancedFlow, welcomeMessage]);
  
  const startVoiceRecognition = useCallback(async () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice recognition not supported in this browser');
      return;
    }
    
    // Check if we have microphone permission first
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop()); // Stop immediately, we just needed permission
    } catch (error) {
      if (error.name === 'NotAllowedError') {
        toast.error('Microphone permission denied. Please allow microphone access.');
      } else {
        toast.error(`Microphone error: ${error.message}`);
      }
      return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    recognition.onstart = () => {
      setIsListening(true);
      toast('Listening... Speak now', { icon: '🎤' });
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputMessage(transcript);
      toast.success(`Heard: "${transcript}"`);
    };
    
    recognition.onerror = (event) => {
      setIsListening(false);
      if (event.error === 'not-allowed') {
        toast.error('Microphone permission denied. Please allow microphone access.');
      } else if (event.error === 'no-speech') {
        toast.error('No speech detected. Please try again.');
      } else if (event.error === 'network') {
        toast.error('Network error. Check your internet connection.');
      } else if (event.error !== 'aborted') {
        toast.error(`Voice recognition error: ${event.error}`);
      }
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    try {
      recognition.start();
    } catch (error) {
      setIsListening(false);
      toast.error('Failed to start voice recognition');
    }
  }, []);
  
  const getStateIcon = useCallback((state) => {
    switch (state) {
      case 'analyzing': return <MessageCircle className="h-4 w-4" />;
      case 'gathering_info': return <AlertCircle className="h-4 w-4" />;
      case 'confirming': return <CheckCircle className="h-4 w-4" />;
      case 'executing': return <Zap className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'error': return <AlertCircle className="h-4 w-4" />;
      default: return <MessageCircle className="h-4 w-4" />;
    }
  }, []);
  
  const getStateColor = useCallback((state) => {
    switch (state) {
      case 'analyzing': return 'text-blue-600';
      case 'gathering_info': return 'text-yellow-600';
      case 'confirming': return 'text-orange-600';
      case 'executing': return 'text-purple-600';
      case 'completed': return 'text-green-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  }, []);
  
  const formatMessage = useCallback((message) => {
    let content = message.content;
    
    // Format action results
    if (message.actionTaken && message.data) {
      content += '\n\n---';
      if (message.actionTaken === 'list_campaigns' && Array.isArray(message.data)) {
        content += '\n📋 **Campaigns Found:**';
        message.data.slice(0, 5).forEach(campaign => {
          content += `\n• ${campaign.name} (${campaign.status})`;
        });
        if (message.data.length > 5) {
          content += `\n• ... and ${message.data.length - 5} more`;
        }
      } else if (message.actionTaken === 'list_prospects' && Array.isArray(message.data)) {
        content += '\n👥 **Prospects Found:**';
        message.data.slice(0, 5).forEach(prospect => {
          content += `\n• ${prospect.first_name} ${prospect.last_name} - ${prospect.company || 'No company'}`;
        });
        if (message.data.length > 5) {
          content += `\n• ... and ${message.data.length - 5} more`;
        }
      }
    }
    
    return content;
  }, []);
  
  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            {getStateIcon(conversationState)}
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {useEnhancedFlow ? 'Enhanced AI Agent' : 'AI Agent'} Assistant
            </h1>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <span className={`flex items-center space-x-1 ${getStateColor(conversationState)}`}>
                {getStateIcon(conversationState)}
                <span className="capitalize">{conversationState.replace('_', ' ')}</span>
              </span>
              <span>•</span>
              <span>{isConnected ? '🟢 Connected via WebSocket' : '🔴 HTTP Mode'}</span>
              {contextInfo.turn_count !== undefined && (
                <>
                  <span>•</span>
                  <span>{contextInfo.turn_count}/{contextInfo.max_turns || turnLimit} turns</span>
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setUseEnhancedFlow(!useEnhancedFlow)}
            className={`px-3 py-2 rounded-lg text-sm transition-colors ${
              useEnhancedFlow 
                ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            title="Toggle enhanced confirmation flow"
          >
            {useEnhancedFlow ? 'Enhanced' : 'Legacy'}
          </button>
          
          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className={`p-2 rounded-lg transition-colors ${
              voiceEnabled ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'
            }`}
            title="Toggle voice responses"
          >
            {voiceEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
          </button>
          
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
            title="Settings"
          >
            <Settings className="h-5 w-5" />
          </button>
          
          <button
            onClick={loadConversationHistory}
            className="p-2 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
            title="Load conversation history"
          >
            <History className="h-5 w-5" />
          </button>
          
          <button
            onClick={connectWebSocket}
            disabled={isConnected}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {isConnected ? 'Connected' : 'Connect WS'}
          </button>
          
          <button
            onClick={clearConversation}
            className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
          >
            Clear Chat
          </button>
        </div>
      </div>
      
      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-yellow-50 border-b p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Conversation Settings</h3>
            <button
              onClick={() => setShowSettings(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Turn Limit (10-100)
              </label>
              <input
                type="number"
                min="10"
                max="100"
                value={turnLimit}
                onChange={(e) => setTurnLimit(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <button
                onClick={() => updateTurnLimit(turnLimit)}
                className="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Update Turn Limit
              </button>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Context Info
              </label>
              <div className="text-sm text-gray-600">
                <p>State: <span className="font-medium">{conversationState}</span></p>
                <p>Extracted Params: <span className="font-medium">{Object.keys(contextInfo.extracted_params || {}).length}</span></p>
                <p>Missing Params: <span className="font-medium">{(contextInfo.missing_params || []).length}</span></p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Pending Action Notice */}
      {pendingAction && (
        <div className="bg-orange-50 border-b p-3">
          <div className="flex items-start space-x-2">
            <CheckCircle className="h-5 w-5 text-orange-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-orange-800">
                Action Waiting for Confirmation
              </p>
              <p className="text-sm text-orange-700">
                {pendingAction.action?.replace('_', ' ')} - Please confirm to proceed
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl px-4 py-3 rounded-lg shadow-sm ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 border'
              }`}
            >
              <div className="whitespace-pre-wrap">{formatMessage(message)}</div>
              
              {/* Enhanced message indicators */}
              {message.conversationState && message.type === 'agent' && (
                <div className="mt-2 flex items-center space-x-2 text-xs opacity-75">
                  {getStateIcon(message.conversationState)}
                  <span>State: {message.conversationState.replace('_', ' ')}</span>
                  {message.actionTaken && (
                    <>
                      <span>•</span>
                      <span>Action: {message.actionTaken.replace('_', ' ')}</span>
                    </>
                  )}
                </div>
              )}
              
              <div className="text-xs mt-1 opacity-70">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border rounded-lg px-4 py-3 shadow-sm">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-gray-600">
                  {conversationState === 'analyzing' && 'Analyzing your request...'}
                  {conversationState === 'gathering_info' && 'Processing information...'}
                  {conversationState === 'confirming' && 'Preparing confirmation...'}
                  {conversationState === 'executing' && 'Executing action...'}
                  {!conversationState && 'AI is thinking...'}
                </span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="px-4 py-2 border-t bg-gray-50">
          <div className="text-sm text-gray-600 mb-2">💡 Suggested actions:</div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1 bg-white border border-blue-200 text-blue-700 rounded-full text-sm hover:bg-blue-50 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <form onSubmit={handleSubmit} className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                conversationState === 'gathering_info' 
                  ? "Please provide the requested information..." 
                  : conversationState === 'confirming'
                  ? "Say 'yes' to confirm, 'no' to cancel, or 'change' to modify..."
                  : "Ask me anything... 'Show my campaigns', 'Create a new prospect', etc."
              }
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            
            <button
              type="button"
              onClick={startVoiceRecognition}
              disabled={isListening || isLoading}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full transition-colors ${
                isListening 
                  ? 'text-red-600 bg-red-100' 
                  : 'text-blue-600 bg-blue-100 hover:bg-blue-200'
              }`}
              title="Voice input - Click to enable microphone"
            >
              {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>
          </div>
          
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </form>
        
        <div className="mt-2 text-xs text-gray-500 text-center">
          {useEnhancedFlow ? (
            <>Enhanced Mode: Actions require confirmation • Try: "Create campaign Summer Sale" • "Yes, proceed" • "Set turn limit to 25"</>
          ) : (
            <>Legacy Mode: Direct execution • Try: "Show my campaigns" • "Create prospect John Doe from TechCorp"</>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedAIAgentChat;