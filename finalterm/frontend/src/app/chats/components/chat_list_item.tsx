"use client";

import Typography from "@/components/ui/Typography";
import { Chat } from "@/services/chatService";
import Link from "next/link";
import { MessageSquare, Users, BookOpen } from "lucide-react";

const ChatListItem = ({ chat }: { chat: Chat }) => {
  const getIcon = (chatType: string) => {
    switch (chatType) {
      case "direct":
        return <MessageSquare className="w-4 h-4 text-blue-500" />;
      case "group":
        return <Users className="w-4 h-4 text-green-500" />;
      case "course":
        return <BookOpen className="w-4 h-4 text-purple-500" />;
      default:
        return <MessageSquare className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <Link
      href={`/chats/${chat.id}`}
      className="block"
    >
      <div className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
        <div className="flex items-center space-x-3">
          {getIcon(chat.chat_type)}
          <Typography
            variant="span"
            className="text-sm truncate"
          >
            {chat.name}
          </Typography>
        </div>
      </div>
    </Link>
  );
};

const ChatSection = ({
  title,
  chats,
  maxHeight = 200,
}: {
  title: string;
  chats: Chat[];
  maxHeight?: number;
}) => {
  if (chats.length === 0) return null;

  return (
    <div className="mb-4">
      <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">
        {title} • {chats.length}
      </div>
      <div
        className="overflow-y-auto"
        style={{ maxHeight }}
      >
        {chats.map((chat) => (
          <ChatListItem
            key={chat.id}
            chat={chat}
          />
        ))}
      </div>
    </div>
  );
};

const ChatList = ({ userChats, allChats }: { userChats: Chat[]; allChats: Chat[] }) => {
  // Filter user's chats by type
  const userDirectChats = userChats.filter((chat) => chat.chat_type === "direct");
  const userGroupChats = userChats.filter((chat) => chat.chat_type === "group");
  const userCourseChats = userChats.filter((chat) => chat.chat_type === "course");

  return (
    <div className="py-2 space-y-6">
      {/* User's Chats - Quick Access */}
      <div>
        <div className="px-3 py-2 text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wide border-b border-blue-200 dark:border-blue-800">
          My Chats
        </div>
        <div className="space-y-4 mt-2">
          <ChatSection
            title="Direct Messages"
            chats={userDirectChats}
            maxHeight={120}
          />
          <ChatSection
            title="Group Chats"
            chats={userGroupChats}
            maxHeight={150}
          />
          <ChatSection
            title="Course Chats"
            chats={userCourseChats}
            maxHeight={200}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatList;
