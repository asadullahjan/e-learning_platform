import { chatService } from "@/services/chatService";
import CreateChatButton from "./create_chat_button";
import ChatList from "./chat_list_item";
import { Card } from "@/components/ui/card";

async function ChatSidebar() {
  const userChats = await chatService.server.getUserChats();
  return (
    <Card className="w-64 h-screen hidden md:block p-4">
      <div className="mb-4 w-full">
        <CreateChatButton />
      </div>
      {userChats && userChats.length > 0 ? (
        <ChatList
          userChats={userChats}
          allChats={[]}
        />
      ) : (
        <div className="text-center text-gray-500">No chats found</div>
      )}
    </Card>
  );
}

export default ChatSidebar;
