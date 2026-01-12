"use client";
import { useState, useEffect } from "react";
import { enrollmentService, TeacherEnrollment } from "@/services/enrollmentService";
import { chatService } from "@/services/chatService";
import { Card, CardContent } from "@/components/ui/card";
import Avatar from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";
import Typography from "@/components/ui/Typography";
import { showToast } from "@/lib/toast";
import { useRouter } from "next/navigation";
import { toast } from "@/components/hooks/use-toast";

interface CourseEnrollmentsProps {
  courseId: number;
  isTeacher: boolean;
  enrollments: TeacherEnrollment[];
}

const CourseEnrollments = ({
  courseId,
  isTeacher,
  enrollments: initialEnrollments,
}: CourseEnrollmentsProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "active" | "inactive">("all");
  const [loadingStates, setLoadingStates] = useState<{ [key: string]: boolean }>({});
  const [enrollments, setEnrollments] = useState<TeacherEnrollment[]>(initialEnrollments);
  const [isLoading, setIsLoading] = useState(false);
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");
  const router = useRouter();

  // Debounce search query to avoid too many API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch filtered enrollments when filters change
  useEffect(() => {
    const fetchFilteredEnrollments = async () => {
      setIsLoading(true);
      try {
        const filteredEnrollments = await enrollmentService.getCourseEnrollments(courseId, {
          search: debouncedSearchQuery.trim() || undefined,
          status: filterStatus,
        });
        setEnrollments(filteredEnrollments);
      } catch (error) {
        console.error("Failed to fetch filtered enrollments:", error);
        showToast.error("Failed to load enrollments");
      } finally {
        setIsLoading(false);
      }
    };

    fetchFilteredEnrollments();
  }, [courseId, debouncedSearchQuery, filterStatus]);

  const handleDeactivateEnrollment = async (enrollmentId: number) => {
    try {
      await enrollmentService.deactivateEnrollment(enrollmentId);
      showToast.success("Student removed successfully");

      // Refresh the enrollments after removal
      const updatedEnrollments = await enrollmentService.getCourseEnrollments(courseId, {
        search: debouncedSearchQuery.trim() || undefined,
        status: filterStatus,
      });
      setEnrollments(updatedEnrollments);
    } catch (error) {
      console.error("Failed to remove student:", error);
      showToast.error("Failed to remove student");
    }
  };

  const handleMessageUser = async (username: string, userId: number) => {
    if (loadingStates[username]) return;

    setLoadingStates((prev) => ({ ...prev, [username]: true }));
    try {
      const response = await chatService.findOrCreateDirectChat(userId);
      toast({ title: "Success", description: `Navigating to chat with ${username}` });

      // Navigate to the chat
      router.push(`/chats/${response.id}`);
    } catch (error: any) {
      console.error("Failed to open chat:", error);
      const errorMessage = error.response?.data?.detail || "Failed to open chat";
      showToast.error(errorMessage);
    } finally {
      setLoadingStates((prev) => ({ ...prev, [username]: false }));
    }
  };

  const handleViewProfile = (username: string) => {
    router.push(`/users/${username}`);
  };

  // Calculate counts from filtered results
  const activeEnrollments = enrollments.filter((e) => e.is_active);
  const inactiveEnrollments = enrollments.filter((e) => !e.is_active);

  if (!initialEnrollments || initialEnrollments.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-gray-500">
          <Typography variant="p">No students enrolled yet.</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <Typography
              variant="p"
              className="font-medium text-gray-900"
            >
              Total Students
            </Typography>
            <Typography
              variant="h2"
              size="lg"
              className="text-blue-600"
            >
              {initialEnrollments.length}
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <Typography
              variant="h2"
              size="lg"
              className="text-green-600"
            >
              {initialEnrollments.filter((e) => e.is_active).length}
            </Typography>
            <Typography
              variant="p"
              className="font-medium text-gray-900"
            >
              Active Students
            </Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <Typography
              variant="h2"
              size="lg"
              className="text-gray-600"
            >
              {initialEnrollments.filter((e) => !e.is_active).length}
            </Typography>
            <Typography
              variant="p"
              className="font-medium text-gray-900"
            >
              Inactive Students
            </Typography>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search students by name or email..."
                className="w-full"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={filterStatus === "all" ? "default" : "outline"}
                size="sm"
                className="transition-all duration-200"
                onClick={() => setFilterStatus("all")}
                disabled={isLoading}
              >
                All Students
              </Button>
              <Button
                variant={filterStatus === "active" ? "default" : "outline"}
                size="sm"
                className="transition-all duration-200"
                onClick={() => setFilterStatus("active")}
                disabled={isLoading}
              >
                Active Only
              </Button>
              <Button
                variant={filterStatus === "inactive" ? "default" : "outline"}
                size="sm"
                className="transition-all duration-200"
                onClick={() => setFilterStatus("inactive")}
                disabled={isLoading}
              >
                Inactive Only
              </Button>
            </div>
          </div>
          {(searchQuery || filterStatus !== "all") && (
            <div className="mt-2 flex items-center gap-2">
              <Typography
                variant="p"
                size="xs"
                className="text-gray-500"
              >
                Showing {enrollments.length} of {initialEnrollments.length} students
              </Typography>
              {isLoading && (
                <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Active Students */}
      {activeEnrollments.length > 0 && (
        <div>
          <Typography
            variant="h3"
            size="md"
            className="mb-4"
          >
            Active Students ({activeEnrollments.length})
          </Typography>
          <div className="grid gap-4">
            {activeEnrollments.map((enrollment) => (
              <Card key={enrollment.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Avatar
                        src={enrollment.user.profile_picture}
                        alt={enrollment.user.username}
                        size="md"
                        fallback={
                          <div className="h-full w-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium rounded-full">
                            {enrollment.user.username.charAt(0).toUpperCase()}
                          </div>
                        }
                      />

                      <div>
                        <Typography
                          variant="h4"
                          size="sm"
                          className="text-gray-900"
                        >
                          {enrollment.user.username}
                        </Typography>
                        <Typography
                          variant="p"
                          size="sm"
                          className="text-gray-500"
                        >
                          {enrollment.user.email}
                        </Typography>
                        <Typography
                          variant="p"
                          size="xs"
                          className="text-gray-400"
                        >
                          Role: {enrollment.user.role}
                        </Typography>
                      </div>
                    </div>

                    <div className="text-right space-y-2">
                      <Typography
                        variant="span"
                        size="xs"
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                      >
                        Active
                      </Typography>
                      <Typography
                        variant="p"
                        size="xs"
                        className="text-gray-500"
                      >
                        Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </Typography>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                          onClick={() => handleViewProfile(enrollment.user.username)}
                        >
                          View Profile
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                          onClick={() =>
                            handleMessageUser(enrollment.user.username, enrollment.user.id)
                          }
                          disabled={loadingStates[enrollment.user.username]}
                        >
                          {loadingStates[enrollment.user.username] ? "Opening..." : "Message"}
                        </Button>
                        {isTeacher && (
                          <Button
                            size="sm"
                            variant="destructive"
                            className="transition-all duration-200 hover:bg-red-700"
                            onClick={() => handleDeactivateEnrollment(enrollment.id)}
                          >
                            Delete
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Inactive Students (if any) */}
      {inactiveEnrollments.length > 0 && (
        <div>
          <Typography
            variant="h3"
            size="md"
            className="mb-4"
          >
            Inactive Students ({inactiveEnrollments.length})
          </Typography>
          <div className="grid gap-4">
            {inactiveEnrollments.map((enrollment) => (
              <Card
                key={enrollment.id}
                className="opacity-75"
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Avatar
                        src={enrollment.user.profile_picture}
                        alt={enrollment.user.username}
                        size="md"
                        fallback={
                          <div className="h-full w-full bg-gray-400 text-white flex items-center justify-center text-sm font-medium rounded-full">
                            {enrollment.user.username.charAt(0).toUpperCase()}
                          </div>
                        }
                      />

                      <div>
                        <Typography
                          variant="h4"
                          size="sm"
                          className="text-gray-700"
                        >
                          {enrollment.user.username}
                        </Typography>
                        <Typography
                          variant="p"
                          size="sm"
                          className="text-gray-500"
                        >
                          {enrollment.user.email}
                        </Typography>
                        <Typography
                          variant="p"
                          size="xs"
                          className="text-gray-400"
                        >
                          Role: {enrollment.user.role}
                        </Typography>
                      </div>
                    </div>

                    <div className="text-right space-y-2">
                      <Typography
                        variant="span"
                        size="xs"
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                      >
                        Inactive
                      </Typography>
                      <Typography
                        variant="p"
                        size="xs"
                        className="text-gray-500"
                      >
                        Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </Typography>
                      {enrollment.unenrolled_at && (
                        <Typography
                          variant="p"
                          size="xs"
                          className="text-gray-500"
                        >
                          Unenrolled: {new Date(enrollment.unenrolled_at).toLocaleDateString()}
                        </Typography>
                      )}
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                          onClick={() => handleViewProfile(enrollment.user.username)}
                        >
                          View Profile
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                          onClick={() =>
                            handleMessageUser(enrollment.user.username, enrollment.user.id)
                          }
                          disabled={loadingStates[enrollment.user.username]}
                        >
                          {loadingStates[enrollment.user.username] ? "Opening..." : "Message"}
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* No results message */}
      {enrollments.length === 0 && (searchQuery || filterStatus !== "all") && !isLoading && (
        <Card>
          <CardContent className="p-6 text-center text-gray-500">
            <Typography variant="p">No students found matching your search criteria.</Typography>
          </CardContent>
        </Card>
      )}

      {/* Loading state */}
      {isLoading && (
        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-2"></div>
            <Typography
              variant="p"
              size="sm"
              className="text-gray-500"
            >
              Loading enrollments...
            </Typography>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CourseEnrollments;
