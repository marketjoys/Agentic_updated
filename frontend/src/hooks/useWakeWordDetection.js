// Wake Word Detection Hook for "Hello Joy" - Enhanced Windows Fix
import { useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'react-hot-toast';

const useWakeWordDetection = (onWakeWordDetected, enabled = true) => {
  const [isListeningForWakeWord, setIsListeningForWakeWord] = useState(false);
  const [isAwake, setIsAwake] = useState(false);
  const [error, setError] = useState(null);
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [permissionChecked, setPermissionChecked] = useState(false);
  const [permissionDeniedPermanently, setPermissionDeniedPermanently] = useState(false);
  
  const recognitionRef = useRef(null);
  const timeoutRef = useRef(null);
  const retryCountRef = useRef(0);
  const permissionRequestInProgressRef = useRef(false);
  const lastPermissionRequestTime = useRef(0);
  const lastErrorToastTime = useRef(0);
  const consecutiveErrorsRef = useRef(0);
  const isStabilizingRef = useRef(false); // New flag to prevent rapid restarts

  const MAX_RETRIES = 2; // Allow 2 retries for better reliability
  const WAKE_WORDS = ['hello joy', 'hello, joy', 'helo joy', 'helo, joy', 'hey joy', 'hey, joy'];
  const SLEEP_TIMEOUT = 30000; // 30 seconds of inactivity before going back to wake word listening
  const PERMISSION_REQUEST_COOLDOWN = 10000; // 10 seconds cooldown between permission requests
  const ERROR_DISPLAY_COOLDOWN = 30000; // 30 seconds cooldown between error toasts to prevent spam

  const checkWakeWordSupport = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Voice recognition not supported in this browser');
      return false;
    }
    return true; // Remove Windows-specific restrictions - let users try
  }, []);

  // Enhanced error display with cooldown to prevent spam
  const displayError = useCallback((message, duration = 4000, force = false) => {
    const now = Date.now();
    
    // Only show error if cooldown has passed or it's a forced display
    if (force || now - lastErrorToastTime.current > ERROR_DISPLAY_COOLDOWN) {
      toast.error(message, { duration });
      lastErrorToastTime.current = now;
    } else {
      console.log('Error suppressed (cooldown active):', message);
    }
  }, []);
  // Enhanced microphone permission check with better Windows support
  const checkMicrophonePermission = useCallback(async () => {
    // If permission was permanently denied, don't retry
    if (permissionDeniedPermanently) {
      return false;
    }

    // If we already have permission, return true
    if (permissionChecked && permissionGranted) {
      return true;
    }

    // Prevent multiple simultaneous permission requests
    if (permissionRequestInProgressRef.current) {
      return false;
    }

    // Respect cooldown period
    const now = Date.now();
    if (now - lastPermissionRequestTime.current < PERMISSION_REQUEST_COOLDOWN) {
      return permissionGranted;
    }

    permissionRequestInProgressRef.current = true;
    lastPermissionRequestTime.current = now;
    
    try {
      // First check if permissions API is available and permission is already granted
      if ('permissions' in navigator) {
        try {
          const permission = await navigator.permissions.query({ name: 'microphone' });
          if (permission.state === 'granted') {
            setPermissionGranted(true);
            setPermissionChecked(true);
            permissionRequestInProgressRef.current = false;
            return true;
          } else if (permission.state === 'denied') {
            setError('Microphone access was denied by the user');
            setPermissionGranted(false);
            setPermissionChecked(true);
            setPermissionDeniedPermanently(true);
            permissionRequestInProgressRef.current = false;
            displayError('Voice commands disabled. Please enable microphone access in browser settings.', 5000, true);
            return false;
          }
        } catch (permError) {
          console.log('Permission query not supported, trying direct access');
        }
      }
      
      // Request permission through getUserMedia
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          } 
        });
        
        // Immediately stop all tracks to free up microphone
        stream.getTracks().forEach(track => track.stop());
        
        setPermissionGranted(true);
        setPermissionChecked(true);
        setError(null);
        permissionRequestInProgressRef.current = false;
        
        console.log('Microphone permission granted successfully');
        toast.success('🎤 Voice commands enabled!', { duration: 2000 });
        consecutiveErrorsRef.current = 0; // Reset error count on success
        return true;
        
      } catch (mediaError) {
        console.error('getUserMedia failed:', mediaError);
        
        let errorMessage = 'Microphone access failed';
        let isPermanent = false;
        
        switch (mediaError.name) {
          case 'NotAllowedError':
            errorMessage = 'Microphone access was denied';
            isPermanent = true;
            break;
          case 'NotFoundError':
            errorMessage = 'No microphone device found. Please check your microphone connection.';
            isPermanent = false; // Don't make this permanent - user might connect microphone later
            break;
          case 'NotReadableError':
            errorMessage = 'Microphone is being used by another application';
            isPermanent = false; // This is temporary - other app might release microphone
            break;
          case 'OverconstrainedError':
            errorMessage = 'Microphone doesn\'t support required features';
            isPermanent = false; // Try with different constraints
            break;
          default:
            errorMessage = `Microphone error: ${mediaError.message}`;
            isPermanent = false; // Don't assume it's permanent
        }
        
        setError(errorMessage);
        setPermissionGranted(false);
        setPermissionChecked(true);
        
        if (isPermanent) {
          setPermissionDeniedPermanently(true);
          displayError(`${errorMessage}. Voice commands are disabled.`, 5000, true);
        } else {
          // For temporary issues, don't set permanently denied and reduce error frequency
          setPermissionDeniedPermanently(false);
          consecutiveErrorsRef.current++;
          
          // Only show error message if we haven't had too many consecutive errors
          if (consecutiveErrorsRef.current <= 2) {
            displayError(`${errorMessage}. Will retry automatically.`, 3000);
          }
        }
        
        permissionRequestInProgressRef.current = false;
        return false;
      }
      
    } catch (error) {
      console.error('Unexpected error during permission check:', error);
      setError('Unexpected error accessing microphone');
      setPermissionGranted(false);
      setPermissionChecked(true);
      permissionRequestInProgressRef.current = false;
      return false;
    }
  }, [permissionGranted, permissionChecked, permissionDeniedPermanently]);

  const resetPermissionState = useCallback(() => {
    setPermissionDeniedPermanently(false);
    setPermissionChecked(false);
    setPermissionGranted(false);
    setError(null);
    retryCountRef.current = 0;
    consecutiveErrorsRef.current = 0;
    lastErrorToastTime.current = 0;
  }, []);

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
        toast('Joy is now sleeping. Say "Hello Joy" to wake up.', { 
          icon: '😴',
          duration: 2000
        });
        // Note: We'll restart wake word listening in the useEffect that handles isAwake changes
      }
    }, SLEEP_TIMEOUT);
  }, [isAwake]);

  // New function to manually activate wake mode after permission is granted
  const activateVoiceMode = useCallback(async () => {
    if (!checkWakeWordSupport() || !enabled) {
      console.log('Voice mode activation failed: not supported or disabled');
      return false;
    }

    // Check/request permission
    const hasPermission = await checkMicrophonePermission();
    if (!hasPermission) {
      console.log('Voice mode activation failed: no permission');
      return false;
    }

    // If permission is granted, set awake state and start wake word detection
    setIsAwake(true);
    setError(null);
    toast.success('🎙️ Voice mode activated! You can now use voice commands.', { duration: 3000 });
    
    // Start sleep timer
    resetSleepTimer();
    
    return true;
  }, [enabled, checkWakeWordSupport, checkMicrophonePermission, resetSleepTimer]);

  const startWakeWordListening = useCallback(async () => {
    if (!checkWakeWordSupport() || !enabled) return;

    // If permission was denied permanently, don't attempt to start
    if (permissionDeniedPermanently) {
      console.log('Cannot start wake word listening: microphone permission denied permanently');
      return;
    }

    // Check permission first with enhanced handling
    const hasPermission = await checkMicrophonePermission();
    if (!hasPermission) {
      console.log('Cannot start wake word listening: no microphone permission');
      return;
    }

    // Stop existing recognition gracefully
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort(); // Use abort instead of stop for immediate termination
        recognitionRef.current = null;
      } catch (error) {
        console.log('Error stopping existing recognition:', error);
      }
    }

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();

      // Enhanced Windows-compatible settings
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.maxAlternatives = 1;
      
      // Improved settings for better reliability
      if ('webkitSpeechRecognition' in window) {
        recognitionRef.current.serviceURI = 'wss://www.google.com/speech-api/full-duplex/v1/up';
        recognitionRef.current.grammars = null; // Clear any grammar constraints
      }

      recognitionRef.current.onstart = () => {
        setIsListeningForWakeWord(true);
        setError(null);
        retryCountRef.current = 0;
        console.log('Wake word detection started successfully');
      };

      recognitionRef.current.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal || result[0].confidence > 0.7) {
            const transcript = result[0].transcript.toLowerCase().trim();
            
            if (containsWakeWord(transcript)) {
              console.log('Wake word detected:', transcript);
              handleWakeWordDetected();
              break;
            }
          }
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.log('Wake word recognition error:', event.error);
        setError(event.error);
        
        // Increment consecutive errors
        consecutiveErrorsRef.current++;
        
        // Handle different error types with improved logic and reduced noise
        switch (event.error) {
          case 'not-allowed':
            setError('Microphone permission denied');
            setPermissionGranted(false);
            setPermissionDeniedPermanently(true);
            displayError('Microphone permission required for wake word detection', 5000, true);
            return;
            
          case 'no-speech':
            // Don't treat no-speech as a critical error - this is normal
            console.log('No speech detected, will retry automatically');
            if (retryCountRef.current < MAX_RETRIES) {
              retryCountRef.current++;
              setTimeout(() => {
                if (!isAwake && enabled && permissionGranted && !permissionDeniedPermanently && !isStabilizingRef.current) {
                  startWakeWordListening();
                }
              }, 5000); // Longer delay to stabilize
            }
            break;
            
          case 'network':
            console.log('Network error in speech recognition, will retry');
            if (consecutiveErrorsRef.current <= 3) { // Only show error for first few attempts
              displayError('Voice recognition network error, retrying...', 2000);
            }
            setTimeout(() => {
              if (!isAwake && enabled && permissionGranted && !permissionDeniedPermanently && !isStabilizingRef.current) {
                startWakeWordListening();
              }
            }, 8000);
            break;
            
          case 'audio-capture':
            setError('Audio capture failed - microphone may be in use');
            if (consecutiveErrorsRef.current <= 2) {
              displayError('Microphone is being used by another application', 4000);
            }
            break;
            
          case 'service-not-allowed':
            setError('Speech recognition service not allowed');
            if (consecutiveErrorsRef.current === 1) { // Only show once
              displayError('Speech recognition service is not available', 4000);
            }
            break;
            
          case 'bad-grammar':
            // Don't show error for grammar issues - just retry silently
            console.log('Grammar error - will retry with basic settings');
            setTimeout(() => {
              if (!isAwake && enabled && permissionGranted && !permissionDeniedPermanently && !isStabilizingRef.current) {
                startWakeWordListening();
              }
            }, 3000);
            break;
            
          default:
            console.log(`Speech recognition error: ${event.error}`);
            setError(`Voice recognition error: ${event.error}`);
            
            // Only show Windows-specific troubleshooting after multiple consecutive errors
            if (consecutiveErrorsRef.current >= 3) {
              const isWindows = navigator.platform.toLowerCase().includes('win');
              const isChrome = navigator.userAgent.toLowerCase().includes('chrome');
              
              if (isWindows && !isChrome) {
                displayError('Voice recognition works best on Chrome browser on Windows.', 6000, true);
              } else if (isWindows && consecutiveErrorsRef.current >= 5) {
                // Only show the full troubleshooting message after 5+ consecutive errors
                displayError('Multiple voice recognition failures. Try: 1) Restart browser, 2) Check microphone privacy settings, 3) Test microphone in other apps.', 8000, true);
                
                // Reset counter after showing troubleshooting message
                consecutiveErrorsRef.current = 0;
              } else {
                displayError('Voice recognition failed. Please check your microphone.', 3000);
              }
            }
            break;
        }
      };

      recognitionRef.current.onend = () => {
        setIsListeningForWakeWord(false);
        
        // Add stabilization period to prevent rapid restarts
        if (!isStabilizingRef.current) {
          isStabilizingRef.current = true;
          setTimeout(() => {
            isStabilizingRef.current = false;
          }, 3000); // 3 second stabilization period
        }
        
        // Only restart if conditions are met and we haven't exceeded retries
        if (!isAwake && enabled && permissionGranted && !permissionDeniedPermanently && 
            retryCountRef.current < MAX_RETRIES && !isStabilizingRef.current) {
          setTimeout(() => {
            if (!isAwake && enabled && permissionGranted && !isStabilizingRef.current) {
              startWakeWordListening();
            }
          }, 5000); // Longer delay to prevent rapid restarts
        } else if (retryCountRef.current >= MAX_RETRIES) {
          console.log('Maximum retries reached for wake word detection');
          setError('Wake word detection paused after multiple failures');
          
          // Reset after a longer period
          setTimeout(() => {
            if (!isAwake && enabled && permissionGranted) {
              retryCountRef.current = 0;
              consecutiveErrorsRef.current = 0;
              setError(null);
              startWakeWordListening();
            }
          }, 30000); // Wait 30 seconds before trying again
        }
      };

      recognitionRef.current.start();
      
    } catch (error) {
      console.error('Failed to start wake word recognition:', error);
      setError('Failed to start voice recognition');
      setIsListeningForWakeWord(false);
      
      // Only show user-friendly error message for first few attempts
      if (consecutiveErrorsRef.current <= 2) {
        const isWindows = navigator.platform.toLowerCase().includes('win');
        const isChrome = navigator.userAgent.toLowerCase().includes('chrome');
        
        let errorMessage = 'Voice recognition failed to start. Please check your microphone.';
        let duration = 4000;
        
        if (isWindows && !isChrome) {
          errorMessage = 'For better voice recognition on Windows, consider using Chrome browser.';
          duration = 6000;
        }
        
        displayError(errorMessage, duration);
      }
      
      consecutiveErrorsRef.current++;
    }
  }, [enabled, isAwake, containsWakeWord, checkWakeWordSupport, checkMicrophonePermission, permissionGranted, permissionDeniedPermanently]);

  const handleWakeWordDetected = useCallback(() => {
    setIsAwake(true);
    setIsListeningForWakeWord(false);
    setError(null); // Clear any previous errors
    
    // Stop wake word recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      } catch (error) {
        console.log('Error stopping wake word recognition:', error);
      }
    }
    
    // Provide enhanced feedback
    toast('Hello! How can I help you?', { 
      icon: '🎙️',
      duration: 3000
    });
    
    // Enhanced speech feedback with error handling
    if ('speechSynthesis' in window) {
      try {
        // Wait for voices to load
        const speak = () => {
          const utterance = new SpeechSynthesisUtterance('Hello! I\'m listening.');
          utterance.rate = 1.0;
          utterance.pitch = 1.1;
          utterance.volume = 0.7;
          
          // Use a more reliable voice if available
          const voices = speechSynthesis.getVoices();
          const englishVoice = voices.find(voice => voice.lang.startsWith('en'));
          if (englishVoice) {
            utterance.voice = englishVoice;
          }
          
          speechSynthesis.speak(utterance);
        };
        
        if (speechSynthesis.getVoices().length > 0) {
          speak();
        } else {
          speechSynthesis.addEventListener('voiceschanged', speak, { once: true });
        }
      } catch (speechError) {
        console.log('Speech synthesis error:', speechError);
      }
    }
    
    // Start sleep timer
    resetSleepTimer();
    
    // Trigger callback
    if (onWakeWordDetected) {
      setTimeout(() => onWakeWordDetected(), 1000);
    }
  }, [resetSleepTimer, onWakeWordDetected]);

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

  // Initialize microphone permission check on mount with improved logic
  useEffect(() => {
    if (enabled && checkWakeWordSupport()) {
      // Initial permission check without starting listening immediately
      checkMicrophonePermission().then((hasPermission) => {
        if (hasPermission && !permissionDeniedPermanently) {
          console.log('Microphone permission available, starting wake word detection after delay...');
          // Longer delay to ensure state is properly set and reduce startup errors
          setTimeout(() => {
            if (enabled && !isAwake) { // Only start if still enabled and not awake
              startWakeWordListening();
            }
          }, 2000); // Increased delay
        } else {
          console.log('Microphone permission not available or denied permanently');
        }
      }).catch((error) => {
        console.error('Failed to check microphone permission on mount:', error);
      });
    }

    return () => {
      stopWakeWordListening();
    };
  }, [enabled, checkWakeWordSupport]); // Removed function dependencies to prevent loops

  // Clean up on unmount with enhanced cleanup
  useEffect(() => {
    return () => {
      // Cleanup recognition
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
          recognitionRef.current = null;
        } catch (error) {
          console.log('Cleanup recognition error:', error);
        }
      }
      
      // Cleanup timer
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      // Reset permission request flag and stabilization flag
      permissionRequestInProgressRef.current = false;
      isStabilizingRef.current = false;
    };
  }, []);

  // Handle wake word listening restart when isAwake changes
  useEffect(() => {
    if (!isAwake && enabled && permissionGranted && !permissionDeniedPermanently && !isStabilizingRef.current) {
      // Reset retry count when manually restarting
      retryCountRef.current = 0;
      
      // Longer delay before restarting wake word listening to prevent rapid cycling
      const restartTimeout = setTimeout(() => {
        if (!isAwake && enabled && permissionGranted && !permissionDeniedPermanently && !isStabilizingRef.current) {
          startWakeWordListening();
        }
      }, 3000); // Increased delay
      
      return () => clearTimeout(restartTimeout);
    }
  }, [isAwake, enabled, permissionGranted, permissionDeniedPermanently, startWakeWordListening]);

  return {
    isListeningForWakeWord,
    isAwake,
    error,
    permissionGranted,
    permissionDeniedPermanently,
    goToSleep,
    resetActivity,
    startWakeWordListening,
    stopWakeWordListening,
    resetPermissionState,
    activateVoiceMode,
    // Additional utility methods for better integration
    requestPermission: checkMicrophonePermission,
    hasSupport: checkWakeWordSupport(),
    // New methods for better user control
    forceRestartListening: () => {
      retryCountRef.current = 0;
      consecutiveErrorsRef.current = 0;
      isStabilizingRef.current = false;
      setError(null);
      if (!isAwake && enabled && permissionGranted) {
        startWakeWordListening();
      }
    },
    getErrorCount: () => consecutiveErrorsRef.current
  };
};

export default useWakeWordDetection;