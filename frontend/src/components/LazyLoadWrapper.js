import React, { Suspense } from 'react';
import { Loader2 } from 'lucide-react';

// Loading component for Suspense fallback
const LoadingSpinner = ({ message = 'Loading...' }) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50">
    <div className="text-center">
      <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
      <p className="text-gray-600">{message}</p>
    </div>
  </div>
);

// HOC for lazy loading components
const withLazyLoading = (WrappedComponent, loadingMessage) => {
  return function LazyLoadedComponent(props) {
    return (
      <Suspense fallback={<LoadingSpinner message={loadingMessage} />}>
        <WrappedComponent {...props} />
      </Suspense>
    );
  };
};

export { LoadingSpinner, withLazyLoading };