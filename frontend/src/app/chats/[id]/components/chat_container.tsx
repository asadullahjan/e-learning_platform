"use client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { chatService, Chat, Message } from "@/services/chatService";
import { Link } from "lucide-react";
import JoinChatButton from "./join_chat_button";
import MessageInput from "./message_input";
import MessageList from "./message_list";
import AddUsersButton from "./add_users_button";
import LeaveChatButton from "./leave_chat_button";
import { useEffect, useState } from "react";
import { ParticipantsDialog } from "./participants_dialog";

interface ChatContainerProps {
  chatId: number;
  initialChat: Chat;
  initialMessages: Message[];
  hasNextPage: boolean;
  nextUrl: string | null;
}

const ChatContainer = ({
  chatId,
  initialChat,
  initialMessages,
  hasNextPage,
  nextUrl,
}: ChatContainerProps) => {
  const [chat, setChat] = useState<Chat>(initialChat);
  const [participantStatus, setParticipantStatus] = useState<{
    is_participant: boolean;
    role: string | null;
  } | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);

  // Extract participant status from chat data
  useEffect(() => {
    if (chat) {
      setParticipantStatus(
        chat.current_user_status || {
          is_participant: false,
          role: null,
        }
      );
      setIsProcessing(false);
    }
  }, [chat]);

  // Show processing state while determining participant status
  if (isProcessing) {
    return (
      <Card className="w-full flex flex-col h-full min-h-[80vh]">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-6 w-48 rounded"></div>
          </div>
        </CardHeader>
        <CardContent className="border-t border-gray-200 flex-1 p-6">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <div className="mt-2 text-gray-600">Processing chat access...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (participantStatus?.is_participant) {
    return (
      <Card className="w-full flex flex-col h-full min-h-[80vh]">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle>{chat.name}</CardTitle>
              <CardDescription>
                {chat.description}
                {participantStatus?.role && (
                  <span className="ml-2 text-sm text-blue-600">• {participantStatus.role}</span>
                )}
                {chat?.is_public && <span className="ml-2 text-sm text-green-600">• public</span>}
              </CardDescription>
            </div>
            {participantStatus?.role === "admin" && (
              <div className="ml-4">
                <AddUsersButton
                  chatId={chatId}
                  chatName={chat?.name || "Chat"}
                />
              </div>
            )}
            {/* Show Leave Chat button for all participants in any chat type */}
            {participantStatus?.is_participant && (
              <div className="ml-4">
                <LeaveChatButton
                  chatId={chatId}
                  chatName={chat?.name || "Chat"}
                  chatType={chat?.chat_type || "direct"}
                />
              </div>
            )}
            {/* Show Participants button for all participants */}
            {participantStatus?.is_participant && (
              <div className="ml-4">
                <ParticipantsDialog 
                  chatId={chatId} 
                />
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="border-t max-h-[80vh] overflow-y-auto border-gray-200 flex-1 p-0">
          <MessageList
            chat_type={chat?.chat_type || "direct"}
            chatId={chatId}
            initialMessages={initialMessages}
            initialHasNextPage={hasNextPage}
            initialNextUrl={nextUrl}
          />
        </CardContent>
        <CardFooter className="py-2">
          <MessageInput id={chatId} />
        </CardFooter>
      </Card>
    );
  }

  // User is not a participant - show messages but replace input with join button
  return (
    <Card className="w-full flex flex-col">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>{chat?.name}</CardTitle>
            <CardDescription>
              {chat?.description}
              {chat?.is_public && <span className="ml-2 text-sm text-green-600">• Public</span>}
            </CardDescription>
          </div>
          {participantStatus?.role === "admin" && (
            <div className="ml-4">
              <AddUsersButton
                chatId={chatId}
                chatName={chat?.name || "Chat"}
              />
            </div>
          )}
          {/* Show Leave Chat button for all participants in any chat type */}
          {participantStatus?.is_participant && (
            <div className="ml-4">
              <LeaveChatButton
                chatId={chatId}
                chatName={chat?.name || "Chat"}
                chatType={chat?.chat_type || "direct"}
              />
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="border-t max-h-[80vh] overflow-y-auto border-gray-200 flex-1 p-0">
        <MessageList
          chat_type={chat?.chat_type || "direct"}
          chatId={chatId}
          initialMessages={initialMessages}
          initialHasNextPage={hasNextPage}
          initialNextUrl={nextUrl}
        />
      </CardContent>
      <CardFooter className="py-2">
        {chat?.is_public ? (
          <JoinChatButton chatId={chatId} />
        ) : (
          <div className="w-full text-center">
            <div className="text-sm text-gray-600">
              This is a private chat room. You need to be invited by an admin to participate.
            </div>
          </div>
        )}
      </CardFooter>
    </Card>
  );
};

export default ChatContainer;
