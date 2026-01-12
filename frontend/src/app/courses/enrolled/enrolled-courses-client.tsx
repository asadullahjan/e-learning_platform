"use client";

import { useState, useEffect } from "react";
import { enrollmentService, StudentEnrollment } from "@/services/enrollmentService";
import Typography from "@/components/ui/Typography";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";
import { Loader2, BookOpen, User, Calendar } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import Link from "next/link";

export default function EnrolledCoursesClient() {
  const { user } = useAuthStore();
  const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetchEnrollments();
  }, []);

  const fetchEnrollments = async (page?: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const params: any = {};
      if (page) {
        params.page = page;
      }

      const response = await enrollmentService.getUserEnrollments(params);
      const newEnrollments = response.results as StudentEnrollment[];

      if (page) {
        // Append to existing enrollments for load more
        setEnrollments((prev) => [...prev, ...newEnrollments]);
      } else {
        // Replace enrollments for initial load
        setEnrollments(newEnrollments);
      }

      // Handle both paginated and non-paginated responses
      if (response.next) {
        setNextPage(response.next);
        setHasMore(true);
      } else {
        setNextPage(null);
        setHasMore(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load enrollments");
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = async () => {
    if (!nextPage || isLoadingMore) return;

    try {
      setIsLoadingMore(true);
      const pageNumber = new URLSearchParams(nextPage.split("?")[1]).get("page");
      if (pageNumber) {
        await fetchEnrollments(pageNumber);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load more enrollments");
    } finally {
      setIsLoadingMore(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="animate-pulse"
          >
            <div className="h-24 bg-gray-200 rounded-lg"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <Typography
          variant="p"
          color="error"
          className="mb-4"
        >
          {error}
        </Typography>
        <Button onClick={() => fetchEnrollments()}>Try Again</Button>
      </div>
    );
  }

  if (enrollments.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <Typography
          variant="h4"
          color="muted"
          className="mb-2"
        >
          Not enrolled in any courses yet
        </Typography>
        <Typography
          variant="p"
          color="muted"
          size="sm"
          className="mb-4"
        >
          Browse available courses and start learning
        </Typography>
        <Link href="/courses">
          <Button>Browse Courses</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enrollment Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <Typography
              variant="h3"
              className="text-blue-600"
            >
              {enrollments.length}
            </Typography>
            <Typography
              variant="span"
              color="muted"
              size="sm"
            >
              Total Enrollments
            </Typography>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <Typography
              variant="h3"
              className="text-green-600"
            >
              {enrollments.filter((e) => e.is_active).length}
            </Typography>
            <Typography
              variant="span"
              color="muted"
              size="sm"
            >
              Active Enrollments
            </Typography>
          </CardHeader>
        </Card>
      </div>

      {/* Enrolled Courses List */}
      <div className="space-y-4">
        {enrollments.map((enrollment) => (
          <Card
            key={enrollment.id}
            className="hover:shadow-md transition-shadow"
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <Typography
                    variant="h4"
                    size="lg"
                    className="text-gray-900 mb-1"
                  >
                    {enrollment.course.title}
                  </Typography>
                  <Typography
                    variant="p"
                    color="muted"
                    size="sm"
                    className="line-clamp-2"
                  >
                    {enrollment.course.description}
                  </Typography>
                </div>
                <span
                  className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    enrollment.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                  }`}
                >
                  {enrollment.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <User className="w-4 h-4" />
                    <Link href={`/users/${enrollment.course.teacher.username}`}>
                      <Typography
                        variant="span"
                        size="sm"
                        className="hover:text-primary transition-colors cursor-pointer"
                      >
                        by {enrollment.course.teacher.username}
                      </Typography>
                    </Link>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <Typography
                      variant="span"
                      size="sm"
                    >
                      Enrolled {new Date(enrollment.enrolled_at).toLocaleDateString()}
                    </Typography>
                  </div>
                </div>
                <Link href={`/courses/${enrollment.course.id}`}>
                  <Button
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <BookOpen className="w-4 h-4" />
                    View Course
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Load More Button */}
      {hasMore && (
        <div className="text-center pt-4">
          <Button
            onClick={loadMore}
            disabled={isLoadingMore}
            variant="outline"
            className="min-w-[120px]"
          >
            {isLoadingMore ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              "Load More"
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
