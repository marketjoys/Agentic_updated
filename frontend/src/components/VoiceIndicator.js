// Voice Activity Indicator Component
import React from 'react';
import { Mic, MicOff, Volume2, VolumeX, Waves, Moon, Sun, Shield, HelpCircle } from 'lucide-react';

const VoiceIndicator = ({ 
  isListeningForWakeWord, 
  isAwake, 
  isListening, 
  isSpeaking, 
  error,
  voiceEnabled,
  permissionGranted,
  onToggleVoice,
  onGoToSleep,
  onRequestPermission,
  onForceRestart, // New prop for manual restart
  onShowHelp // New prop for showing help
}) => {
  const getStatusIcon = () => {
    if (error && error.includes('permission')) return <Shield className="h-5 w-5 text-red-500" />;
    if (error) return <MicOff className="h-5 w-5 text-red-500" />;
    if (isSpeaking) return <Volume2 className="h-5 w-5 text-purple-500" />;
    if (isListening) return <Mic className="h-5 w-5 text-green-500" />;
    if (isAwake) return <Sun className="h-5 w-5 text-yellow-500" />;
    if (isListeningForWakeWord) return <Moon className="h-5 w-5 text-blue-500" />;
    return <MicOff className="h-5 w-5 text-gray-400" />;
  };

  const getStatusText = () => {
    if (error && error.includes('permission')) return 'Permission needed - Click to grant';
    if (error && error.includes('failed')) return 'Voice paused - Click to retry';
    if (error) return 'Voice issue - Click to retry';
    if (isSpeaking) return 'Speaking';
    if (isListening) return 'Listening';
    if (isAwake) return 'Awake - Say something or "sleep"';
    if (isListeningForWakeWord) return 'Listening for "Hello Joy"';
    if (!permissionGranted) return 'Click to enable microphone';
    return 'Voice disabled';
  };

  const getStatusColor = () => {
    if (error && error.includes('permission')) return 'bg-orange-100 text-orange-700 border-orange-200';
    if (error) return 'bg-red-100 text-red-700 border-red-200';
    if (isSpeaking) return 'bg-purple-100 text-purple-700 border-purple-200';
    if (isListening) return 'bg-green-100 text-green-700 border-green-200';
    if (isAwake) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    if (isListeningForWakeWord) return 'bg-blue-100 text-blue-700 border-blue-200';
    return 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const getPulseAnimation = () => {
    if (isListening) return 'animate-pulse';
    if (isListeningForWakeWord) return 'animate-ping';
    return '';
  };

  const handleStatusClick = () => {
    if (error && error.includes('permission') && onRequestPermission) {
      onRequestPermission();
    } else if (error && onForceRestart) {
      onForceRestart();
    }
  };

  return (
    <div className="flex items-center space-x-3">
      {/* Voice Status Indicator */}
      <div 
        className={`flex items-center space-x-2 px-3 py-2 rounded-full border ${getStatusColor()} transition-all duration-300 ${
          ((error && error.includes('permission')) || (error && onForceRestart)) ? 'cursor-pointer hover:opacity-80' : ''
        }`}
        onClick={handleStatusClick}
        title={getStatusText()}
      >
        <div className={`relative ${getPulseAnimation()}`}>
          {getStatusIcon()}
          {/* Audio visualization dots */}
          {(isListening || isSpeaking) && (
            <div className="absolute -right-1 -top-1 flex space-x-0.5">
              <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '100ms' }}></div>
              <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '200ms' }}></div>
            </div>
          )}
        </div>
        <span className="text-sm font-medium">
          {getStatusText()}
        </span>
      </div>

      {/* Voice Controls */}
      <div className="flex items-center space-x-1">
        {/* Voice Toggle */}
        <button
          onClick={onToggleVoice}
          className={`p-2 rounded-lg transition-colors ${
            voiceEnabled 
              ? 'bg-green-100 text-green-600 hover:bg-green-200' 
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
          title={voiceEnabled ? 'Disable voice' : 'Enable voice'}
        >
          {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
        </button>

        {/* Permission Request Button */}
        {!permissionGranted && onRequestPermission && (
          <button
            onClick={onRequestPermission}
            className="p-2 rounded-lg bg-orange-100 text-orange-600 hover:bg-orange-200 transition-colors"
            title="Request microphone permission"
          >
            <Shield className="h-4 w-4" />
          </button>
        )}

        {/* Sleep Control */}
        {isAwake && onGoToSleep && (
          <button
            onClick={onGoToSleep}
            className="p-2 rounded-lg bg-blue-100 text-blue-600 hover:bg-blue-200 transition-colors"
            title="Put Joy to sleep"
          >
            <Moon className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Wake Word Indicator */}
      {isListeningForWakeWord && (
        <div className="flex items-center space-x-1 text-xs text-blue-600">
          <Waves className="h-3 w-3 animate-pulse" />
          <span>Wake: "Hello Joy"</span>
        </div>
      )}
    </div>
  );
};

export default VoiceIndicator;