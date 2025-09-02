import { notFound } from "next/navigation";
import { lessonService } from "@/services/lessonService";
import { courseService } from "@/services/courseService";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { getServerUser } from "@/lib/auth";
import { LessonSidebar } from "../components/lesson-sidebar";
import { LessonDetail } from "../components/lesson-detail";

interface LessonPageProps {
  params: Promise<{
    id: string;
    lessonId: string;
  }>;
}

export default async function LessonPage({ params }: LessonPageProps) {
  const { id, lessonId } = await params;
  const idNumber = parseInt(id);
  const lessonIdNumber = parseInt(lessonId);
  const user = await getServerUser();
  const [course, lesson, lessonsResponse] = await Promise.all([
    courseService.server.getCourse(idNumber),
    lessonService.server.getLesson(idNumber, lessonIdNumber),
    lessonService.server.getCourseLessons(idNumber),
  ]);

  if (!course || !lesson) {
    notFound();
  }

  return (
    <div className="container mx-auto py-8">
      {/* Back Navigation */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          asChild
        >
          <Link
            href={`/courses/${idNumber}?tab=${user?.role === "teacher" ? "lessons" : "content"}`}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Course
          </Link>
        </Button>
      </div>

      {/* Main Content with Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 lg:gap-8">
        {/* Lesson Sidebar - Takes 1/4 of the space on desktop, full width on mobile */}
        <div className="lg:col-span-1 order-2 lg:order-1">
          <LessonSidebar
            lessons={lessonsResponse.results}
            courseId={idNumber}
            currentLessonId={lessonIdNumber}
          />
        </div>

        {/* Lesson Content - Takes 3/4 of the space on desktop, full width on mobile */}
        <div className="lg:col-span-3 order-1 lg:order-2">
          <LessonDetail
            lesson={lesson}
            courseId={idNumber}
            isTeacher={course.teacher.username === user?.username}
          />
        </div>
      </div>
    </div>
  );
}
