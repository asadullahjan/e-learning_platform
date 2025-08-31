"use client";

import { Button } from "@/components/ui/button";
import { useTransition } from "react";
import { chatService } from "@/services/chatService";
import { useRouter } from "next/navigation";
import { showToast } from "@/lib/toast";

interface JoinChatButtonProps {
  chatId: number;
}

const JoinChatButton = ({ chatId }: JoinChatButtonProps) => {
  const [joining, startTransition] = useTransition();
  const router = useRouter();

  const handleJoin = async () => {
    startTransition(async () => {
      try {
        await chatService.joinChatRoom(chatId);
        router.refresh();
      } catch (error) {
        console.error("Failed to join chat:", error);
        showToast.error("Failed to join chat");
      }
    });
  };

  return (
    <div className="w-full text-center">
      <div className="text-sm text-gray-600 mb-2">
        You can view messages but need to join to participate
      </div>
      <Button
        className="w-full"
        onClick={handleJoin}
        disabled={joining}
        loading={joining}
      >
        Join Chat Room
      </Button>
    </div>
  );
};

export default JoinChatButton;
