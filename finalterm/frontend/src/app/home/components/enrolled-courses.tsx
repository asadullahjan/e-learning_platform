"use client";

import { useEffect, useState } from "react";
import { enrollmentService, StudentEnrollment } from "@/services/enrollmentService";
import { courseService } from "@/services/courseService";
import { useAuthStore } from "@/store/authStore";
import Typography from "@/components/ui/Typography";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { CardHeader } from "@/components/ui/card";
import { Course } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";

export default function EnrolledCourses() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
  const [teacherCourses, setTeacherCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);

        if (user?.role === "teacher") {
          // For teachers, fetch their created courses
          const courses = await courseService.getTeacherCourses(user.id.toString());
          setTeacherCourses(courses);
        } else {
          // For students, fetch their enrollments
          const data = await enrollmentService.getUserEnrollments();
          setEnrollments(data);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="animate-pulse"
          >
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <Typography
          variant="p"
          color="error"
          size="sm"
        >
          {error}
        </Typography>
      </div>
    );
  }

  if (user?.role === "teacher" && teacherCourses.length === 0) {
    return (
      <div className="text-center py-4">
        <Typography
          variant="p"
          color="muted"
          size="sm"
        >
          No courses created yet
        </Typography>
      </div>
    );
  }

  if (user?.role === "student" && enrollments.length === 0) {
    return (
      <div className="text-center py-4">
        <Typography
          variant="p"
          color="muted"
          size="sm"
        >
          Not enrolled in any courses yet
        </Typography>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader className="p-5 pb-0">
        <div className="flex items-center justify-between">
          <Typography
            variant="h4"
            className="text-gray-900 "
          >
            {user?.role === "teacher" ? "My Created Courses" : "My Enrolled Courses"}
          </Typography>
          {user?.role === "teacher" && teacherCourses.length > 0 && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => router.push("/courses")}
              className="text-xs"
            >
              <Plus className="w-3 h-3 mr-1" />
              Manage Courses
            </Button>
          )}
        </div>

        {/* Teacher Stats */}
        {user?.role === "teacher" && teacherCourses.length > 0 && (
          <div className="flex gap-4 mt-3 pt-3 border-t border-gray-100">
            <div className="text-center">
              <Typography
                variant="h5"
                className="text-blue-600"
              >
                {teacherCourses.length}
              </Typography>
              <Typography
                variant="span"
                size="xs"
                color="muted"
              >
                Total Courses
              </Typography>
            </div>
            <div className="text-center">
              <Typography
                variant="h5"
                className="text-green-600"
              >
                {teacherCourses.filter((c) => c.published_at).length}
              </Typography>
              <Typography
                variant="span"
                size="xs"
                color="muted"
              >
                Published
              </Typography>
            </div>
            <div className="text-center">
              <Typography
                variant="h5"
                className="text-green-600"
              >
                {teacherCourses.filter((c) => !c.published_at).length}
              </Typography>
              <Typography
                variant="span"
                size="xs"
                color="muted"
              >
                Drafts
              </Typography>
            </div>
          </div>
        )}

        {/* Student Stats */}
        {user?.role === "student" && enrollments.length > 0 && (
          <div className="flex gap-4 mt-3 pt-3 border-t border-gray-100">
            <div className="text-center">
              <Typography
                variant="h5"
                className="text-blue-600"
              >
                {enrollments.length}
              </Typography>
              <Typography
                variant="span"
                size="xs"
                color="muted"
              >
                Enrolled Courses
              </Typography>
            </div>
            <div className="text-center">
              <Typography
                variant="h5"
                className="text-green-600"
              >
                {enrollments.filter((e) => e.is_active).length}
              </Typography>
              <Typography
                variant="span"
                size="xs"
                color="muted"
              >
                Active
              </Typography>
            </div>
          </div>
        )}
      </CardHeader>

      {user?.role === "teacher"
        ? // Render teacher courses
          teacherCourses.map((course) => (
            <Link
              key={course.id}
              href={`/courses/${course.id}`}
              className="block p-5 hover:bg-gray-100 duration-300 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <Typography
                    variant="h6"
                    className="text-gray-900 font-medium mb-1"
                  >
                    {course.title}
                  </Typography>
                  <Typography
                    variant="p"
                    color="muted"
                    size="sm"
                    className="line-clamp-2"
                  >
                    {course.description}
                  </Typography>
                  <div className="flex items-center gap-2 mt-2">
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        course.published_at
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {course.published_at ? "Published" : "Draft"}
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))
        : // Render student enrollments
          enrollments.map((enrollment) => (
            <Link
              key={enrollment.id}
              href={`/courses/${enrollment.course.id}`}
              className="block p-5 hover:bg-gray-100 duration-300 transition-all"
            >
              <Typography
                variant="h6"
                className="text-gray-900 font-medium mb-1"
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
              <div className="flex items-center justify-between mt-2">
                <Link href={`/users/${enrollment.course.teacher.username}`}>
                  <Typography
                    variant="span"
                    color="muted"
                    size="xs"
                    className="hover:text-primary transition-colors cursor-pointer"
                  >
                    by {enrollment.course.teacher.username}
                  </Typography>
                </Link>
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Enrolled
                </span>
              </div>
            </Link>
          ))}
    </Card>
  );
}
