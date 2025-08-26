import { Course, ListResponse } from "@/lib/types";
import { courseService } from "@/services/courseService";
import CourseCard from "./components/course-card";
import Typography from "@/components/ui/Typography";
import Filter from "./components/filter";
import CourseFormDialog from "./components/course-form-dialog";
import { getServerUser } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { BookOpen, Plus, UserCheck } from "lucide-react";

export default async function CoursesPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const coursesData = (await courseService.server.getCourses(searchParams)) as ListResponse<Course>;
  const user = await getServerUser();
  
  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4 w-full">
        <Filter />
        {user?.role === "teacher" && <CourseFormDialog mode="create" />}
      </div>

      {/* User-specific navigation buttons */}
      {user && (
        <div className="flex gap-3 mb-4">
          {user.role === "teacher" && (
            <Link href="/courses/my-courses">
              <Button variant="outline" className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                My Created Courses
              </Button>
            </Link>
          )}
          {user.role === "student" && (
            <Link href="/courses/enrolled">
              <Button variant="outline" className="flex items-center gap-2">
                <UserCheck className="w-4 h-4" />
                My Enrolled Courses
              </Button>
            </Link>
          )}
        </div>
      )}

      <Typography
        variant="h1"
        size="lg"
        className="sr-only"
      >
        Courses
      </Typography>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {coursesData.results.map((course) => (
          <CourseCard
            key={course.id}
            course={course}
          />
        ))}
      </div>
    </div>
  );
}
