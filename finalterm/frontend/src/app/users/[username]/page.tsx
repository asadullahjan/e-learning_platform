"use client";

import { notFound } from "next/navigation";
import { useRef, useEffect, useState } from "react";
import Typography from "@/components/ui/Typography";
import UserStatusList, { UserStatusListRef } from "./components/user-status-list";
import CreateStatusButton from "@/app/home/components/create-status-button";
import UserAvatar from "@/components/user/user-avatar";
import { Button } from "@/components/ui/button";
import { MessageCircle } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { userService, User } from "@/services/userService";
import { chatService } from "@/services/chatService";
import { useToast } from "@/components/hooks/use-toast";
import React from "react";

interface UserProfilePageProps {
  params: Promise<{
    username: string;
  }>;
}

export default function UserProfilePage({ params }: UserProfilePageProps) {
  const { username } = React.use(params);
  const statusListRef = useRef<UserStatusListRef>(null);
  const { user: currentUser } = useAuthStore();
  const router = useRouter();
  const { toast } = useToast();

  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStartingChat, setIsStartingChat] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setIsLoading(true);
        const userData = await userService.getUserByUsername(username);
        setUser(userData);
      } catch (error) {
        console.error("Failed to fetch user:", error);
        toast({
          title: "Error",
          description: "Failed to load user profile",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [username, toast]);

  const handleStatusCreated = () => {
    if (statusListRef.current) {
      statusListRef.current.refresh();
    }
  };

  const handleStartChat = async () => {
    if (!currentUser || !user) return;

    try {
      setIsStartingChat(true);
      const response = await chatService.findOrCreateDirectChat(user.id);

      toast({
        title: "Success",
        description: `Navigating to chat with ${username}`,
      });

      router.push(`/chats/${response.id}`);
    } catch (error) {
      console.error("Failed to start chat:", error);
      toast({
        title: "Error",
        description: "Failed to start chat. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsStartingChat(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8 shadow-sm">
          <div className="text-center">
            <div className="animate-pulse">
              <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-32 mx-auto mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-24 mx-auto mb-3"></div>
              <div className="h-4 bg-gray-200 rounded w-32 mx-auto"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto text-center py-8">
        <Typography
          variant="h2"
          color="error"
        >
          User not found
        </Typography>
        <Typography
          variant="p"
          color="muted"
        >
          The user "{username}" could not be found.
        </Typography>
      </div>
    );
  }

  const isOwnProfile = currentUser?.username === username;
  const joinDate = new Date(user.created_at).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="mx-auto">
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8 shadow-sm">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <UserAvatar
              user={user}
              size="4xl"
              clickable={false}
              showName={false}
            />
          </div>

          <Typography
            variant="h1"
            className="text-gray-900 mb-2"
          >
            {user.username}
          </Typography>

          <Typography
            variant="p"
            color="muted"
            className="mb-3"
          >
            {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
          </Typography>

          <Typography
            variant="span"
            color="muted"
            size="sm"
            className="block mb-4"
          >
            Member since {joinDate}
          </Typography>

          {!isOwnProfile && (
            <Button
              onClick={handleStartChat}
              disabled={isStartingChat}
              className="inline-flex items-center gap-2"
            >
              <MessageCircle className="w-4 h-4" />
              {isStartingChat ? "Starting Chat..." : "Start Chat"}
            </Button>
          )}
        </div>
      </div>

      <div className="mb-6">
        <Typography
          variant="h2"
          className="text-gray-900 mb-2"
        >
          Status Updates
        </Typography>
        <Typography
          variant="p"
          color="muted"
        >
          Recent updates from {user.username}
        </Typography>
      </div>

      {isOwnProfile && <CreateStatusButton onStatusCreated={handleStatusCreated} />}
      <UserStatusList
        ref={statusListRef}
        user={user}
      />
    </div>
  );
}
