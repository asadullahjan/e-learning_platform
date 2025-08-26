import ChatContainer from "./components/chat_container";
import { chatService } from "@/services/chatService";

const ChatPage = async ({ params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params;

  try {
    // Fetch both chat and messages on the server side
    const [chat, messagesResponse] = await Promise.all([
      chatService.server.getChat(id),
      chatService.server.getMessages(id, 1),
    ]);
    console.log(chat);
    return (
      <ChatContainer
        chatId={id}
        initialChat={chat}
        initialMessages={messagesResponse.results || []}
        hasNextPage={!!messagesResponse.next}
        nextUrl={messagesResponse.next}
      />
    );
  } catch (error: any) {
    // Handle errors on server side
    if (error.status === 403 || error.status === 404) {
      return (
        <div className="w-full flex flex-col">
          <div className="p-6 border rounded-lg">
            <h1 className="text-xl font-semibold mb-2">Chat Not Found</h1>
            <p className="text-gray-600 mb-4">
              This chat room doesn't exist or you don't have access to it.
            </p>
            <a
              href="/chats"
              className="text-blue-600 hover:underline"
            >
              Back to Chats
            </a>
          </div>
        </div>
      );
    }

    return (
      <div className="w-full flex flex-col">
        <div className="p-6 border rounded-lg">
          <h1 className="text-xl font-semibold mb-2">Error</h1>
          <p className="text-gray-600 mb-4">Something went wrong while loading this chat room.</p>
          <a
            href="/chats"
            className="text-blue-600 hover:underline"
          >
            Back to Chats
          </a>
        </div>
      </div>
    );
  }
};

export default ChatPage;
