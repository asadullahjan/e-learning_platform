"use client";

import { useState, useEffect } from "react";
import { Course, ListResponse } from "@/lib/types";
import { courseService } from "@/services/courseService";
import CourseCard from "../components/course-card";
import Typography from "@/components/ui/Typography";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";
import { Loader2, BookOpen } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function MyCoursesClient() {
  const { user } = useAuthStore();
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async (page?: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const params: any = { teacher: user?.id };
      if (page) {
        params.page = page;
      }

      const response = await courseService.getCourses(params);
      const newCourses = response.results;

      if (page) {
        // Append to existing courses for load more
        setCourses((prev) => [...prev, ...newCourses]);
      } else {
        // Replace courses for initial load
        setCourses(newCourses);
      }

      setNextPage(response.next || null);
      setHasMore(!!response.next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load courses");
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
        await fetchCourses(pageNumber);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load more courses");
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
            <div className="h-32 bg-gray-200 rounded-lg"></div>
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
        <Button onClick={() => fetchCourses()}>Try Again</Button>
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <Typography
          variant="h4"
          color="muted"
          className="mb-2"
        >
          No courses created yet
        </Typography>
        <Typography
          variant="p"
          color="muted"
          size="sm"
        >
          Create your first course to get started
        </Typography>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Course Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <Typography
              variant="h3"
              className="text-blue-600"
            >
              {courses.length}
            </Typography>
            <Typography
              variant="span"
              color="muted"
              size="sm"
            >
              Total Courses
            </Typography>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <Typography
              variant="h3"
              className="text-green-600"
            >
              {courses.filter((c) => c.published_at).length}
            </Typography>
            <Typography
              variant="span"
              color="muted"
              size="sm"
            >
              Published
            </Typography>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <Typography
              variant="h3"
              className="text-yellow-600"
            >
              {courses.filter((c) => !c.published_at).length}
            </Typography>
            <Typography
              variant="span"
              color="muted"
              size="sm"
            >
              Drafts
            </Typography>
          </CardHeader>
        </Card>
      </div>

      {/* Course List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {courses.map((course) => (
          <CourseCard
            key={course.id}
            course={course}
          />
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
