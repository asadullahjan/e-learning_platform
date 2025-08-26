"use client";

import { useState, useEffect } from "react";
import { Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import Typography from "@/components/ui/Typography";
import { chatService } from "@/services/chatService";
import UserAvatar from "@/components/user/user-avatar";
import Link from "next/link";

interface ParticipantUser {
  id: number;
  username: string;
  profile_picture?: string;
  role: string;
  created_at: string;
  email: string;
}

interface Participant {
  id: number;
  user: ParticipantUser;
  role: string;
  is_active: boolean;
}

interface ParticipantsDialogProps {
  chatId: string;
  trigger?: React.ReactNode;
}

export function ParticipantsDialog({ chatId, trigger }: ParticipantsDialogProps) {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const fetchParticipants = async () => {
    try {
      setIsLoading(true);
      const response = await chatService.getChatParticipants(chatId);
      setParticipants(response);
    } catch (error) {
      console.error("Failed to fetch participants:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchParticipants();
    }
  }, [isOpen, chatId]);

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "admin":
        return "Admin";
      default:
        return "Participant";
    }
  };

  const activeParticipants = participants.filter((p) => p.is_active);
  const inactiveParticipants = participants.filter((p) => !p.is_active);

  return (
    <Dialog
      open={isOpen}
      onOpenChange={setIsOpen}
    >
      <DialogTrigger asChild>
        {trigger || (
          <Button
            variant="ghost"
            size="sm"
            className="flex items-center gap-2"
          >
            <Users className="h-4 w-4" />
            <span className="hidden sm:inline">Participants</span>
          </Button>
        )}
      </DialogTrigger>
      <DialogContent>
        <DialogTitle className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          Chat Participants
        </DialogTitle>

        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-4">
              <Typography
                variant="span"
                color="muted"
              >
                Loading participants...
              </Typography>
            </div>
          ) : (
            <>
              {/* Active Participants */}
              <div>
                <Typography
                  variant="h4"
                  size="sm"
                  className="font-medium mb-2"
                >
                  Active ({activeParticipants.length})
                </Typography>
                <div className="space-y-2">
                  {activeParticipants.map((participant) => (
                    <div
                      key={participant.id}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <UserAvatar
                          user={{
                            ...participant.user,
                            role: participant.user.role as "student" | "teacher",
                          }}
                          size="sm"
                          showName={false}
                          clickable={false}
                        />
                        <div className="flex items-center gap-2">
                          <Link
                            href={`/users/${participant.user.username}`}
                            className="hover:underline text-blue-600 hover:text-blue-800"
                          >
                            <Typography
                              variant="span"
                              size="sm"
                              className="font-medium"
                            >
                              {participant.user.username}
                            </Typography>
                          </Link>
                        </div>
                      </div>
                      <Typography
                        variant="span"
                        size="xs"
                        color="muted"
                        className="px-2 py-1 bg-gray-200 rounded-full"
                      >
                        {getRoleLabel(participant.role)}
                      </Typography>
                    </div>
                  ))}
                </div>
              </div>

              {/* Inactive Participants */}
              {inactiveParticipants.length > 0 && (
                <div>
                  <Typography
                    variant="h4"
                    size="sm"
                    className="font-medium mb-2"
                  >
                    Inactive ({inactiveParticipants.length})
                  </Typography>
                  <div className="space-y-2">
                    {inactiveParticipants.map((participant) => (
                      <div
                        key={participant.id}
                        className="flex items-center justify-between p-3 bg-gray-100 rounded-lg opacity-60"
                      >
                        <div className="flex items-center gap-3">
                          <UserAvatar
                            user={{
                              ...participant.user,
                              role: participant.user.role as "student" | "teacher",
                            }}
                            size="sm"
                            showName={false}
                            clickable={false}
                          />
                          <div className="flex items-center gap-2">
                            <Link
                              href={`/users/${participant.user.username}`}
                              className="hover:underline text-blue-600 hover:text-blue-800"
                            >
                              <Typography
                                variant="span"
                                size="sm"
                                className="font-medium"
                              >
                                {participant.user.username}
                              </Typography>
                            </Link>
                          </div>
                        </div>
                        <Typography
                          variant="span"
                          size="xs"
                          color="muted"
                          className="px-2 py-1 bg-gray-200 rounded-full"
                        >
                          {getRoleLabel(participant.role)}
                        </Typography>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {participants.length === 0 && (
                <div className="text-center py-4">
                  <Typography
                    variant="span"
                    color="muted"
                  >
                    No participants found
                  </Typography>
                </div>
              )}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
