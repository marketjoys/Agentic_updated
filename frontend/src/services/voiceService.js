// Voice Service for handling microphone permissions and audio processing
import { toast } from 'react-hot-toast';

class VoiceService {
  constructor() {
    this.mediaStream = null;
    this.audioContext = null;
    this.recognition = null;
    this.isSupported = this.checkSupport();
  }

  checkSupport() {
    const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    const hasSpeechRecognition = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
    const hasSpeechSynthesis = !!window.speechSynthesis;
    
    return {
      microphone: hasGetUserMedia,
      speechRecognition: hasSpeechRecognition,
      speechSynthesis: hasSpeechSynthesis,
      all: hasGetUserMedia && hasSpeechRecognition && hasSpeechSynthesis
    };
  }

  async requestMicrophonePermission() {
    try {
      if (!this.isSupported.microphone) {
        throw new Error('Microphone access not supported in this browser');
      }

      // Check if we already have an active permission
      if (this.mediaStream && this.mediaStream.active) {
        return { success: true, stream: this.mediaStream };
      }

      // Clean up any existing inactive streams
      if (this.mediaStream && !this.mediaStream.active) {
        this.mediaStream = null;
      }

      // Check permission status first
      const permissionStatus = await this.checkPermissionStatus();
      if (permissionStatus === 'denied') {
        throw new Error('Microphone permission was previously denied. Please enable it in browser settings.');
      }

      // Request permission with enhanced constraints for better compatibility
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: { ideal: 44100, min: 16000 },
          channelCount: { ideal: 1 }
        } 
      });

      // Verify the stream is active
      if (!this.mediaStream || !this.mediaStream.active) {
        throw new Error('Failed to activate microphone stream');
      }

      toast.success('🎤 Microphone access granted!', { duration: 2000 });

      return { success: true, stream: this.mediaStream };

    } catch (error) {
      console.error('Microphone permission error:', error);
      
      let errorMessage = 'Microphone access failed';
      let helpText = '';
      let isRetryable = true;

      switch (error.name) {
        case 'NotAllowedError':
          errorMessage = 'Microphone permission denied';
          helpText = 'Please allow microphone access in your browser settings and refresh the page';
          isRetryable = false;
          break;
        case 'NotFoundError':
          errorMessage = 'No microphone found';
          helpText = 'Please connect a microphone to your device';
          isRetryable = false;
          break;
        case 'NotReadableError':
          errorMessage = 'Microphone is being used by another application';
          helpText = 'Please close other applications using the microphone and try again';
          isRetryable = true;
          break;
        case 'OverconstrainedError':
          errorMessage = 'Microphone constraints not supported';
          helpText = 'Your microphone may not support the required features';
          isRetryable = false;
          break;
        case 'AbortError':
          errorMessage = 'Microphone request was cancelled';
          helpText = 'Please try again';
          isRetryable = true;
          break;
        default:
          errorMessage = error.message || 'Unknown microphone error';
          helpText = 'Please check your microphone settings and try again';
      }

      const fullMessage = helpText ? `${errorMessage}\n${helpText}` : errorMessage;
      
      toast.error(fullMessage, { 
        duration: isRetryable ? 4000 : 6000,
        style: { maxWidth: '400px' }
      });

      return { success: false, error: errorMessage, helpText, isRetryable };
    }
  }

  async checkPermissionStatus() {
    try {
      if (!navigator.permissions) {
        return 'unknown';
      }

      const permission = await navigator.permissions.query({ name: 'microphone' });
      return permission.state; // 'granted', 'denied', or 'prompt'
    } catch (error) {
      console.warn('Could not check microphone permission:', error);
      return 'unknown';
    }
  }

  createSpeechRecognition(options = {}) {
    if (!this.isSupported.speechRecognition) {
      throw new Error('Speech recognition not supported in this browser');
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    // Default settings
    recognition.lang = options.language || 'en-US';
    recognition.continuous = options.continuous || false;
    recognition.interimResults = options.interimResults || false;
    recognition.maxAlternatives = options.maxAlternatives || 1;

    this.recognition = recognition;
    return recognition;
  }

  speak(text, options = {}) {
    if (!this.isSupported.speechSynthesis) {
      console.warn('Speech synthesis not supported');
      return Promise.reject(new Error('Speech synthesis not supported'));
    }

    return new Promise((resolve, reject) => {
      if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
      }

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Default settings
      utterance.rate = options.rate || 0.95;
      utterance.pitch = options.pitch || 1.1;
      utterance.volume = options.volume || 0.9;
      utterance.voice = options.voice || null;

      utterance.onend = () => resolve();
      utterance.onerror = (event) => reject(new Error(`Speech synthesis error: ${event.error}`));

      speechSynthesis.speak(utterance);
    });
  }

  stopSpeaking() {
    if (this.isSupported.speechSynthesis && speechSynthesis.speaking) {
      speechSynthesis.cancel();
    }
  }

  getAvailableVoices() {
    if (!this.isSupported.speechSynthesis) {
      return [];
    }

    return speechSynthesis.getVoices().filter(voice => 
      voice.lang.startsWith('en') // Filter to English voices
    );
  }

  // Audio visualization helpers
  createAudioContext() {
    if (!this.mediaStream) {
      throw new Error('No media stream available. Request microphone permission first.');
    }

    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      const analyser = this.audioContext.createAnalyser();
      
      analyser.fftSize = 256;
      source.connect(analyser);

      return { audioContext: this.audioContext, analyser };
    } catch (error) {
      console.error('Failed to create audio context:', error);
      throw error;
    }
  }

  // Cleanup resources
  cleanup() {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    if (this.recognition) {
      this.recognition.stop();
      this.recognition = null;
    }

    this.stopSpeaking();
  }

  // Utility methods
  isPermissionGranted() {
    return this.mediaStream && this.mediaStream.active;
  }

  getSupportStatus() {
    return {
      ...this.isSupported,
      permissionGranted: this.isPermissionGranted(),
      mediaStream: !!this.mediaStream
    };
  }
}

// Create singleton instance
const voiceService = new VoiceService();

export default voiceService;