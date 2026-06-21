const API_BASE = 'http://localhost:8000/api';

export const api = {
  get: async <T>(endpoint: string): Promise<T> => {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },
  post: async <T>(endpoint: string, data: any): Promise<T> => {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  },
  // Add put, delete as needed
};
