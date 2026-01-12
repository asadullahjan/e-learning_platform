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
import { ListResponse } from "@/lib/types";
import Link from "next/link";

const SearchChats = () => {
  const [chats, setChats] = useState<ListResponse<Chat>>({
    count: 0,
    next: null,
    previous: null,
    results: [],
  });
  const [search, setSearch] = useState<string>("");

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
        <div className="space-y-2 py-4">
          {chats && chats.results.length > 0 ? (
            chats.results.map((chat) => (
              <Button
                asChild
                variant={"outline"}
                key={chat.id}
                className="w-full"
              >
                <Link href={`/chats/${chat.id}`}>{chat.name}</Link>
              </Button>
            ))
          ) : (
            <Typography
              className="p-4 text-center"
              variant={"span"}
            >
              No chats found
            </Typography>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SearchChats;
