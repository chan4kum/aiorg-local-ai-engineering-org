type Listener = (data: any) => void;

class WebSocketManager {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Listener>> = new Map();
  private reconnectTimer: any = null;
  private url = 'ws://localhost:8000/ws';

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    
    // Check if running in browser
    if (typeof window === 'undefined') return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WS connected');
      if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { type, payload } = data;
        const typeListeners = this.listeners.get(type);
        if (typeListeners) {
          typeListeners.forEach(listener => listener(payload));
        }
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    this.ws.onclose = () => {
      console.log('WS disconnected, reconnecting in 3s...');
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };
  }

  subscribe(type: string, listener: Listener) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(listener);

    return () => {
      this.listeners.get(type)?.delete(listener);
    };
  }

  send(type: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    }
  }
}

export const wsManager = new WebSocketManager();
