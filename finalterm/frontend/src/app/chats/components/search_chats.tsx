"use client";

import {
  Dialog,
  DialogDescription,
  DialogContent,
  DialogTrigger,
  DialogTitle,
} from "@/components/ui/dialog";
import Input from "@/components/ui/Input";
import { SearchIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { Chat, chatService } from "@/services/chatService";
import Typography from "@/components/ui/Typography";

const SearchChats = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [search, setSearch] = useState("");

  const fetchChats = async () => {
    const chats = await chatService.getChats(search);
    setChats(chats);
  };

  useEffect(() => {
    fetchChats();
  }, []);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="w-full">
          <SearchIcon
            size={16}
            className="mr-1"
          />
          Search chats
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Search chats</DialogTitle>
        <div className="flex gap-2">
          <Input
            placeholder="Search chats"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
            }}
          />
          <Button onClick={fetchChats}>Search</Button>
        </div>
        {chats && chats.length > 0 ? (
          chats.map((chat) => <div key={chat.id}>{chat.name}</div>)
        ) : (
          <Typography
            className="p-4 text-center"
            variant={"span"}
          >
            No chats found
          </Typography>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default SearchChats;
