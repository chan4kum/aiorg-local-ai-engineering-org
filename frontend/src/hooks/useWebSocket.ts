import { useEffect } from 'react';
import { wsManager } from '../lib/websocket';

export function useWebSocket(eventType: string, callback: (data: any) => void) {
  useEffect(() => {
    // Connect on mount (manager handles deduplication)
    wsManager.connect();
    
    const unsubscribe = wsManager.subscribe(eventType, callback);
    
    return () => {
      unsubscribe();
    };
  }, [eventType, callback]);
}
