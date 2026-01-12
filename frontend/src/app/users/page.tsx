"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Search, Users, Filter } from "lucide-react";
import Link from "next/link";
import { userService, User } from "@/services/userService";
import { useToast } from "@/components/hooks/use-toast";
import UserAvatar from "@/components/user/user-avatar";
import Typography from "@/components/ui/Typography";
import { Skeleton } from "@/components/ui/skeleton";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function UsersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const { toast } = useToast();

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    // Only filter when we have users and search query or role filter changes
    if (users.length > 0) {
      filterUsers();
    }
  }, [users, searchQuery, roleFilter]);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      const results = await userService.listUsers();
      setUsers(results);
    } catch (error) {
      console.error("Failed to load users:", error);
      toast({
        title: "Error",
        description: "Failed to load users. Please try again.",
        variant: "destructive",
      });
      setUsers([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (user) =>
          user.username.toLowerCase().includes(query) ||
          user.first_name.toLowerCase().includes(query) ||
          user.last_name.toLowerCase().includes(query)
      );
    }

    // Apply role filter
    if (roleFilter !== "all") {
      filtered = filtered.filter((user) => user.role === roleFilter);
    }

    setFilteredUsers(filtered);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      // If no search query, load all users
      await loadUsers();
      return;
    }

    try {
      setIsLoading(true);
      const results = await userService.searchUsers(searchQuery.trim());
      setUsers(results);
      setFilteredUsers(results);
    } catch (error) {
      console.error("Failed to search users:", error);
      toast({
        title: "Error",
        description: "Failed to search users. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const clearFilters = async () => {
    setSearchQuery("");
    setRoleFilter("all");
    await loadUsers();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <Typography
          variant="h1"
          className="text-3xl font-bold mb-2"
        >
          Browse Users
        </Typography>
        <Typography
          variant="p"
          color="muted"
        >
          Discover and connect with students and teachers in the eLearning community
        </Typography>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-4">
        {/* Search Input */}
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

        {/* Role Filter */}
        <div className="w-full md:w-48">
          <Select
            value={roleFilter}
            onValueChange={setRoleFilter}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Roles</SelectItem>
              <SelectItem value="student">Students</SelectItem>
              <SelectItem value="teacher">Teachers</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Search Button */}
        <Button
          onClick={handleSearch}
          disabled={isLoading}
        >
          <Search className="w-4 h-4 mr-2" />
          {searchQuery.trim() ? "Search" : "Load All"}
        </Button>

        {/* Clear Filters */}
        {(searchQuery || roleFilter !== "all") && (
          <Button
            variant="outline"
            onClick={clearFilters}
          >
            <Filter className="w-4 h-4 mr-2" />
            Clear
          </Button>
        )}
      </div>

      {/* Results Section */}
      <div className="space-y-4">
        {/* Results Header */}
        <div className="flex justify-between items-center">
          <Typography
            variant="h6"
            className="text-gray-700"
          >
            {isLoading ? "Loading..." : `${filteredUsers.length} users found`}
          </Typography>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card
                key={i}
                className="p-4"
              >
                <div className="flex items-center gap-3">
                  <Skeleton className="w-12 h-12 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-3 w-32" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* No Results */}
        {!isLoading && filteredUsers.length === 0 && (
          <Card className="p-12 text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <Typography
              variant="h6"
              className="text-gray-600 mb-2"
            >
              No users found
            </Typography>
            <Typography
              variant="p"
              color="muted"
              className="mb-4"
            >
              {searchQuery || roleFilter !== "all"
                ? "Try adjusting your search criteria or filters"
                : "No users are currently available"}
            </Typography>
            {(searchQuery || roleFilter !== "all") && (
              <Button
                onClick={clearFilters}
                variant="outline"
              >
                Clear all filters
              </Button>
            )}
          </Card>
        )}

        {/* Users Grid */}
        {!isLoading && filteredUsers.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredUsers.map((user) => (
              <Card
                key={user.id}
                className="p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-3">
                  <UserAvatar
                    user={user}
                    size="lg"
                    clickable={false}
                  />
                  <div className="flex-1 min-w-0">
                    <Link
                      href={`/users/${user.username}`}
                      className="hover:underline block"
                    >
                      <Typography
                        variant="h6"
                        className="text-gray-900 font-medium truncate"
                      >
                        {user.username}
                      </Typography>
                    </Link>
                    <Typography
                      variant="p"
                      color="muted"
                      size="sm"
                      className="truncate"
                    >
                      {user.first_name} {user.last_name}
                    </Typography>
                    <div className="flex items-center gap-2 mt-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          user.role === "teacher"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {user.role === "teacher" ? "👨‍🏫 Teacher" : "👨‍🎓 Student"}
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
