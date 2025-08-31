import { useEffect, useRef, useCallback, useState } from "react";
import { useAuthStore } from "@/store/authStore";

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
  const hasInitializedRef = useRef(false);

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  // --- Core socket initializer ---
  const initSocket = useCallback(() => {
    try {
      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log("WebSocket connected successfully");
        isConnectingRef.current = false;
        isReconnectingRef.current = false;
        setIsConnecting(false);
        setIsReconnecting(false);
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      wsRef.current.onmessage = (event) => {
        onMessage?.(event);
      };

      wsRef.current.onclose = (event) => {
        console.log("WebSocket connection closed:", event.code, event.reason);
        isConnectingRef.current = false;
        isReconnectingRef.current = false;
        setIsConnecting(false);
        setIsReconnecting(false);
        setIsConnected(false);

        const shouldAttemptReconnect =
          shouldReconnectRef.current &&
          autoReconnect &&
          event.code !== 1000 &&
          event.code !== 4001 &&
          event.code !== 4003;

        if (shouldAttemptReconnect) {
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++;
            console.log(
              `Reconnecting... attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`
            );

            isReconnectingRef.current = true;
            setIsReconnecting(true);

            clearReconnectTimeout();
            reconnectTimeoutRef.current = setTimeout(() => {
              if (shouldReconnectRef.current && user && isAuthenticated) {
                initSocket();
              }
            }, reconnectInterval);
          } else {
            console.log("Max reconnection attempts reached");
          }
        }

        onClose?.(event);
      };

      wsRef.current.onerror = (event) => {
        console.error("WebSocket error:", event);
        onError?.(event);
      };
    } catch (error) {
      console.error("Failed to create WebSocket:", error);
      isConnectingRef.current = false;
      setIsConnecting(false);
    }
  }, [
    url,
    autoReconnect,
    reconnectInterval,
    maxReconnectAttempts,
    onOpen,
    onMessage,
    onClose,
    onError,
    isAuthenticated,
    user,
  ]);

  const connect = useCallback(() => {
    if (!user || !isAuthenticated) {
      console.log("User not authenticated, skipping WebSocket connection");
      return;
    }
    if (wsRef.current?.readyState === WebSocket.OPEN || isConnectingRef.current) {
      console.log("WebSocket already connected or connecting, skipping");
      return;
    }
    if (!url) {
      console.log("WebSocket URL is empty, skipping");
      return;
    }

    console.log("Connecting WebSocket:", url);
    isConnectingRef.current = true;
    setIsConnecting(true);
    setIsReconnecting(false);

    initSocket();
  }, [url, user, isAuthenticated, initSocket]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    clearReconnectTimeout();

    if (wsRef.current) {
      wsRef.current.close(1000, "Manual disconnect");
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
      console.warn("WebSocket not connected, cannot send message");
    }
  }, []);

  // Handle auth changes
  useEffect(() => {
    if (user && isAuthenticated && !hasInitializedRef.current) {
      hasInitializedRef.current = true;
      connect();
    } else if (!user || !isAuthenticated) {
      hasInitializedRef.current = false;
      disconnect();
    }
    return () => disconnect();
  }, [user, isAuthenticated, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => disconnect();
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
