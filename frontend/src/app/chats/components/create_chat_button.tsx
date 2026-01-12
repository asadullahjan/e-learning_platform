"use client";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import { chatService } from "@/services/chatService";
import { useState, useTransition } from "react";
import Input from "@/components/ui/Input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { showToast } from "@/lib/toast";
import { useRouter } from "next/navigation";
import { Label } from "@radix-ui/react-dropdown-menu";

const CreateChatButton = () => {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const router = useRouter();
  const [transitioning, startTransition] = useTransition();

  const handleCreateChat = () => {
    startTransition(async () => {
      try {
        const chat = await chatService.createChat({
          name,
          description,
          chat_type: "group",
          is_public: isPublic,
        });
        showToast.success("Chat created successfully");
        router.push(`/chats/${chat.id}`);
        setOpen(false);
        setName("");
        setDescription("");
      } catch (error) {
        console.error(error);
        showToast.error("Failed to create chat");
      }
    });
  };
  return (
    <Dialog
      open={open}
      onOpenChange={setOpen}
    >
      <DialogTrigger
        className="w-full"
        asChild
      >
        <Button className="w-full">
          <PlusIcon
            size={20}
            className="mr-1"
          />
          Create Chat
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Create Chat</DialogTitle>
        <DialogDescription>
          Create a new group chat to start a conversation.
          <div className="flex flex-col gap-2 mt-4">
            <Label>Name</Label>
            <Input
              placeholder="Enter chat name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Label>Description</Label>
            <Input
              placeholder="Enter chat description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <Label>Is Private</Label>
            <Input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
            />
            <Button
              onClick={handleCreateChat}
              loading={transitioning}
            >
              Create Chat
            </Button>
          </div>
        </DialogDescription>
      </DialogContent>
    </Dialog>
  );
};

export default CreateChatButton;
