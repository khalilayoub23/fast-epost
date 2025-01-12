import React, { useState, useEffect } from 'react';
import '../styles/styles.css';

function LoadingScreen({ onLoadingComplete }) {
  const [loadingComplete, setLoadingComplete] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoadingComplete(true);
      onLoadingComplete();
    }, 3000); // 3 seconds loading time

    return () => clearTimeout(timer);
  }, [onLoadingComplete]);

  return (
    <div className="loading-screen">
      <div className={`loading-logo ${loadingComplete ? 'logo-move-up' : ''}`} />
      {!loadingComplete && (
        <div className="loading-bar-container">
          <div className="loading-bar" style={{ width: '100%' }} />
        </div>
      )}
    </div>
  );
}


export default LoadingScreen;
