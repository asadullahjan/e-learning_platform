"use client";

import { useState, useEffect } from "react";
import { Users, Crown, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import Typography from "@/components/ui/Typography";
import { chatService } from "@/services/chatService";

interface Participant {
  id: number;
  user: {
    id: number;
    username: string;
    profile_picture?: string;
  };
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

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "admin":
        return <Crown className="h-4 w-4 text-yellow-500" />;
      case "moderator":
        return <Crown className="h-4 w-4 text-blue-500" />;
      default:
        return <User className="h-4 w-4 text-gray-500" />;
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "admin":
        return "Admin";
      case "moderator":
        return "Moderator";
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
                      className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                    >
                      <div className="flex items-center gap-2">
                        {getRoleIcon(participant.role)}
                        <Typography
                          variant="span"
                          size="sm"
                        >
                          {participant.user.username}
                        </Typography>
                      </div>
                      <Typography
                        variant="span"
                        size="xs"
                        color="muted"
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
                        className="flex items-center justify-between p-2 bg-gray-100 rounded-lg opacity-60"
                      >
                        <div className="flex items-center gap-2">
                          {getRoleIcon(participant.role)}
                          <Typography
                            variant="span"
                            size="sm"
                          >
                            {participant.user.username}
                          </Typography>
                        </div>
                        <Typography
                          variant="span"
                          size="xs"
                          color="muted"
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
