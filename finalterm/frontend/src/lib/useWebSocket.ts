import { useEffect, useRef, useCallback, useState } from 'react';
import { useAuthStore } from '@/store/authStore';

interface UseWebSocketOptions {
  url: string;
  onMessage?: (event: MessageEvent) => void;
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  connect: () => void;
  disconnect: () => void;
  send: (data: string | ArrayBufferLike | Blob | ArrayBufferView) => void;
}

export function useWebSocket({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  autoReconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions): UseWebSocketReturn {
  const { user, isAuthenticated } = useAuthStore();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isConnectingRef = useRef(false);
  const isReconnectingRef = useRef(false);
  const shouldReconnectRef = useRef(true);

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    // Don't connect if user is not authenticated
    if (!user || !isAuthenticated) {
      console.log('User not authenticated, skipping WebSocket connection');
      return;
    }

    // Don't connect if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN || isConnectingRef.current) {
      return;
    }

    // Don't connect if URL is empty
    if (!url) {
      console.log('WebSocket URL is empty, skipping connection');
      return;
    }

    console.log('Attempting to connect to WebSocket:', url);
    
    isConnectingRef.current = true;
    setIsConnecting(true);
    setIsReconnecting(false);

    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected successfully');
        isConnectingRef.current = false;
        setIsConnecting(false);
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      wsRef.current.onmessage = (event) => {
        onMessage?.(event);
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        isConnectingRef.current = false;
        setIsConnecting(false);
        setIsConnected(false);

        // Only attempt to reconnect if it wasn't a deliberate close and auto-reconnect is enabled
        if (shouldReconnectRef.current && autoReconnect && event.code !== 1000 && event.code !== 4001 && event.code !== 4003) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            isReconnectingRef.current = true;
            setIsReconnecting(true);
            reconnectAttemptsRef.current++;

            clearReconnectTimeout();
            reconnectTimeoutRef.current = setTimeout(() => {
              console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
              connect();
            }, reconnectInterval);
          } else {
            console.log('Max reconnection attempts reached');
            setIsReconnecting(false);
          }
        }

        onClose?.(event);
      };

      wsRef.current.onerror = (event) => {
        console.error('WebSocket error:', event);
        onError?.(event);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      isConnectingRef.current = false;
      setIsConnecting(false);
    }
  }, [url, user, isAuthenticated, autoReconnect, reconnectInterval, maxReconnectAttempts, onOpen, onMessage, onClose, onError]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    clearReconnectTimeout();
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    isConnectingRef.current = false;
    isReconnectingRef.current = false;
    setIsConnecting(false);
    setIsReconnecting(false);
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, [clearReconnectTimeout]);

  const send = useCallback((data: string | ArrayBufferLike | Blob | ArrayBufferView) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
    } else {
      console.warn('WebSocket is not connected, cannot send message');
    }
  }, []);

  // Effect to handle user authentication changes
  useEffect(() => {
    if (user && isAuthenticated) {
      // User is authenticated, connect to WebSocket
      connect();
    } else {
      // User is not authenticated, disconnect and clean up
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [user, isAuthenticated, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isConnecting,
    isReconnecting,
    connect,
    disconnect,
    send,
  };
}
