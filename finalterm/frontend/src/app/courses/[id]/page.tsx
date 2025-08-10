import { courseService } from "@/services/courseService";
import { Course } from "@/lib/types";
import { getServerUser } from "@/lib/auth";
import CourseHeader from "./components/course-header";
import CourseTabs from "./components/course-tabs";

export default async function CoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const course: Course = await courseService.server.getCourse(id);
  const user = await getServerUser();
  
  const isTeacher = user?.role === "teacher";
  const isCourseOwner = user?.id === course.teacher.id;
  console.log(course);
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
      />
    </div>
  );
}
