'use client';

import { useState, useEffect, useRef } from 'react';
import { getMessages, queryAI } from '@/lib/aiApi';
import MessageBubble from '@/components/MessageBubble';
import TypingIndicator from '@/components/TypingIndicator';

interface ChatWindowProps {
  sessionId: string | null;
}

const ChatWindow = ({ sessionId }: ChatWindowProps) => {
  const [messages, setMessages] = useState<{ id: string; role: string; content: string; sources?: string[] }[]>([]);
  const [query, setQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchMessages = async () => {
      if (!sessionId) {
        setMessages([]);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const fetchedMessages = await getMessages(sessionId);
        setMessages(fetchedMessages);
      } catch (err) {
        setError('Failed to load messages. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
  }, [sessionId]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !sessionId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await queryAI(query, sessionId);
      setMessages((prevMessages) => [...prevMessages, response]);
      setQuery('');
    } catch (err) {
      setError('Failed to send query. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 bg-gray-100">
        {sessionId ? (
          messages.length > 0 ? (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                role={message.role}
                content={message.content}
                sources={message.sources}
              />
            ))
          ) : (
            <div className="text-center text-gray-500">No messages yet. Start the conversation!</div>
          )
        ) : (
          <div className="text-center text-gray-500">Select a session to view messages.</div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex items-center p-4 bg-white border-t border-gray-300">
        <textarea
          className="flex-1 p-2 border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your message..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          onKeyDown={(e) => {
            if (e.ctrlKey && e.key === 'Enter') {
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          className="ml-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
          disabled={loading}
        >
          Send
        </button>
      </form>
      {loading && <TypingIndicator />}
      {error && <div className="text-red-500 text-center mt-2">{error}</div>}
    </div>
  );
};

export default ChatWindow;