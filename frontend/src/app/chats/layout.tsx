import ChatSidebar from "./components/chats_sidebar";

const ChatLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex gap-4">
      <ChatSidebar />
      <div className="flex-1">{children}</div>
    </div>
  );
};

export default ChatLayout;
