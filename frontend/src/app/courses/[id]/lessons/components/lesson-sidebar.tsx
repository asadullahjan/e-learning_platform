import { Card } from "@/components/ui/card";
import Typography from "@/components/ui/Typography";
import { CourseLesson } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import Link from "next/link";
import { BookOpen, FileText } from "lucide-react";

interface LessonSidebarProps {
  lessons: CourseLesson[];
  courseId: number;
  currentLessonId?: number;
}

export function LessonSidebar({ lessons, courseId, currentLessonId }: LessonSidebarProps) {
  if (lessons.length === 0) {
    return (
      <Card className="p-4">
        <div className="text-center py-4">
          <BookOpen className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <Typography
            variant="p"
            color="muted"
            size="sm"
          >
            No lessons available yet
          </Typography>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <div className="mb-4">
        <Typography
          variant="h4"
          className="flex items-center gap-2"
        >
          <BookOpen className="w-5 h-5" />
          Course Lessons
        </Typography>
        <Typography
          variant="p"
          color="muted"
          size="sm"
        >
          {lessons.length} lesson{lessons.length !== 1 ? "s" : ""}
        </Typography>
      </div>

      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {lessons.map((lesson) => {
          const isActive = lesson.id === currentLessonId;
          const isPublished = !!lesson.published_at;

          return (
            <Link
              key={lesson.id}
              href={`/courses/${courseId}/lessons/${lesson.id}`}
              className={`block transition-colors ${
                isActive ? "bg-blue-50 border-l-4 border-blue-500" : "hover:bg-gray-50"
              }`}
            >
              <div className={`p-3 rounded-lg ${isActive ? "bg-blue-50" : ""}`}>
                <div className="flex items-start justify-between mb-2">
                  <Typography
                    variant="p"
                    className={`font-medium line-clamp-2 ${
                      isActive ? "text-blue-700" : "text-gray-900"
                    }`}
                  >
                    {lesson.title}
                  </Typography>
                  {!isPublished && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 ml-2 flex-shrink-0">
                      Draft
                    </span>
                  )}
                </div>

                <Typography
                  variant="span"
                  color="muted"
                  size="sm"
                  className="line-clamp-2 block mb-2"
                >
                  {lesson.description}
                </Typography>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{formatDate(lesson.created_at)}</span>
                  {lesson.file && (
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      File
                    </span>
                  )}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </Card>
  );
}
