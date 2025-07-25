// Voice/Chat Interface for AI Agent - React Component with Wake Word
import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, MessageCircle, Headphones, Volume2, VolumeX, Settings } from 'lucide-react';
import { toast } from 'react-hot-toast';
import apiService from '../services/api';
import useWakeWordDetection from '../hooks/useWakeWordDetection';
import VoiceIndicator from './VoiceIndicator';

const AIAgentChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(true); // Default to enabled for wake word
  const [suggestions, setSuggestions] = useState([]);
  
  const messagesEndRef = useRef(null);
  const websocketRef = useRef(null);
  const recognitionRef = useRef(null);

  // Wake word detection
  const {
    isListeningForWakeWord,
    isAwake,
    error: wakeWordError,
    goToSleep,
    resetActivity,
    startWakeWordListening,
    stopWakeWordListening
  } = useWakeWordDetection(
    () => {
      // When wake word is detected, automatically start listening for command
      setTimeout(() => startVoiceRecognition(true), 1000);
    },
    voiceEnabled
  );
  
  useEffect(() => {
    // Generate session ID
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    
    // Add welcome message
    setMessages([{
      id: 'welcome',
      type: 'agent',
      content: "Hello! I'm Joy, your AI assistant. Say 'Hello Joy' to activate voice mode, or just type your message. I can help you manage campaigns, prospects, templates, and much more!",
      suggestions: [
        "Hello Joy",
        "Show me all my campaigns",
        "Create a new prospect",
        "What are my analytics?",
        "Upload prospects from CSV"
      ],
      timestamp: new Date()
    }]);
    
    setSuggestions([
      "Hello Joy",
      "Show me all my campaigns", 
      "Create a new prospect",
      "What are my analytics?",
      "Upload prospects from CSV"
    ]);

    // Auto-speak welcome message if voice is enabled
    if (voiceEnabled) {
      setTimeout(() => {
        speakResponse("Hello! I'm Joy, your AI assistant. Say 'Hello Joy' to wake me up anytime.");
      }, 1000);
    }
  }, [voiceEnabled]);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
  const connectWebSocket = () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const wsUrl = backendUrl.replace('http', 'ws') + `/api/ai-agent/ws/${sessionId}`;
      
      websocketRef.current = new WebSocket(wsUrl);
      
      websocketRef.current.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
        toast.success('Connected to AI Agent');
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
          timestamp: new Date(response.timestamp)
        };
        
        setMessages(prev => [...prev, agentMessage]);
        setSuggestions(response.suggestions || []);
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
  };
  
  const sendMessage = async (message) => {
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
      if (isConnected && websocketRef.current) {
        // Send via WebSocket
        websocketRef.current.send(JSON.stringify({
          message: message,
          user_id: 'default',
          context: {}
        }));
      } else {
        // Send via HTTP API
        const response = await apiService.post('/api/ai-agent/chat', {
          message: message,
          user_id: 'default',
          session_id: sessionId,
          context: {}
        });
        
        const agentMessage = {
          id: `agent_${Date.now()}`,
          type: 'agent',
          content: response.data.response,
          actionTaken: response.data.action_taken,
          data: response.data.data,
          suggestions: response.data.suggestions || [],
          timestamp: new Date(response.data.timestamp)
        };
        
        setMessages(prev => [...prev, agentMessage]);
        setSuggestions(response.data.suggestions || []);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Detailed error sending message:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Error message:', error.message);
      
      toast.error(`Failed to send message: ${error.message}`);
      setIsLoading(false);
      
      // Add detailed error message for debugging
      const errorMessage = {
        id: `error_${Date.now()}`,
        type: 'agent',
        content: `I apologize, but I'm having trouble processing your request right now. 
        
Error details: ${error.message}
Status: ${error.response?.status || 'Unknown'}
Response: ${JSON.stringify(error.response?.data) || 'No response data'}

Please try again or ask for help.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };
  
  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };
  
  const startVoiceRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice recognition not supported in this browser');
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
      toast.error(`Voice recognition error: ${event.error}`);
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    recognition.start();
  };
  
  const speakResponse = (text) => {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    speechSynthesis.speak(utterance);
  };
  
  const clearChat = () => {
    setMessages([]);
    setSuggestions([]);
    toast.success('Chat cleared');
  };
  
  const formatMessage = (message) => {
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
      } else if (message.actionTaken === 'show_analytics' && message.data) {
        content += '\n📊 **Analytics Summary:**';
        content += `\n• Campaigns: ${message.data.total_campaigns}`;
        content += `\n• Prospects: ${message.data.total_prospects}`;
        content += `\n• Emails Sent: ${message.data.total_emails_sent}`;
        content += `\n• Open Rate: ${message.data.average_open_rate}%`;
      }
    }
    
    return content;
  };
  
  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <MessageCircle className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI Agent Assistant</h1>
            <p className="text-sm text-gray-500">
              {isConnected ? '🟢 Connected via WebSocket' : '🔴 HTTP Mode'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
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
            onClick={connectWebSocket}
            disabled={isConnected}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {isConnected ? 'Connected' : 'Connect WS'}
          </button>
          
          <button
            onClick={clearChat}
            className="px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
          >
            Clear Chat
          </button>
        </div>
      </div>
      
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
              
              {/* Action indicator */}
              {message.actionTaken && (
                <div className="mt-2 text-xs opacity-75">
                  ⚡ Action: {message.actionTaken.replace('_', ' ')}
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
                <span className="text-gray-600">AI is thinking...</span>
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
              placeholder="Ask me anything... 'Show my campaigns', 'Create a new prospect', etc."
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
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              }`}
              title="Voice input"
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
          Try: "Show my campaigns" • "Create prospect John Doe from TechCorp" • "What are my analytics?" • "Send Summer Sale campaign"
        </div>
      </div>
    </div>
  );
};

export default AIAgentChat;