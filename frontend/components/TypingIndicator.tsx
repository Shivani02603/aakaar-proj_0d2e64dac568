'use client';

import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-center space-x-2">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce1"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce2"></div>
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce3"></div>
      <style jsx>{`
        @keyframes bounce {
          0%, 80%, 100% {
            transform: scale(0);
          }
          40% {
            transform: scale(1);
          }
        }
        .animate-bounce1 {
          animation: bounce 1.4s infinite;
          animation-delay: 0s;
        }
        .animate-bounce2 {
          animation: bounce 1.4s infinite;
          animation-delay: 0.2s;
        }
        .animate-bounce3 {
          animation: bounce 1.4s infinite;
          animation-delay: 0.4s;
        }
      `}</style>
    </div>
  );
};

export default TypingIndicator;