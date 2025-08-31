"use client";
import { Button } from "@/components/ui/button";
import { UserPlus } from "lucide-react";
import SearchUsersDialog from "@/components/ui/search-users-dialog";
import { chatService } from "@/services/chatService";
import { useToast } from "@/components/hooks/use-toast";
import { User } from "@/services/userService";

interface AddUsersButtonProps {
  chatId: number;
  chatName: string;
}

export default function AddUsersButton({ chatId, chatName }: AddUsersButtonProps) {
  const { toast } = useToast();

  const handleAddUser = async (user: User) => {
    try {
      await chatService.addUserToChat(chatId, user.id);
      toast({
        title: "Success",
        description: `Added ${user.username} to ${chatName}`,
      });
      // Don't close dialog - allow adding multiple users
    } catch (error: any) {
      // Handle different Django REST Framework error formats
      let errorMessage = "Failed to add user to chat";
      
      if (error.response?.data) {
        const data = error.response.data;
        // Check for our custom error format
        if (data.error) {
          errorMessage = data.error;
        }
        // Check for DRF validation errors
        else if (data.detail) {
          errorMessage = data.detail;
        }
        // Check for non-field errors
        else if (data.non_field_errors) {
          errorMessage = data.non_field_errors[0];
        }
        // Check for field-specific errors
        else if (typeof data === 'object') {
          const firstError = Object.values(data)[0];
          if (Array.isArray(firstError)) {
            errorMessage = firstError[0];
          } else if (typeof firstError === 'string') {
            errorMessage = firstError;
          }
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
    <SearchUsersDialog
      title="Add Users to Chat"
      description={`Search for users to add to ${chatName}`}
      keepOpenAfterAction={true}
      customActionButton={(user, closeDialog) => (
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleAddUser(user)}
          className="px-2 py-1 h-8"
        >
          <UserPlus className="w-3 h-3 mr-1" />
          Add
        </Button>
      )}
      trigger={
        <Button size="sm" variant="outline">
          <UserPlus className="w-4 h-4 mr-2" />
          Add Users
        </Button>
      }
    />
  );
}
