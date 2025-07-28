// Voice Troubleshooting Modal for Windows Users
import React from 'react';
import { X, Mic, Chrome, Settings, Headphones } from 'lucide-react';

const VoiceTroubleshootingModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const isWindows = navigator.platform.toLowerCase().includes('win');
  const isChrome = navigator.userAgent.toLowerCase().includes('chrome');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl mx-4 max-h-96 overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold flex items-center">
            <Headphones className="h-5 w-5 mr-2" />
            Voice Recognition Troubleshooting
          </h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4">
          {isWindows && (
            <>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2 flex items-center">
                  <Chrome className="h-4 w-4 mr-2" />
                  Browser Recommendation
                </h4>
                <p className="text-sm text-blue-800">
                  {isChrome 
                    ? "✅ You're using Chrome, which works best for voice recognition on Windows."
                    : "⚠️ For best voice recognition on Windows, we recommend using Google Chrome browser."
                  }
                </p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2 flex items-center">
                  <Settings className="h-4 w-4 mr-2" />
                  Windows Privacy Settings
                </h4>
                <div className="text-sm text-green-800 space-y-1">
                  <p>1. Open Windows Settings → Privacy & Security → Microphone</p>
                  <p>2. Ensure "Microphone access" is turned ON</p>
                  <p>3. Make sure your browser has microphone permission</p>
                  <p>4. Check "Let desktop apps access your microphone" is ON</p>
                </div>
              </div>
            </>
          )}

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-medium text-yellow-900 mb-2 flex items-center">
              <Mic className="h-4 w-4 mr-2" />
              Browser Permissions
            </h4>
            <div className="text-sm text-yellow-800 space-y-1">
              <p>1. Click the 🔒 lock icon in your browser's address bar</p>
              <p>2. Set microphone permission to "Allow"</p>
              <p>3. Refresh the page after changing permissions</p>
              <p>4. Make sure no other applications are using your microphone</p>
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Quick Test</h4>
            <div className="text-sm text-gray-700 space-y-1">
              <p>1. Try saying "Hello Joy" clearly after ensuring permissions</p>
              <p>2. If it doesn't work, try clicking the microphone button manually</p>
              <p>3. Ensure you're in a quiet environment</p>
              <p>4. Speak at a normal volume and pace</p>
            </div>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-900 mb-2">Still Having Issues?</h4>
            <div className="text-sm text-red-800 space-y-1">
              <p>1. Restart your browser completely</p>
              <p>2. Check if other applications can access your microphone</p>
              <p>3. Try using a different microphone or headset</p>
              <p>4. You can always type commands instead of using voice</p>
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
};

export default VoiceTroubleshootingModal;