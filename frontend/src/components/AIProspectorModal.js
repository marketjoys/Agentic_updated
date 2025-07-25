import React, { useState, useEffect } from 'react';
import { X, Search, Sparkles, Users, Building, MapPin, AlertCircle, CheckCircle, Clock, Brain, Mic, MicOff } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';
import useWakeWordDetection from '../hooks/useWakeWordDetection';
import VoiceIndicator from './VoiceIndicator';

const AIProspectorModal = ({ isOpen, onClose, onProspectsAdded }) => {
  const [step, setStep] = useState('query'); // query, clarification, searching, results
  const [query, setQuery] = useState('');
  const [targetList, setTargetList] = useState('');
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [clarificationQuestions, setClarificationQuestions] = useState([]);
  const [clarifications, setClarifications] = useState({});
  const [extractedParameters, setExtractedParameters] = useState(null);
  
  // Voice capabilities
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Wake word detection for Auto Prospector
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
    permissionGranted
  } = useWakeWordDetection(
    () => {
      // When wake word is detected in prospector, start listening for search query
      setTimeout(() => startVoiceRecognition(true), 1000);
    },
    voiceEnabled && isOpen
  );

  useEffect(() => {
    if (isOpen) {
      loadLists();
      resetModal();
    }
  }, [isOpen]);

  const resetModal = () => {
    setStep('query');
    setQuery('');
    setTargetList('');
    setSearchResults(null);
    setClarificationQuestions([]);
    setClarifications({});
    setExtractedParameters(null);
  };

  const loadLists = async () => {
    try {
      const response = await apiService.getLists();
      setLists(response.data || []);
    } catch (error) {
      console.error('Failed to load lists:', error);
    }
  };

  const startVoiceRecognition = (autoSearch = false) => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Voice recognition not supported in this browser');
      return;
    }
    
    resetActivity();
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    recognition.onstart = () => {
      setIsListening(true);
      toast('🎤 Listening for your prospect search...', { 
        icon: '🎤',
        duration: 1000 
      });
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      
      // Check for sleep command
      if (transcript.toLowerCase().includes('sleep') || transcript.toLowerCase().includes('go to sleep')) {
        toast('Going to sleep. Say "Hello Joy" to wake me up.', { icon: '😴' });
        goToSleep();
        return;
      }
      
      setQuery(transcript);
      toast.success(`Heard: "${transcript}"`);
      speakResponse(`I heard: ${transcript}. Let me search for those prospects.`);
      
      // Auto-search if triggered by wake word
      if (autoSearch) {
        setTimeout(() => handleSearch(), 1000);
      }
    };
    
    recognition.onerror = (event) => {
      setIsListening(false);
      if (event.error !== 'aborted') {
        toast.error(`Voice recognition error: ${event.error}`);
      }
    };
    
    recognition.onend = () => {
      setIsListening(false);
    };
    
    try {
      recognition.start();
    } catch (error) {
      toast.error('Failed to start voice recognition');
      setIsListening(false);
    }
  };

  const speakResponse = (text) => {
    if (!voiceEnabled || !('speechSynthesis' in window) || !isAwake) return;
    
    setIsSpeaking(true);
    
    // Clean up text for better speech
    const cleanText = text.substring(0, 200); // Limit length for speech
    
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

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    resetActivity();
    setLoading(true);
    setStep('searching');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-prospecting/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          query: query,
          target_list: targetList || null,
          max_results: 25
        })
      });

      const result = await response.json();

      if (result.success) {
        if (result.needs_clarification) {
          setClarificationQuestions(result.questions || []);
          setExtractedParameters(result.extracted_parameters);
          setStep('clarification');
          
          // Voice feedback for clarification
          if (voiceEnabled && isAwake) {
            const clarificationText = `I need more information. ${result.questions?.[0] || 'Please provide additional details.'}`;
            setTimeout(() => speakResponse(clarificationText), 500);
          }
        } else {
          setSearchResults(result);
          setStep('results');
          if (result.prospects_count > 0) {
            const successMessage = `Found ${result.prospects_count} prospects!`;
            toast.success(successMessage);
            if (voiceEnabled && isAwake) {
              setTimeout(() => speakResponse(successMessage), 500);
            }
            if (onProspectsAdded) {
              onProspectsAdded(result.prospects_count);
            }
          } else {
            const noResultsMessage = 'No prospects found matching your criteria';
            toast.info(noResultsMessage);
            if (voiceEnabled && isAwake) {
              setTimeout(() => speakResponse(noResultsMessage), 500);
            }
          }
        }
      } else {
        const errorMessage = result.error || 'Search failed';
        toast.error(errorMessage);
        if (voiceEnabled && isAwake) {
          setTimeout(() => speakResponse(`Search failed: ${errorMessage}`), 500);
        }
        setStep('query');
      }
    } catch (error) {
      const errorMessage = 'Search failed. Please try again.';
      toast.error(errorMessage);
      if (voiceEnabled && isAwake) {
        setTimeout(() => speakResponse(errorMessage), 500);
      }
      setStep('query');
    } finally {
      setLoading(false);
    }
  };

  const handleClarificationSubmit = async () => {
    if (clarificationQuestions.some(q => !clarifications[q])) {
      toast.error('Please answer all questions');
      return;
    }

    setLoading(true);
    setStep('searching');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-prospecting/clarify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          query: query,
          target_list: targetList || null,
          clarifications: clarifications
        })
      });

      const result = await response.json();

      if (result.success) {
        setSearchResults(result);
        setStep('results');
        if (result.prospects_count > 0) {
          toast.success(`Found ${result.prospects_count} prospects!`);
          if (onProspectsAdded) {
            onProspectsAdded(result.prospects_count);
          }
        } else {
          toast.info('No prospects found matching your criteria');
        }
      } else {
        toast.error(result.error || 'Search failed');
        setStep('query');
      }
    } catch (error) {
      toast.error('Search failed. Please try again.');
      setStep('query');
    } finally {
      setLoading(false);
    }
  };

  const renderQueryStep = () => (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
          <Brain className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Joy - AI Prospector</h3>
          <p className="text-gray-600">
            {isAwake 
              ? "🎙️ I'm listening! Describe the prospects you're looking for"
              : "Say 'Hello Joy' for voice mode, or describe prospects you're looking for"
            }
          </p>
        </div>
      </div>

      {/* Voice Indicator for Prospector */}
      <div className="flex items-center justify-center mb-4">
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
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Search Query *
            </label>
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
              disabled={isListening || loading}
              className={`flex items-center space-x-1 px-2 py-1 rounded text-xs transition-colors ${
                isListening 
                  ? 'bg-red-100 text-red-600' 
                  : permissionGranted && isAwake
                  ? 'bg-blue-100 text-blue-600 hover:bg-blue-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title={
                !permissionGranted 
                  ? "Click to enable microphone and voice search" 
                  : !isAwake 
                  ? "Click to activate voice mode for search" 
                  : "Voice input for search query"
              }
            >
              {isListening ? <MicOff className="h-3 w-3" /> : <Mic className="h-3 w-3" />}
              <span>{isListening ? 'Stop' : 'Voice'}</span>
            </button>
          </div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Find me CEOs and founders at technology companies in California with 10-500 employees"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={4}
          />
          <div className="mt-2 text-xs text-gray-500">
            <p className="font-medium mb-1">Example queries:</p>
            <ul className="space-y-1 pl-4">
              <li>• "CTOs and VP Engineering at software companies in San Francisco"</li>
              <li>• "Marketing directors at healthcare startups with 50-200 employees"</li>
              <li>• "Founders of fintech companies in New York, not including managers"</li>
            </ul>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target List (Optional)
          </label>
          <select
            value={targetList}
            onChange={(e) => setTargetList(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Create new list or add to existing prospects</option>
            {lists.map(list => (
              <option key={list.id} value={list.name}>{list.name}</option>
            ))}
          </select>
          <p className="mt-1 text-xs text-gray-500">
            If no list is selected, prospects will be added to your main prospects database
          </p>
        </div>
      </div>

      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Sparkles className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-blue-900">How it works</h4>
            <p className="text-sm text-blue-800 mt-1">
              Joy will analyze your query and search Apollo.io's database for matching prospects. 
              You can specify job titles, industries, company sizes, and locations in natural language.
              {voiceEnabled && " Use voice commands by saying 'Hello Joy' to activate voice mode."}
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-3">
        <button
          onClick={onClose}
          className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleSearch}
          disabled={!query.trim() || loading}
          className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
        >
          <Search className="h-4 w-4" />
          <span>Find Prospects</span>
        </button>
      </div>
    </div>
  );

  const renderClarificationStep = () => (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-full flex items-center justify-center">
          <AlertCircle className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Need More Details</h3>
          <p className="text-gray-600">Please provide additional information to improve your search</p>
        </div>
      </div>

      <div className="bg-yellow-50 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-yellow-900 mb-2">Your Query:</h4>
        <p className="text-sm text-yellow-800">{query}</p>
      </div>

      <div className="space-y-4">
        {clarificationQuestions.map((question, index) => (
          <div key={index}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {question}
            </label>
            <input
              type="text"
              value={clarifications[question] || ''}
              onChange={(e) => setClarifications(prev => ({
                ...prev,
                [question]: e.target.value
              }))}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Please provide details..."
            />
          </div>
        ))}
      </div>

      <div className="flex justify-end space-x-3">
        <button
          onClick={() => setStep('query')}
          className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={handleClarificationSubmit}
          disabled={loading}
          className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
        >
          <Search className="h-4 w-4" />
          <span>Search with Details</span>
        </button>
      </div>
    </div>
  );

  const renderSearchingStep = () => (
    <div className="text-center py-12">
      <div className="flex items-center justify-center mb-6">
        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center animate-pulse">
          <Brain className="h-8 w-8 text-white" />
        </div>
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">AI is searching for prospects...</h3>
      <p className="text-gray-600 mb-6">This may take a few moments while we analyze your query and search our database</p>
      <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
        <Clock className="h-4 w-4 animate-spin" />
        <span>Processing your request</span>
      </div>
    </div>
  );

  const renderResultsStep = () => (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
          <CheckCircle className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Search Results</h3>
          <p className="text-gray-600">Your AI prospecting search is complete</p>
        </div>
      </div>

      {searchResults && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-900">Prospects Found</span>
              </div>
              <p className="text-2xl font-bold text-green-900 mt-1">
                {searchResults.prospects_count || 0}
              </p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Building className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Target List</span>
              </div>
              <p className="text-sm font-bold text-blue-900 mt-1">
                {searchResults.target_list || 'General Prospects'}
              </p>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Search Summary</h4>
            <p className="text-sm text-gray-700">{searchResults.message}</p>
            {searchResults.failed_count > 0 && (
              <p className="text-sm text-yellow-700 mt-1">
                Note: {searchResults.failed_count} prospects could not be saved due to validation errors.
              </p>
            )}
          </div>

          {searchResults.prospects && searchResults.prospects.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg">
              <div className="px-4 py-3 border-b border-gray-200">
                <h4 className="text-sm font-medium text-gray-900">Sample Prospects</h4>
                <p className="text-xs text-gray-500">Showing first {Math.min(5, searchResults.prospects.length)} prospects</p>
              </div>
              <div className="divide-y divide-gray-200">
                {searchResults.prospects.slice(0, 5).map((prospect, index) => (
                  <div key={index} className="px-4 py-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {prospect.first_name} {prospect.last_name}
                        </p>
                        <p className="text-xs text-gray-500">{prospect.title}</p>
                        <p className="text-xs text-gray-500">{prospect.company}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">{prospect.city}, {prospect.country}</p>
                        <p className="text-xs text-green-600">{prospect.email_status}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex justify-end space-x-3">
        <button
          onClick={() => {
            resetModal();
            setStep('query');
          }}
          className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          New Search
        </button>
        <button
          onClick={onClose}
          className="px-6 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-colors flex items-center space-x-2"
        >
          <CheckCircle className="h-4 w-4" />
          <span>Done</span>
        </button>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <h2 className="text-2xl font-bold gradient-text">AI Prospector</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {step === 'query' && renderQueryStep()}
          {step === 'clarification' && renderClarificationStep()}
          {step === 'searching' && renderSearchingStep()}
          {step === 'results' && renderResultsStep()}
        </div>
      </div>
    </div>
  );
};

export default AIProspectorModal;