"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import Input from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Search, Users, UserPlus, MessageCircle } from "lucide-react";
import Link from "next/link";
import { userService, User } from "@/services/userService";
import { useToast } from "@/components/hooks/use-toast";
import UserAvatar from "@/components/user/user-avatar";
import Typography from "@/components/ui/Typography";
import { Skeleton } from "@/components/ui/skeleton";

interface SearchUsersDialogProps {
  trigger?: React.ReactNode;
  title?: string;
  description?: string;
  customActionButton?: (user: User, closeDialog: () => void) => React.ReactNode;
  keepOpenAfterAction?: boolean;
}

export default function SearchUsersDialog({
  trigger,
  title = "Search Users",
  description = "Find and connect with other users",
  customActionButton,
  keepOpenAfterAction = false,
}: SearchUsersDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { toast } = useToast();

  const closeDialog = () => {
    if (!keepOpenAfterAction) {
      setIsOpen(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setUsers([]);
      setHasSearched(false);
      return;
    }

    try {
      setIsLoading(true);
      const results = await userService.searchUsers(searchQuery.trim());
      setUsers(results);
      setHasSearched(true);
    } catch (error) {
      console.error("Failed to search users:", error);
      toast({
        title: "Error",
        description: "Failed to search users. Please try again.",
        variant: "destructive",
      });
      setUsers([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  useEffect(() => {
    if (isOpen) {
      setSearchQuery("");
      setUsers([]);
      setHasSearched(false);
    }
  }, [isOpen]);

  return (
    <Dialog
      open={isOpen}
      onOpenChange={setIsOpen}
    >
      <DialogTrigger asChild>
        {trigger || (
          <Button
            variant="outline"
            size="sm"
          >
            <Users className="w-4 h-4 mr-2" />
            Search Users
          </Button>
        )}
      </DialogTrigger>
      <DialogContent>
        <div className="mb-4">
          <DialogTitle>{title}</DialogTitle>
          <Typography
            variant="p"
            color="muted"
            size="sm"
          >
            {description}
          </Typography>
        </div>

        <div className="space-y-4">
          {/* Search Input */}
          <div className="flex gap-2">
            <div className="flex-1">
              <Label
                htmlFor="search-users"
                className="sr-only"
              >
                Search users
              </Label>
              <Input
                id="search-users"
                placeholder="Search by username, first name, or last name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="pr-10"
              />
            </div>
            <Button
              onClick={handleSearch}
              disabled={isLoading || !searchQuery.trim()}
            >
              <Search className="w-4 h-4" />
            </Button>
          </div>

          {/* Results */}
          <div className="max-h-64 overflow-y-auto space-y-2">
            {isLoading && (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-2"
                  >
                    <Skeleton className="w-10 h-10 rounded-full" />
                    <div className="flex-1 space-y-1">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-3 w-32" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!isLoading && hasSearched && users.length === 0 && (
              <div className="text-center py-8">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <Typography
                  variant="p"
                  color="muted"
                >
                  No users found
                </Typography>
                <Typography
                  variant="p"
                  color="muted"
                  size="sm"
                >
                  Try a different search term
                </Typography>
              </div>
            )}

            {!isLoading && users.length > 0 && (
              <div className="space-y-2">
                {users.map((user) => (
                  <div
                    key={user.id}
                    className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    <UserAvatar
                      user={user}
                      size="md"
                      clickable={false}
                    />
                    <div className="flex-1 min-w-0">
                      <Link
                        href={`/users/${user.username}`}
                        className="hover:underline"
                      >
                        <Typography
                          variant="h6"
                          className="text-gray-900 font-medium truncate"
                        >
                          {user.username}
                        </Typography>
                      </Link>
                      <Typography
                        variant="span"
                        color="muted"
                        size="sm"
                        className="truncate block"
                      >
                        {user.first_name} {user.last_name}
                      </Typography>
                      <Typography
                        variant="span"
                        color="muted"
                        size="xs"
                        className="capitalize"
                      >
                        {user.role}
                      </Typography>
                    </div>
                    <div className="flex gap-2">
                      {customActionButton && customActionButton(user, closeDialog)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
