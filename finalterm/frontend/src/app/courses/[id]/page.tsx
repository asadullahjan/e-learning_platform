import api from "@/services/api";
import { Course } from "@/lib/types";
import { getServerUser } from "@/lib/auth";
import CourseHeader from "./components/course-header";
import CourseContent from "./components/course-content";

export default async function CoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await api.get<Course>(`/courses/${id}`);
  const course = data.data;
  const user = await getServerUser();

  const isTeacher = user?.role === "teacher";
  const isCourseOwner = user?.id === course.teacher.id;

  return (
    <div className="container mx-auto py-8">
      <CourseHeader
        course={course}
        isTeacher={isTeacher}
        isCourseOwner={isCourseOwner}
      />

      <CourseContent course={course} />
    </div>
  );
}
