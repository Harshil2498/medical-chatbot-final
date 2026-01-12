import React from 'react';

const LoadingSpinner = ({ message = 'Loading...' }) => {
  const displayMessage =
    typeof message === 'string'
      ? message
      : message?.message || 'Loading...';

  return (
    <div className="loading-spinner">
      <span>{displayMessage}</span>
    </div>
  );
};

export default LoadingSpinner;
