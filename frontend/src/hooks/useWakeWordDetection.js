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

  const containsWakeWord = useCallback((transcript) => {
    const normalizedTranscript = transcript.toLowerCase().trim();
    return WAKE_WORDS.some(wakeWord => normalizedTranscript.includes(wakeWord));
  }, []);

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

  const startWakeWordListening = useCallback(() => {
    if (!checkWakeWordSupport() || !enabled) return;

    // Stop existing recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();

    recognitionRef.current.lang = 'en-US';
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.maxAlternatives = 1;

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
          recognitionRef.current.stop();
          
          // Provide audio feedback
          toast('Hello! How can I help you?', { 
            icon: '🎙️',
            duration: 3000
          });
          
          // Play wake sound
          if ('speechSynthesis' in window) {
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
      
      // Retry logic for certain errors
      if (event.error === 'no-speech' && retryCountRef.current < MAX_RETRIES) {
        retryCountRef.current++;
        setTimeout(() => {
          if (!isAwake && enabled) {
            startWakeWordListening();
          }
        }, 1000);
      } else if (event.error === 'not-allowed') {
        setError('Microphone permission denied. Please allow microphone access.');
        toast.error('Microphone permission required for wake word detection');
      }
    };

    recognitionRef.current.onend = () => {
      setIsListeningForWakeWord(false);
      
      // Restart if not awake and enabled
      if (!isAwake && enabled) {
        setTimeout(() => {
          startWakeWordListening();
        }, 500);
      }
    };

    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start wake word recognition:', error);
      setError('Failed to start voice recognition');
    }
  }, [enabled, isAwake, containsWakeWord, checkWakeWordSupport, onWakeWordDetected, resetSleepTimer]);

  const stopWakeWordListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
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
    startWakeWordListening();
    toast('Going back to sleep. Say "Hello Joy" to wake up.', { 
      icon: '😴',
      duration: 2000
    });
  }, [startWakeWordListening]);

  const resetActivity = useCallback(() => {
    if (isAwake) {
      resetSleepTimer();
    }
  }, [isAwake, resetSleepTimer]);

  // Request microphone permission on mount
  useEffect(() => {
    if (enabled && checkWakeWordSupport()) {
      navigator.mediaDevices?.getUserMedia({ audio: true })
        .then(() => {
          console.log('Microphone permission granted');
          startWakeWordListening();
        })
        .catch((error) => {
          console.error('Microphone permission denied:', error);
          setError('Microphone permission required');
          toast.error('Please allow microphone access for wake word detection');
        });
    }

    return () => {
      stopWakeWordListening();
    };
  }, [enabled, startWakeWordListening, stopWakeWordListening, checkWakeWordSupport]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
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
    goToSleep,
    resetActivity,
    startWakeWordListening,
    stopWakeWordListening
  };
};

export default useWakeWordDetection;