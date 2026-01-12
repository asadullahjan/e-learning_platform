"use client";

import Typography from "@/components/ui/Typography";
import MyCourses from "./components/my-courses";
import StatusList, { StatusListRef } from "./components/status-list";
import CreateStatusButton from "./components/create-status-button";
import SearchUsersDialog from "@/components/ui/search-users-dialog";
import { useRef } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/hooks/use-toast";
import { chatService } from "@/services/chatService";
import { User } from "@/services/userService";
import { Button } from "@/components/ui/button";
import { Users, MessageCircle, Plus } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import CourseFormDialog from "../courses/components/course-form-dialog";

export default function HomePage() {
  const statusListRef = useRef<StatusListRef>(null);
  const router = useRouter();
  const { toast } = useToast();
  const { user } = useAuthStore();

  const handleStatusCreated = () => {
    if (statusListRef.current) {
      statusListRef.current.refresh();
    }
  };

  const handleStartChat = async (user: User) => {
    try {
      const response = await chatService.findOrCreateDirectChat(user.id);
      toast({ title: "Success", description: `Navigating to chat with ${user.username}` });
      router.push(`/chats/${response.id}`);
    } catch (error) {
      console.error("Failed to start chat:", error);
      toast({
        title: "Error",
        description: "Failed to start chat. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen ">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Sidebar - Enrolled Courses */}
        <div className="lg:col-span-1">
          <div className="sticky top-6 space-y-6">
            {/* Create Course Button for Teachers */}
            {user?.role === "teacher" && (
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <Typography
                  variant="h3"
                  className="text-gray-900 mb-3"
                >
                  Course Management
                </Typography>
                <Typography
                  variant="p"
                  color="muted"
                  className="mb-4"
                >
                  Create and manage your courses
                </Typography>
                <div className="space-y-2">
                  <CourseFormDialog
                    mode="create"
                    width="full"
                  />
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => router.push("/courses")}
                  >
                    Manage All Courses
                  </Button>
                </div>
              </div>
            )}

            <MyCourses />

            {/* Browse Courses Button for Students */}
            {user?.role === "student" && (
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <Typography
                  variant="h3"
                  className="text-gray-900 mb-3"
                >
                  Discover Courses
                </Typography>
                <Typography
                  variant="p"
                  color="muted"
                  className="mb-4"
                >
                  Find new courses to enroll in
                </Typography>
                <div className="space-y-2">
                  <Button
                    className="w-full"
                    onClick={() => router.push("/courses")}
                  >
                    Browse All Courses
                  </Button>
                </div>
              </div>
            )}

            {/* Search Users Section */}
            <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
              <Typography
                variant="h3"
                className="text-gray-900 mb-3"
              >
                Find People
              </Typography>
              <Typography
                variant="p"
                color="muted"
                className="mb-4"
              >
                Search for other users to connect with
              </Typography>
              <SearchUsersDialog
                customActionButton={(user, closeDialog) => (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleStartChat(user)}
                    className="px-2 py-1 h-8"
                  >
                    <MessageCircle className="w-3 h-3 mr-1" />
                    Chat
                  </Button>
                )}
                trigger={
                  <Button className="w-full">
                    <Users className="w-4 h-4 mr-2" />
                    Search Users
                  </Button>
                }
              />
            </div>
          </div>
        </div>

        {/* Main Content - Status Updates */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <div className="mb-6">
              <Typography
                variant="h2"
                className="text-gray-900 mb-2"
              >
                Community Updates
              </Typography>
              <Typography
                variant="p"
                color="muted"
              >
                See what's happening in your learning community
              </Typography>
            </div>
            <CreateStatusButton onStatusCreated={handleStatusCreated} />
            <StatusList ref={statusListRef} />
          </div>
        </div>
      </div>
    </div>
  );
}
