import { Course, ListResponse } from "@/lib/types";
import { courseService } from "@/services/courseService";
import CourseCard from "./components/course-card";
import Typography from "@/components/ui/Typography";
import Filter from "./components/filter";

export default async function CoursesPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const coursesData = (await courseService.server.getCourses(searchParams)) as ListResponse<Course>;

  return (
    <div className="flex flex-col gap-4">
      <Filter />
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
