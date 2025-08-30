"use client";
import { chatService, Message, Chat } from "@/services/chatService";
import ChatContainer from "@/app/chats/[id]/components/chat_container";
import { useState, useEffect } from "react";
import { ListResponse } from "@/lib/types";

const CourseChat = ({ chatId }: { chatId: string }) => {
  const [chat, setChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<ListResponse<Message> | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    Promise.all([
      chatService.server.getChat(chatId),
      chatService.server.getMessages(chatId, 1),
    ]).then(([chat, messagesResponse]) => {
      setChat(chat);
      setMessages(messagesResponse);
      setLoading(false);
    });
  }, [chatId]);

  if (loading) {
    return (
      <div className="w-full flex flex-col">
        <div className="p-6 border rounded-lg">
          <h1 className="text-xl font-semibold mb-2">Loading...</h1>
        </div>
      </div>
    );
  }

  if (!chat || !messages) {
    // Handle errors on server side
    return (
      <div className="w-full flex flex-col">
        <div className="p-6 border rounded-lg">
          <h1 className="text-xl font-semibold mb-2">Chat Not Found</h1>
          <p className="text-gray-600 mb-4">
            This chat room doesn't exist or you don't have access to it.
          </p>
        </div>
      </div>
    );
  }

  if (chat && messages) {
    return (
      <ChatContainer
        chatId={chatId}
        initialChat={chat}
        initialMessages={messages?.results || []}
        hasNextPage={!!messages?.next}
        nextUrl={messages?.next}
      />
    );
  }
};

export default CourseChat;
