'use client';

import { useEffect, useState } from 'react';
import { createSession, getSessions, Session } from '@/lib/aiApi';
import { formatRelative } from 'date-fns';

interface SessionSidebarProps {
  onSelectSession: (id: string) => void;
  activeSessionId?: string;
}

export default function SessionSidebar({ onSelectSession, activeSessionId }: SessionSidebarProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const fetchedSessions = await getSessions();
        const sortedSessions = fetchedSessions.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setSessions(sortedSessions);
      } catch (err) {
        setError('Failed to load sessions. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const handleNewChat = async () => {
    try {
      const newSession = await createSession();
      onSelectSession(newSession.id);
    } catch (err) {
      setError('Failed to create a new session. Please try again.');
    }
  };

  return (
    <div className="w-64 bg-gray-100 border-r border-gray-300 h-full flex flex-col">
      <div className="p-4 border-b border-gray-300">
        <button
          onClick={handleNewChat}
          className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition"
        >
          New Chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-4">
            {[...Array(3)].map((_, index) => (
              <div key={index} className="h-10 bg-gray-300 rounded animate-pulse"></div>
            ))}
          </div>
        ) : error ? (
          <div className="p-4 text-red-500">{error}</div>
        ) : (
          <ul className="p-4 space-y-2">
            {sessions.map((session) => (
              <li
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`p-2 rounded cursor-pointer ${
                  session.id === activeSessionId
                    ? 'bg-gray-200 border-l-4 border-blue-500'
                    : 'hover:bg-gray-200'
                }`}
              >
                <div className="text-sm font-medium truncate">{session.name}</div>
                <div className="text-xs text-gray-500">
                  {formatRelative(new Date(session.created_at), new Date())}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}