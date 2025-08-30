"use client";

import { useEffect, useState, useRef } from "react";
import Typography from "@/components/ui/Typography";
import UserAvatar from "@/components/user/user-avatar";
import { LoadMoreButton } from "@/components/ui/load-more-button";
import { Chat, Message } from "@/services/chatService";
import { chatService } from "@/services/chatService";
import Link from "next/link";

const MessageList = ({
  chat_type,
  chatId,
  initialMessages,
  initialHasNextPage,
  initialNextUrl,
}: {
  chat_type: Chat["chat_type"];
  chatId: string;
  initialMessages: Message[];
  initialHasNextPage: boolean;
  initialNextUrl: string | null;
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasNextPage, setIsHasNextPage] = useState(initialHasNextPage);
  const [nextUrl, setNextUrl] = useState<string | null>(initialNextUrl);
  const [initialLoadComplete, setInitialLoadComplete] = useState(true); // Already loaded from server
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Ensure initial messages are properly sorted
  useEffect(() => {
    if (initialMessages.length > 0) {
      const sortedMessages = [...initialMessages].sort(
        (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setMessages(sortedMessages);
    }
  }, [initialMessages]);

  const loadMore = async () => {
    if (isLoadingMore || !hasNextPage || !nextUrl) return;

    try {
      setIsLoadingMore(true);

      // Extract page parameter from the next URL
      const url = new URL(nextUrl, window.location.origin);
      const page = url.searchParams.get("page");

      if (!page) {
        throw new Error("No page parameter found in next URL");
      }

      const response = await chatService.getMessages(chatId, parseInt(page));

      // Add older messages to the beginning (since they're older)
      // Sort the combined messages to maintain proper chronological order
      const combinedMessages = [...response.results, ...messages];
      const sortedMessages = combinedMessages.sort(
        (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );

      setMessages(sortedMessages);
      setNextUrl(response.next);
      setIsHasNextPage(!!response.next);
    } catch (error) {
      console.error("Failed to load older messages:", error);
    } finally {
      setIsLoadingMore(false);
    }
  };

  // Auto-scroll to bottom when new messages arrive or on initial load
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Scroll to bottom on initial load completion
  useEffect(() => {
    if (initialLoadComplete && messages.length > 0) {
      scrollToBottom();
    }
  }, [initialLoadComplete, messages.length]);

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    console.log("Attempting to connect to WebSocket...");
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WEBSOCKET_BASE_URL}/ws/chat/${chatId}/`);

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
        if (data.type === "message_created") {
          // Add new message at the end (bottom)
          const newMessage = data.message;
          setMessages((prev) => {
            // Ensure the new message is added at the end and maintain chronological order
            const updatedMessages = [...prev, newMessage];
            return updatedMessages.sort(
              (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
            );
          });
          console.log("New message received:", newMessage);
          scrollToBottom();
        } else if (data.type === "message_updated") {
          const updatedMessage = data.message;
          setMessages((prev) =>
            prev.map((msg) => (msg.id === updatedMessage.id ? updatedMessage : msg))
          );
          console.log("Message updated:", updatedMessage);
        } else if (data.type === "message_deleted") {
          const deletedMessage = data.message;
          setMessages((prev) => prev.filter((msg) => msg.id !== deletedMessage.id));
          console.log("Message deleted:", deletedMessage);
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
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Load More Button for Older Messages */}
        {hasNextPage && (
          <LoadMoreButton
            onClick={loadMore}
            isLoading={isLoadingMore}
            hasNextPage={hasNextPage}
            className="w-full"
          />
        )}

        {/* Show loading indicator when loading more messages */}
        {isLoadingMore && (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 mx-auto"></div>
            <Typography
              variant="span"
              size="sm"
              className="text-gray-500 mt-2 block"
            >
              Loading older messages...
            </Typography>
          </div>
        )}

        {messages.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Typography
              variant="span"
              size="sm"
            >
              No messages yet. Start the conversation!
            </Typography>
          </div>
        ) : (
          messages.map((message: Message) => (
            <div
              key={message.id}
              className="flex items-start gap-2 bg-gray-100 dark:bg-gray-800 p-3 rounded-md"
            >
              <UserAvatar
                user={message.sender}
                size="sm"
                showName={false}
                clickable={false}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Link
                    href={`/users/${message.sender.username}`}
                    className="hover:underline"
                  >
                    <Typography
                      variant="span"
                      className="text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                      {message.sender.username}
                    </Typography>
                  </Link>
                  <Typography
                    variant="span"
                    size="sm"
                    className="text-xs text-gray-500"
                  >
                    {new Date(message.created_at).toLocaleString()}
                  </Typography>
                </div>
                <Typography
                  variant="span"
                  className="text-sm text-gray-600 dark:text-gray-400 block"
                >
                  {message.content}
                </Typography>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;
