import { useState } from 'react';
import SessionSidebar from '@/components/SessionSidebar';
import DocumentUploader from '@/components/DocumentUploader';
import ChatWindow from '@/components/ChatWindow';

export default function AppLayout() {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="flex items-center justify-between px-4 py-2 bg-gray-800 text-white">
        <h1 className="text-lg font-semibold">Aakaar Project</h1>
        <button
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium"
          onClick={() => setActiveSessionId(null)}
        >
          New Chat
        </button>
      </header>
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-64 bg-gray-100 border-r border-gray-300 flex flex-col">
          <SessionSidebar onSelectSession={handleSelectSession} />
          <div className="mt-auto p-4">
            <DocumentUploader sessionId={activeSessionId} />
          </div>
        </aside>
        <main className="flex-1 flex flex-col">
          <ChatWindow activeSessionId={activeSessionId} />
        </main>
      </div>
    </div>
  );
}