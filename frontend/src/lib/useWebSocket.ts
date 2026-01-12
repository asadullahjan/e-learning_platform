"use client";
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
}

export const isBrowser = typeof window !== "undefined";

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
  const shouldConnectRef = useRef(false);

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    console.log("🔌 Disconnecting WebSocket");
    shouldConnectRef.current = false;
    clearReconnectTimeout();

    if (wsRef.current) {
      // Remove event listeners to prevent unwanted callbacks
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;

      if (
        wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING
      ) {
        wsRef.current.close(1000, "Manual disconnect");
      }
      wsRef.current = null;
    }

    setIsConnecting(false);
    setIsReconnecting(false);
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, [clearReconnectTimeout]);

  const connect = useCallback(() => {
    // Remove overly restrictive auth checks - let the server handle auth if needed
    if (!url || !isBrowser) {
      console.log("❌ Cannot connect: invalid URL or not in browser");
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log("⚠️ WebSocket already connected");
      return;
    }

    if (wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log("⚠️ WebSocket already connecting");
      return;
    }

    console.log("🔌 Connecting to WebSocket:", url);
    shouldConnectRef.current = true;
    setIsConnecting(true);
    setIsReconnecting(false);

    try {
      // Clean up any existing connection first
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      wsRef.current = new WebSocket(url);

      wsRef.current.onopen = () => {
        console.log("✅ WebSocket connected successfully");
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
        console.log("🔌 WebSocket closed:", event.code, event.reason);
        setIsConnecting(false);
        setIsReconnecting(false);
        setIsConnected(false);

        // Only reconnect if we intended to stay connected and it wasn't a normal close
        const shouldReconnect =
          shouldConnectRef.current &&
          autoReconnect &&
          event.code !== 1000 && // Normal close
          event.code !== 1001 && // Going away
          event.code !== 4001 && // Unauthorized (don't retry)
          event.code !== 4003; // Forbidden (don't retry)

        if (shouldReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(
            `🔄 Reconnecting... attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`
          );

          setIsReconnecting(true);
          clearReconnectTimeout();
          reconnectTimeoutRef.current = setTimeout(() => {
            if (shouldConnectRef.current) {
              connect();
            }
          }, reconnectInterval);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          console.log("❌ Max reconnection attempts reached");
          shouldConnectRef.current = false;
        }

        onClose?.(event);
      };

      wsRef.current.onerror = (event) => {
        console.error("❌ WebSocket error:", event);
        setIsConnecting(false);
        onError?.(event);
      };
    } catch (error) {
      console.error("❌ Failed to create WebSocket:", error);
      setIsConnecting(false);
      shouldConnectRef.current = false;
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
    clearReconnectTimeout,
  ]);

  // Simplified effect - only connect when dependencies change, not on every render
  useEffect(() => {
    // Auto-connect if we have a URL and user is authenticated (if auth is required)
    if (url && user && isAuthenticated && !wsRef.current) {
      connect();
    }

    // Disconnect if user becomes unauthenticated
    if ((!user || !isAuthenticated) && wsRef.current) {
      disconnect();
    }
  }, [url, user, isAuthenticated]); // Removed connect/disconnect from deps to avoid infinite loops

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []); // Empty deps - only run on mount/unmount

  return {
    isConnected,
    isConnecting,
    isReconnecting,
    connect,
    disconnect,
  };
}
