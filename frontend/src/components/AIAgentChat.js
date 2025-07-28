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
    stopWakeWordListening,
    activateVoiceMode,
    requestPermission,
    permissionGranted,
    forceRestartListening
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
    
    // Reset activity timer when sending message
    resetActivity();
    
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
        
        // Speak response if voice is enabled and user is awake
        if (voiceEnabled && isAwake) {
          setTimeout(() => speakResponse(response.data.response), 500);
        }
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
  
  const startVoiceRecognition = (autoSend = false) => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice recognition not supported in this browser');
      return;
    }
    
    // Reset activity timer when user interacts
    resetActivity();
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    
    // Windows-optimized settings
    recognitionRef.current.lang = 'en-US';
    recognitionRef.current.interimResults = false;
    recognitionRef.current.maxAlternatives = 1;
    recognitionRef.current.continuous = false; // Set to false for single command
    
    // Windows compatibility: Add service hints
    if (window.webkitSpeechRecognition) {
      recognitionRef.current.serviceURI = 'wss://www.google.com/speech-api/full-duplex/v1/up';
    }
    
    recognitionRef.current.onstart = () => {
      setIsListening(true);
      toast('🎤 Listening... Speak now', { 
        icon: '🎤',
        duration: 2000 
      });
    };
    
    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      
      // Check for sleep command
      if (transcript.toLowerCase().includes('sleep') || transcript.toLowerCase().includes('go to sleep')) {
        toast('Going to sleep. Say "Hello Joy" to wake me up.', { icon: '😴' });
        goToSleep();
        return;
      }
      
      setInputMessage(transcript);
      toast.success(`Heard: "${transcript}"`);
      
      // Auto-send if triggered by wake word
      if (autoSend) {
        setTimeout(() => sendMessage(transcript), 500);
      }
    };
    
    recognitionRef.current.onerror = (event) => {
      setIsListening(false);
      console.error('Voice recognition error:', event.error);
      
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
    
    recognitionRef.current.onend = () => {
      setIsListening(false);
    };
    
    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      toast.error('Failed to start voice recognition');
      setIsListening(false);
    }
  };
  
  const speakResponse = (text) => {
    if (!voiceEnabled || !('speechSynthesis' in window) || !isAwake) return;
    
    setIsSpeaking(true);
    
    // Clean up text for better speech
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove markdown bold
      .replace(/\*(.*?)\*/g, '$1') // Remove markdown italic
      .replace(/#{1,6}\s/g, '') // Remove markdown headers
      .replace(/```[\s\S]*?```/g, 'code block') // Replace code blocks
      .replace(/`([^`]+)`/g, '$1') // Remove inline code
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Replace links with text
      .replace(/---+/g, '') // Remove horizontal rules
      .replace(/\n{3,}/g, '\n\n') // Reduce multiple newlines
      .substring(0, 300); // Limit length for speech
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1.1;
    utterance.volume = 0.9;
    
    utterance.onstart = () => {
      resetActivity();
    };
    
    utterance.onend = () => {
      setIsSpeaking(false);
      resetActivity();
    };
    
    utterance.onerror = () => {
      setIsSpeaking(false);
    };
    
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
            <h1 className="text-xl font-bold text-gray-900">Joy - AI Agent Assistant</h1>
            <p className="text-sm text-gray-500">
              {isConnected ? '🟢 Connected via WebSocket' : '🔴 HTTP Mode'}
            </p>
          </div>
        </div>
        
        {/* Voice Indicator */}
        <VoiceIndicator
          isListeningForWakeWord={isListeningForWakeWord}
          isAwake={isAwake}
          isListening={isListening}
          isSpeaking={isSpeaking}
          error={wakeWordError}
          voiceEnabled={voiceEnabled}
          permissionGranted={permissionGranted}
          onToggleVoice={() => setVoiceEnabled(!voiceEnabled)}
          onGoToSleep={goToSleep}
          onRequestPermission={requestPermission}
        />
        
        <div className="flex items-center space-x-2">
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
              onClick={async () => {
                if (!permissionGranted || !isAwake) {
                  // If no permission or not awake, try to activate voice mode first
                  const activated = await activateVoiceMode();
                  if (activated) {
                    // Small delay then start voice recognition
                    setTimeout(() => startVoiceRecognition(false), 500);
                  }
                } else {
                  // If already awake and have permission, start voice recognition directly
                  startVoiceRecognition(false);
                }
              }}
              disabled={isListening || isLoading}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full transition-colors ${
                isListening 
                  ? 'text-red-600 bg-red-100' 
                  : permissionGranted && isAwake
                  ? 'text-blue-600 bg-blue-100 hover:bg-blue-200' 
                  : 'text-gray-600 bg-gray-100 hover:bg-gray-200'
              }`}
              title={
                !permissionGranted 
                  ? "Click to enable microphone and voice commands" 
                  : !isAwake 
                  ? "Click to activate voice mode" 
                  : "Voice input (or say 'Hello Joy' to wake up)"
              }
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
          {isAwake 
            ? "🎙️ Voice activated! Say 'sleep' to deactivate • Try: \"Show my campaigns\" • \"Create prospect John Doe from TechCorp\""
            : permissionGranted
            ? "💤 Say \"Hello Joy\" to activate voice mode or click the microphone • Try: \"Show campaigns\" • \"Create prospect\" • \"Analytics\""
            : "🎤 Click the microphone to enable voice commands • Or type: \"Show campaigns\" • \"Create prospect\" • \"Analytics\""
          }
        </div>
      </div>
    </div>
  );
};

export default AIAgentChat;