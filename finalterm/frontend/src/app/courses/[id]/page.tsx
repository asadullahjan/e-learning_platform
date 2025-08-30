import { courseService } from "@/services/courseService";
import { Course } from "@/lib/types";
import { getServerUser } from "@/lib/auth";
import CourseHeader from "./components/course-header";
import CourseTabs from "./components/course-tabs";
import { restrictionService } from "@/services/restrictionService";
import Typography from "@/components/ui/Typography";
import { Card } from "@/components/ui/card";

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
  const isRestricted = await restrictionService.server.checkStudentRestriction(course.id);
  const isTeacher = user?.role === "teacher";
  const isCourseOwner = user?.id === course.teacher.id;
  const isEnrolled = course.is_enrolled;

  return (
    <div className="container mx-auto py-8">
      {isRestricted.is_restricted && (
        <Card className="bg-error-light p-4 mb-4">
          <Typography
            variant="p"
            color="error"
          >
            "You are restricted from accessing this course content"
          </Typography>
          <Typography
            variant="p"
            color="error"
          >
            {isRestricted.reason}
          </Typography>
        </Card>
      )}
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
