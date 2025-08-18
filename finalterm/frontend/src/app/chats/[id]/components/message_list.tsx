"use client";

import { useEffect, useState, useRef } from "react";
import Typography from "@/components/ui/Typography";
import UserAvatar from "@/components/user/user-avatar";
import { Chat, Message } from "@/services/chatService";

const MessageList = ({
  chat_type,
  messages: initialMessages,
  chatId,
}: {
  chat_type: Chat["chat_type"];
  messages: Message[];
  chatId: string;
}) => {
  // Reverse the messages so newest appear at bottom (better chat UX)
  const [messages, setMessages] = useState<Message[]>([...initialMessages].reverse());
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    console.log("Attempting to connect to WebSocket...");
    const ws = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/`);

    ws.onopen = () => {
      console.log("WebSocket connected for listening");
      setIsConnected(true);
      setIsReconnecting(false);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("WebSocket message received:", data);

        // Handle different event types from your backend
        // Backend sends: { type: "message_created", message: {...} }
        if (data.type === "message_created") {
          // Add new message at the end (bottom)
          setMessages((prev) => [...prev, data.message]);
        } else if (data.type === "message_updated") {
          setMessages((prev) =>
            prev.map((msg) => (msg.id === data.message.id ? data.message : msg))
          );
        } else if (data.type === "message_deleted") {
          setMessages((prev) => prev.filter((msg) => msg.id !== data.message.id));
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onclose = (event) => {
      console.log("WebSocket disconnected:", event.code, event.reason);
      setIsConnected(false);

      // Only attempt to reconnect if it wasn't a manual close
      if (event.code !== 1000) {
        setIsReconnecting(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log("Attempting to reconnect...");
          connectWebSocket();
        }, 3000);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000); // Normal closure
      }
    };
  }, [chatId]);

  return (
    <div className="flex flex-col h-full">
      {/* Connection Status */}
      <div className="px-3 py-2 border-b sticky top-0 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-green-500" : isReconnecting ? "bg-yellow-500" : "bg-red-500"
            }`}
          />
          <Typography
            variant="span"
            className="text-xs text-gray-500"
          >
            {isConnected
              ? "Listening for messages..."
              : isReconnecting
              ? "Reconnecting..."
              : "Connecting..."}
          </Typography>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1  overflow-y-auto p-3 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 p-3 rounded-md"
          >
            <UserAvatar
              user={message.sender}
              size="sm"
              showName={false}
              clickable={false}
            />
            <div className="flex-1">
              <Typography
                variant="span"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {message.sender.username}
              </Typography>
              <Typography
                variant="span"
                className="text-sm text-gray-600 dark:text-gray-400 block mt-1"
              >
                {message.content}
              </Typography>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;
