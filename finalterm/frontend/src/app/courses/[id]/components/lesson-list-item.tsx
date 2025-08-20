import Link from "next/link";
import { Card } from "@/components/ui/card";
import Typography from "@/components/ui/Typography";
import { CourseLesson } from "@/lib/types";
import { formatDate } from "@/lib/utils";

interface LessonListItemProps {
  lesson: CourseLesson;
  courseId: string;
}

export function LessonListItem({ lesson, courseId }: LessonListItemProps) {
  const isPublished = !!lesson.published_at;

  return (
    <Link href={`/courses/${courseId}/lessons/${lesson.id}`}>
      <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer">
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <Typography variant="h4" className="text-left">
              {lesson.title}
            </Typography>
                      {!isPublished && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Draft
            </span>
          )}
          </div>
          
          <Typography variant="p" color="muted" className="text-left line-clamp-2">
            {lesson.description}
          </Typography>
          
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <span>Created: {formatDate(lesson.created_at)}</span>
              {isPublished && (
                <span>• Published: {formatDate(lesson.published_at!)}</span>
              )}
            </div>
            {lesson.file && (
              <span className="flex items-center gap-1">
                📎 {lesson.file.original_name}
              </span>
            )}
          </div>
        </div>
      </Card>
    </Link>
  );
}
