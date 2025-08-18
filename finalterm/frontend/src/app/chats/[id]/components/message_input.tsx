"use client";

import { useState, useTransition } from "react";
import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";
import Typography from "@/components/ui/Typography";
import { chatService } from "@/services/chatService";

const MessageInput = ({ id }: { id: string }) => {
  const [message, setMessage] = useState("");
  const [sending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const handleSend = () => {
    if (!message.trim()) return;

    startTransition(async () => {
      try {
        // Send message via HTTP API
        await chatService.createMessage({ id, content: message });
        setMessage("");
        setError(null);
      } catch (error: any) {
        console.error(error);
        setError(error?.response?.data?.detail || "Failed to send message");
      }
    });
  };

  return (
    <div className="flex flex-col gap-2">
      {error && (
        <Typography
          variant="p"
          color="destructive"
          className="text-sm"
        >
          {error}
        </Typography>
      )}

      <div className="flex gap-2">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Type your message..."
        />
        <Button
          onClick={handleSend}
          disabled={sending || !message.trim()}
          loading={sending}
        >
          Send
        </Button>
      </div>
    </div>
  );
};

export default MessageInput;
