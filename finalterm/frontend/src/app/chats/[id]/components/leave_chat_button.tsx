"use client";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { chatService } from "@/services/chatService";
import { useToast } from "@/components/hooks/use-toast";
import { useRouter } from "next/navigation";

interface LeaveChatButtonProps {
  chatId: string;
  chatName: string;
  chatType: string;
}

export default function LeaveChatButton({ chatId, chatName, chatType }: LeaveChatButtonProps) {
  const { toast } = useToast();
  const router = useRouter();

  const handleLeaveChat = async () => {
    try {
      await chatService.deactivateChat(chatId);
      toast({
        title: "Success",
        description: `You have left ${chatName}`,
      });
      // Redirect to chats list
      router.push("/chats");
    } catch (error: any) {
      let errorMessage = "Failed to leave chat";
      
      if (error.response?.data) {
        const data = error.response.data;
        if (data.error) {
          errorMessage = data.error;
        } else if (data.detail) {
          errorMessage = data.detail;
        }
      }
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleLeaveChat}
      className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
    >
      <LogOut className="w-4 h-4 mr-2" />
      Leave Chat
    </Button>
  );
}
