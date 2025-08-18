import ChatContainer from "./components/chat_container";

const ChatPage = async ({ params }: { params: Promise<{ id: string }> }) => {
  const { id } = await params;

  return <ChatContainer chatId={id} />;
};

export default ChatPage;
