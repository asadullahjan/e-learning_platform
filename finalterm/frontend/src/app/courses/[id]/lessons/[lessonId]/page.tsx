import { notFound } from "next/navigation";
import { lessonService } from "@/services/lessonService";
import { courseService } from "@/services/courseService";
import { LessonDetail } from "../../components/lesson-detail";
import { LessonSidebar } from "../../components/lesson-sidebar";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

interface LessonPageProps {
  params: {
    id: string;
    lessonId: string;
  };
}

export default async function LessonPage({ params }: LessonPageProps) {
  const [course, lesson, lessonsResponse] = await Promise.all([
    courseService.server.getCourse(params.id),
    lessonService.server.getLesson(params.id, params.lessonId),
    lessonService.server.getCourseLessons(params.id),
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
          <Link href={`/courses/${params.id}?tab=content`}>
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
            courseId={params.id}
            currentLessonId={params.lessonId}
          />
        </div>

        {/* Lesson Content - Takes 3/4 of the space on desktop, full width on mobile */}
        <div className="lg:col-span-3 order-1 lg:order-2">
          <LessonDetail 
            lesson={lesson} 
            courseId={params.id}
            isTeacher={true}
          />
        </div>
      </div>
    </div>
  );
}
