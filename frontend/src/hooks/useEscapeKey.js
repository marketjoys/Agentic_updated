import { useEffect } from 'react';

const useEscapeKey = (callback, isEnabled = true) => {
  useEffect(() => {
    if (!isEnabled) return;

    const handleEscapeKey = (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        callback();
      }
    };

    document.addEventListener('keydown', handleEscapeKey);

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [callback, isEnabled]);
};

export default useEscapeKey;