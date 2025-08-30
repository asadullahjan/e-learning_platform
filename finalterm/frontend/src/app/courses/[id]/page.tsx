import { courseService } from "@/services/courseService";
import { Course } from "@/lib/types";
import { getServerUser } from "@/lib/auth";
import CourseHeader from "./components/course-header";
import CourseTabs from "./components/course-tabs";

export default async function CoursePage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ tab?: string }>;
}) {
  const { id } = await params;
  const { tab } = await searchParams;
  const course: Course = await courseService.server.getCourse(id);
  const user = await getServerUser();
  console.log(course);
  const isTeacher = user?.role === "teacher";
  const isCourseOwner = user?.id === course.teacher.id;
  const isEnrolled = course.is_enrolled;

  return (
    <div className="container mx-auto py-8">
      <CourseHeader
        course={course}
        isTeacher={isTeacher}
        isCourseOwner={isCourseOwner}
      />

      <CourseTabs
        course={course}
        isTeacher={isTeacher}
        isCourseOwner={isCourseOwner}
        isEnrolled={isEnrolled}
        defaultTab={tab}
      />
    </div>
  );
}
