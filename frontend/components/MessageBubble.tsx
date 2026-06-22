'use client';

import React from 'react';
import { useState } from 'react';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, sources }) => {
  const [copiedSource, setCopiedSource] = useState<string | null>(null);

  const handleCopySource = (source: string) => {
    navigator.clipboard.writeText(source).then(() => {
      setCopiedSource(source);
      setTimeout(() => setCopiedSource(null), 2000);
    });
  };

  const renderContent = (text: string) => {
    const markdownRegex = /(\*\*(.*?)\*\*)|(`(.*?)`)|(```([\s\S]*?)```)/g;
    const parts = text.split(markdownRegex).filter(Boolean);

    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={index} className="font-bold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={index} className="bg-gray-200 text-gray-800 px-1 rounded">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part.startsWith('```') && part.endsWith('```')) {
        return (
          <pre key={index} className="bg-gray-100 text-gray-800 p-2 rounded">
            <code>{part.slice(3, -3)}</code>
          </pre>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div
      className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-lg p-3 rounded-lg ${
          role === 'user'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 text-gray-800'
        }`}
      >
        <div>{renderContent(content)}</div>
        {role === 'assistant' && sources && sources.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {sources.map((source, index) => (
              <button
                key={index}
                onClick={() => handleCopySource(source)}
                className="text-xs bg-gray-300 text-gray-700 px-2 py-1 rounded hover:bg-gray-400"
              >
                {source}
              </button>
            ))}
            {copiedSource && (
              <span className="text-xs text-green-600">
                Copied "{copiedSource}"!
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;