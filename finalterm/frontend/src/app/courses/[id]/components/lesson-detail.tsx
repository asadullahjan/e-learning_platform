"use client";
import { Card } from "@/components/ui/card";
import Typography from "@/components/ui/Typography";
import { CourseLesson } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Download, Eye, EyeOff } from "lucide-react";
import { LessonFormDialog } from "./lesson-form-dialog";
import { lessonService } from "@/services/lessonService";
import { useToast } from "@/components/hooks/use-toast";
import { useState } from "react";
import ConfirmDialog from "@/components/ui/confirm-dialog";

interface LessonDetailProps {
  lesson: CourseLesson;
  courseId: string;
  isTeacher?: boolean;
}

export function LessonDetail({ lesson, courseId, isTeacher = false }: LessonDetailProps) {
  const [isPublished, setIsPublished] = useState(!!lesson.published_at);
  const [isLoading, setIsLoading] = useState(false);
  const [isPublishConfirmOpen, setIsPublishConfirmOpen] = useState(false);
  const [isUnpublishConfirmOpen, setIsUnpublishConfirmOpen] = useState(false);
  const { toast } = useToast();

  const handleFileDownload = () => {
    if (lesson.file?.download_url) {
      window.open(lesson.file.download_url, "_blank");
    }
  };

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
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to unpublish lesson",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Main Lesson Card */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* Header with Title, Description, and Status */}
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <Typography
                variant="h1"
                className="text-left"
              >
                {lesson.title}
              </Typography>
              <Typography
                variant="p"
                color="muted"
                className="text-left"
              >
                {lesson.description}
              </Typography>
            </div>

            <div className="flex items-center gap-3">
              {!isPublished && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
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

                  {/* Edit Button */}
                  <LessonFormDialog
                    courseId={courseId}
                    lesson={lesson}
                    mode="edit"
                  />
                </>
              )}
            </div>
          </div>

          {/* Lesson Content */}
          {lesson.content && (
            <div className="pt-4 border-t border-gray-200">
              <Typography
                variant="p"
                className="whitespace-pre-wrap"
              >
                {lesson.content}
              </Typography>
            </div>
          )}

          {/* Lesson Metadata */}
          <div className="flex items-center gap-4 text-sm text-gray-500 pt-4 border-t border-gray-200">
            {isPublished ? (
              <span>Published: {formatDate(lesson.published_at!)}</span>
            ) : (
              <>
                <span>Created: {formatDate(lesson.created_at)}</span>
                {lesson.updated_at !== lesson.created_at && (
                  <span>Updated: {formatDate(lesson.updated_at)}</span>
                )}
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Lesson File */}
      {lesson.file && (
        <Card className="p-6">
          <Typography
            variant="h3"
            className="mb-4"
          >
            Attached File
          </Typography>

          <div className="space-y-4">
            {/* File Info */}
            <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                📎
              </div>
              <div>
                <Typography
                  variant="p"
                  className="font-medium"
                >
                  {lesson.file.original_name}
                </Typography>
                <Typography
                  variant="span"
                  color="muted"
                  className="text-sm"
                >
                  {lesson.file.is_previewable ? "Previewable" : "Download only"}
                </Typography>
              </div>

              <div className="ml-auto">
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleFileDownload}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>

            {/* File Preview */}
            {lesson.file.is_previewable && (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                  <Typography
                    variant="span"
                    size="sm"
                    className="font-medium"
                  >
                    Preview
                  </Typography>
                </div>
                <div className="p-4">
                  {lesson.file.original_name.toLowerCase().includes(".pdf") ? (
                    <iframe
                      src={`data:application/pdf;base64,${lesson.file.file_content}`}
                      className="w-full h-96 border-0"
                      title={`Preview of ${lesson.file.original_name}`}
                    />
                  ) : lesson.file.original_name
                      .toLowerCase()
                      .match(/\.(jpg|jpeg|png|gif|webp)$/i) ? (
                    <img
                      src={`data:image/jpeg;base64,${lesson.file.file_content}`}
                      alt={lesson.file.original_name}
                      className="max-w-full h-auto max-h-96 mx-auto"
                    />
                  ) : lesson.file.original_name.toLowerCase().match(/\.(txt|md|html)$/i) ? (
                    <iframe
                      src={`data:text/html;base64,${lesson.file.file_content}`}
                      className="w-full h-96 border-0"
                      title={`Preview of ${lesson.file.original_name}`}
                    />
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Typography
                        variant="p"
                        color="muted"
                      >
                        Preview not available for this file type
                      </Typography>
                      <Typography
                        variant="span"
                        size="sm"
                        color="muted"
                      >
                        Please download the file to view it
                      </Typography>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

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
