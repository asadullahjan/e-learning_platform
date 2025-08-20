"use client";

import { useEffect, useState } from "react";
import { enrollmentService, StudentEnrollment } from "@/services/enrollmentService";
import Typography from "@/components/ui/Typography";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { CardHeader } from "@/components/ui/card";

export default function EnrolledCourses() {
  const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnrollments = async () => {
      try {
        setIsLoading(true);
        const data = await enrollmentService.getUserEnrollments();
        setEnrollments(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load enrollments");
      } finally {
        setIsLoading(false);
      }
    };

    fetchEnrollments();
  }, []);

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

  if (enrollments.length === 0) {
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
        <Typography
          variant="h4"
          className="text-gray-900 "
        >
          My Courses
        </Typography>
      </CardHeader>

      {enrollments.map((enrollment) => (
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
          <Typography
            variant="span"
            color="muted"
            size="xs"
            className="block mt-2"
          >
            by {enrollment.course.teacher.username}
          </Typography>
        </Link>
      ))}
    </Card>
  );
}
