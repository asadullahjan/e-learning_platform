import Link from "next/link";
import { Card } from "@/components/ui/card";
import Typography from "@/components/ui/Typography";
import { CourseLesson } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Eye, EyeOff } from "lucide-react";
import { lessonService } from "@/services/lessonService";
import { useToast } from "@/components/hooks/use-toast";
import { useState } from "react";
import ConfirmDialog from "@/components/ui/confirm-dialog";

interface LessonListItemProps {
  lesson: CourseLesson;
  courseId: string;
  isTeacher?: boolean;
}

export function LessonListItem({ lesson, courseId, isTeacher = false }: LessonListItemProps) {
  const [isPublished, setIsPublished] = useState(!!lesson.published_at);
  const [isLoading, setIsLoading] = useState(false);
  const [isPublishConfirmOpen, setIsPublishConfirmOpen] = useState(false);
  const [isUnpublishConfirmOpen, setIsUnpublishConfirmOpen] = useState(false);
  const { toast } = useToast();

  const handlePublishLesson = async () => {
    try {
      setIsLoading(true);
      await lessonService.toggleLessonPublish(courseId, lesson.id, true);
      setIsPublished(true);
      toast({
        title: "Success",
        description: "Lesson published successfully",
      });
      setIsPublishConfirmOpen(false);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to publish lesson",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnpublishLesson = async () => {
    try {
      setIsLoading(true);
      await lessonService.toggleLessonPublish(courseId, lesson.id, false);
      setIsPublished(false);
      toast({
        title: "Success",
        description: "Lesson unpublished successfully",
      });
      setIsUnpublishConfirmOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-2">
      <Card className="p-4 hover:shadow-md transition-shadow">
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <Link href={`/courses/${courseId}/lessons/${lesson.id}`} className="flex-1">
              <Typography variant="h4" className="text-left hover:text-blue-600">
                {lesson.title}
              </Typography>
            </Link>
            
            <div className="flex items-center gap-2 ml-4">
              {!isPublished && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                  Draft
                </span>
              )}

              {isTeacher && (
                <>
                  {/* Publish/Unpublish Button */}
                  {isPublished ? (
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-orange-600 hover:text-orange-700 hover:bg-orange-50"
                      onClick={() => setIsUnpublishConfirmOpen(true)}
                      disabled={isLoading}
                    >
                      <EyeOff className="w-4 h-4 mr-1" />
                      {isLoading ? "Unpublishing..." : "Unpublish"}
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="default"
                      className="bg-green-600 hover:bg-green-700"
                      onClick={() => setIsPublishConfirmOpen(true)}
                      disabled={isLoading}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      {isLoading ? "Publishing..." : "Publish"}
                    </Button>
                  )}
                </>
              )}
            </div>
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

      {/* Confirm Dialogs */}
      <ConfirmDialog
        isOpen={isPublishConfirmOpen}
        onClose={() => setIsPublishConfirmOpen(false)}
        onConfirm={handlePublishLesson}
        title="Publish Lesson"
        description="Are you sure you want to publish this lesson? Students will be able to view it once published."
        confirmText="Publish"
        cancelText="Cancel"
        variant="info"
      />

      <ConfirmDialog
        isOpen={isUnpublishConfirmOpen}
        onClose={() => setIsUnpublishConfirmOpen(false)}
        onConfirm={handleUnpublishLesson}
        title="Unpublish Lesson"
        description="Are you sure you want to unpublish this lesson? Students will no longer be able to view it."
        confirmText="Unpublish"
        cancelText="Cancel"
        variant="warning"
      />
    </div>
  );
}
