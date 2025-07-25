// Wake Word Detection Hook for "Hello Joy" - Fixed for Windows
import { useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'react-hot-toast';

const useWakeWordDetection = (onWakeWordDetected, enabled = true) => {
  const [isListeningForWakeWord, setIsListeningForWakeWord] = useState(false);
  const [isAwake, setIsAwake] = useState(false);
  const [error, setError] = useState(null);
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [permissionChecked, setPermissionChecked] = useState(false);
  
  const recognitionRef = useRef(null);
  const timeoutRef = useRef(null);
  const retryCountRef = useRef(0);
  const permissionRequestedRef = useRef(false);

  const MAX_RETRIES = 2; // Reduced retries to prevent loops
  const WAKE_WORDS = ['hello joy', 'hello, joy', 'helo joy', 'helo, joy', 'hey joy', 'hey, joy'];
  const SLEEP_TIMEOUT = 30000; // 30 seconds of inactivity before going back to wake word listening

  const checkWakeWordSupport = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Voice recognition not supported in this browser');
      return false;
    }
    return true;
  }, []);

  // Check microphone permission status
  const checkMicrophonePermission = useCallback(async () => {
    if (permissionChecked) return permissionGranted;
    
    try {
      // Check if permissions API is available
      if ('permissions' in navigator) {
        const permission = await navigator.permissions.query({ name: 'microphone' });
        if (permission.state === 'granted') {
          setPermissionGranted(true);
          setPermissionChecked(true);
          return true;
        } else if (permission.state === 'denied') {
          setError('Microphone permission denied');
          setPermissionGranted(false);
          setPermissionChecked(true);
          return false;
        }
      }
      
      // Fallback: try to get user media without storing stream
      if (!permissionRequestedRef.current) {
        permissionRequestedRef.current = true;
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Immediately stop all tracks to free up microphone
        stream.getTracks().forEach(track => track.stop());
        setPermissionGranted(true);
        setPermissionChecked(true);
        console.log('Microphone permission granted');
        return true;
      }
      
      return permissionGranted;
    } catch (error) {
      console.error('Microphone permission check failed:', error);
      setError('Microphone permission required for voice commands');
      setPermissionGranted(false);
      setPermissionChecked(true);
      
      // Don't show toast if user explicitly denied permission
      if (error.name !== 'NotAllowedError') {
        toast.error('Please allow microphone access for voice commands');
      }
      return false;
    }
  }, [permissionGranted, permissionChecked]);

  const containsWakeWord = useCallback((transcript) => {
    const normalizedTranscript = transcript.toLowerCase().trim();
    return WAKE_WORDS.some(wakeWord => normalizedTranscript.includes(wakeWord));
  }, [WAKE_WORDS]);

  const resetSleepTimer = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      if (isAwake) {
        setIsAwake(false);
        startWakeWordListening();
        toast('Joy is now sleeping. Say "Hello Joy" to wake up.', { 
          icon: '😴',
          duration: 2000
        });
      }
    }, SLEEP_TIMEOUT);
  }, [isAwake]);

  const startWakeWordListening = useCallback(async () => {
    if (!checkWakeWordSupport() || !enabled) return;

    // Check permission first
    const hasPermission = await checkMicrophonePermission();
    if (!hasPermission) {
      console.log('Cannot start wake word listening: no microphone permission');
      return;
    }

    // Stop existing recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.log('Error stopping existing recognition:', error);
      }
    }

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();

      // Windows-optimized settings
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.maxAlternatives = 1;
      
      // Windows compatibility: Add service hints
      if (window.webkitSpeechRecognition) {
        recognitionRef.current.serviceURI = 'wss://www.google.com/speech-api/full-duplex/v1/up';
      }

      recognitionRef.current.onstart = () => {
        setIsListeningForWakeWord(true);
        setError(null);
        retryCountRef.current = 0;
        console.log('Wake word detection started');
      };

      recognitionRef.current.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          
          if (containsWakeWord(transcript)) {
            console.log('Wake word detected:', transcript);
            setIsAwake(true);
            setIsListeningForWakeWord(false);
            
            // Stop wake word recognition
            if (recognitionRef.current) {
              recognitionRef.current.stop();
            }
            
            // Provide audio feedback
            toast('Hello! How can I help you?', { 
              icon: '🎙️',
              duration: 3000
            });
            
            // Play wake sound (Windows compatible)
            if ('speechSynthesis' in window && speechSynthesis.getVoices().length > 0) {
              const utterance = new SpeechSynthesisUtterance('Hello! I\'m listening.');
              utterance.rate = 1.1;
              utterance.pitch = 1.2;
              utterance.volume = 0.8;
              speechSynthesis.speak(utterance);
            }
            
            // Start sleep timer
            resetSleepTimer();
            
            // Trigger callback
            if (onWakeWordDetected) {
              setTimeout(() => onWakeWordDetected(), 1000);
            }
            
            break;
          }
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Wake word recognition error:', event.error);
        setError(event.error);
        
        // Handle different error types
        if (event.error === 'not-allowed') {
          setError('Microphone permission denied. Please allow microphone access.');
          setPermissionGranted(false);
          toast.error('Microphone permission required for wake word detection');
          return;
        }
        
        if (event.error === 'no-speech' && retryCountRef.current < MAX_RETRIES) {
          retryCountRef.current++;
          console.log(`Retrying wake word detection (${retryCountRef.current}/${MAX_RETRIES})`);
          setTimeout(() => {
            if (!isAwake && enabled && permissionGranted) {
              startWakeWordListening();
            }
          }, 2000); // Longer delay for Windows
        } else if (event.error === 'network') {
          console.log('Network error in speech recognition, retrying...');
          setTimeout(() => {
            if (!isAwake && enabled && permissionGranted) {
              startWakeWordListening();
            }
          }, 5000);
        }
      };

      recognitionRef.current.onend = () => {
        setIsListeningForWakeWord(false);
        
        // Only restart if not awake, enabled, and have permission
        if (!isAwake && enabled && permissionGranted && retryCountRef.current < MAX_RETRIES) {
          setTimeout(() => {
            startWakeWordListening();
          }, 1000); // Delay to prevent rapid restarts
        }
      };

      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start wake word recognition:', error);
      setError('Failed to start voice recognition');
      setIsListeningForWakeWord(false);
    }
  }, [enabled, isAwake, containsWakeWord, checkWakeWordSupport, checkMicrophonePermission, onWakeWordDetected, resetSleepTimer, permissionGranted]);

  const stopWakeWordListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.log('Error stopping recognition:', error);
      }
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsListeningForWakeWord(false);
    setIsAwake(false);
  }, []);

  const goToSleep = useCallback(() => {
    setIsAwake(false);
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (permissionGranted) {
      startWakeWordListening();
    }
    toast('Going back to sleep. Say "Hello Joy" to wake up.', { 
      icon: '😴',
      duration: 2000
    });
  }, [startWakeWordListening, permissionGranted]);

  const resetActivity = useCallback(() => {
    if (isAwake) {
      resetSleepTimer();
    }
  }, [isAwake, resetSleepTimer]);

  // Initialize microphone permission check on mount
  useEffect(() => {
    if (enabled && checkWakeWordSupport()) {
      checkMicrophonePermission().then((hasPermission) => {
        if (hasPermission) {
          console.log('Starting wake word detection...');
          startWakeWordListening();
        }
      });
    }

    return () => {
      stopWakeWordListening();
    };
  }, [enabled]); // Only depend on enabled, not the functions

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.log('Cleanup error:', error);
        }
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    isListeningForWakeWord,
    isAwake,
    error,
    permissionGranted,
    goToSleep,
    resetActivity,
    startWakeWordListening,
    stopWakeWordListening
  };
};

export default useWakeWordDetection;