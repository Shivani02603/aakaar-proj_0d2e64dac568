import { env } from '@/env';

const API_BASE_URL = env.NEXT_PUBLIC_API_BASE_URL;

export interface Session {
  id: string;
  name: string;
  created_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface AIQueryResponse {
  answer: string;
  sources: string[];
}

export async function ingestFile(file: File, sessionId: string): Promise<{ chunks_indexed: number }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);

  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/ingest`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to ingest file: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error ingesting file: ${error.message}`);
  }
}

export async function queryAI(query: string, sessionId: string): Promise<AIQueryResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, session_id: sessionId }),
    });

    if (!response.ok) {
      throw new Error(`Failed to query AI: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error querying AI: ${error.message}`);
  }
}

export function streamAnswer(query: string, sessionId: string): EventSource {
  const url = `${API_BASE_URL}/api/ai/stream?query=${encodeURIComponent(query)}&session_id=${encodeURIComponent(sessionId)}`;
  return new EventSource(url);
}

export async function getSessions(): Promise<Session[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch sessions: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error fetching sessions: ${error.message}`);
  }
}

export async function createSession(name?: string): Promise<Session> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error creating session: ${error.message}`);
  }
}

export async function getMessages(sessionId: string): Promise<Message[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/messages`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch messages: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Error fetching messages: ${error.message}`);
  }
}