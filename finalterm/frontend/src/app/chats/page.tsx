import { chatService } from "@/services/chatService";
import ChatSidebar from "./components/chats_sidebar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import CreateChatButton from "./components/create_chat_button";
import SearchChats from "./components/search_chats";
import ChatList from "./components/chat_list_item";

async function ChatPage() {
  // Fetch both user's chats and all available chats
  const [userChats, allChats] = await Promise.all([
    chatService.server.getUserChats(),
    chatService.server.getChats(),
  ]);

  const hasAnyChats = (userChats && userChats.length > 0) || (allChats && allChats.length > 0);

  return (
    <>
      {hasAnyChats ? (
        <ChatList
          userChats={userChats || []}
          allChats={allChats || []}
        />
      ) : (
        <Card className="flex flex-col items-center justify-center h-[70vh] w-full">
          <CardHeader className="flex flex-col items-center justify-center">
            <CardTitle>No chats found</CardTitle>
            <CardDescription>Create a new chat to start a conversation.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 w-xs mx-auto">
            <CreateChatButton />
            <SearchChats />
          </CardContent>
        </Card>
      )}
    </>
  );
}

export default ChatPage;
