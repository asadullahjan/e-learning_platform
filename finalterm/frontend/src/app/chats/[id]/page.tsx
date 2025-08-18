import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { chatService } from "@/services/chatService";
import MessageInput from "./components/message_input";
import MessageList from "./components/message_list";
import JoinChatButton from "./components/join_chat_button";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const ChatPage = async ({ params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params;

  try {
    // Fetch chat data and messages concurrently
    const [chat, messages] = await Promise.all([
      chatService.server.getChat(id),
      chatService.server.getMessages(id),
    ]);

    // Extract participant status from chat data
    const participantStatus = chat.current_user_status || {
      is_participant: false,
      role: null,
    };

    console.log(participantStatus);

    if (participantStatus.is_participant) {
      return (
        <Card className="w-full flex flex-col">
          <CardHeader>
            <CardTitle>{chat?.name}</CardTitle>
            <CardDescription>
              {chat?.description}
              {participantStatus.role && (
                <span className="ml-2 text-sm text-blue-600">• {participantStatus.role}</span>
              )}
              {chat?.is_public && <span className="ml-2 text-sm text-green-600">• Public</span>}
            </CardDescription>
          </CardHeader>
          <CardContent className="border-t max-h-[80vh] overflow-y-auto border-gray-200 flex-1 p-0">
            <MessageList
              chat_type={chat?.chat_type}
              messages={messages}
              chatId={id}
            />
          </CardContent>
          <CardFooter className="py-2">
            <MessageInput id={id} />
          </CardFooter>
        </Card>
      );
    }

    // User is not a participant - show messages but replace input with join button
    return (
      <Card className="w-full flex flex-col">
        <CardHeader>
          <CardTitle>{chat?.name}</CardTitle>
          <CardDescription>
            {chat?.description}
            {chat?.is_public && <span className="ml-2 text-sm text-green-600">• Public</span>}
          </CardDescription>
        </CardHeader>
        <CardContent className="border-t max-h-[80vh] overflow-y-auto border-gray-200 flex-1 p-0">
          <MessageList
            chat_type={chat?.chat_type}
            messages={messages}
            chatId={id}
          />
        </CardContent>
        <CardFooter className="py-2">
          {chat?.is_public ? (
            <JoinChatButton chatId={id} />
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
  } catch (error: any) {
    if (error.status === 403 || error.status === 404) {
      return (
        <Card className="w-full flex flex-col">
          <CardHeader>
            <CardTitle>Chat Not Found</CardTitle>
            <CardDescription>
              This chat room doesn't exist or you don't have access to it.
            </CardDescription>
          </CardHeader>
          <CardContent className="border-t border-gray-200 p-6">
            <div className="text-center space-y-4">
              <div className="text-gray-600">
                The chat room may be private or may have been deleted.
              </div>
              <Link href="/chats">
                <Button>Back to Chats</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      );
    }

    // Generic error
    return (
      <Card className="w-full flex flex-col">
        <CardHeader>
          <CardTitle>Error</CardTitle>
          <CardDescription>Something went wrong while loading this chat room.</CardDescription>
        </CardHeader>
        <CardContent className="border-t border-gray-200 p-6">
          <div className="text-center space-y-4">
            <div className="text-gray-600">Please try again later.</div>
            <Link href="/chats">
              <Button>Back to Chats</Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    );
  }
};

export default ChatPage;
