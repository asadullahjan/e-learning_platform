"use client";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogDescription,
  DialogContent,
  DialogTrigger,
  DialogTitle,
} from "@/components/ui/dialog";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { courseService } from "@/services/courseService";
import { enrollmentService } from "@/services/enrollmentService";
import { showToast } from "@/lib/toast";
import { Course } from "@/lib/types";
import CourseFormDialog from "../../components/course-form-dialog";
import ConfirmDialog from "@/components/ui/confirm-dialog";

interface CourseActionsProps {
  isTeacher: boolean;
  isCourseOwner: boolean;
  courseId: number;
  isEnrolled: boolean;
  course: Course;
}

const CourseActions = ({
  isTeacher,
  isCourseOwner,
  courseId,
  isEnrolled,
  course,
}: CourseActionsProps) => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isPublishConfirmOpen, setIsPublishConfirmOpen] = useState(false);
  const [isUnpublishConfirmOpen, setIsUnpublishConfirmOpen] = useState(false);
  const [isUnenrollConfirmOpen, setIsUnenrollConfirmOpen] = useState(false);
  const [isEnrollConfirmOpen, setIsEnrollConfirmOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleDeleteCourse = async () => {
    try {
      setIsLoading(true);
      await courseService.deleteCourse(courseId);
      setIsDeleteDialogOpen(false);
      router.push("/courses");
      showToast.success("Course deleted successfully");
    } catch (error) {
      console.error("Error deleting course:", error);
      showToast.error("Error deleting course");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublishCourse = async () => {
    try {
      setIsLoading(true);
      await courseService.publishCourse(courseId);
      router.refresh();
      showToast.success("Course published successfully");
      setIsPublishConfirmOpen(false);
    } catch (error) {
      showToast.error("Failed to publish course");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnpublishCourse = async () => {
    try {
      setIsLoading(true);
      await courseService.unpublishCourse(courseId);
      router.refresh();
      showToast.success("Course unpublished successfully");
      setIsUnpublishConfirmOpen(false);
    } catch (error) {
      showToast.error("Failed to unpublish course");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnrollCourse = async () => {
    try {
      setIsLoading(true);
      await enrollmentService.createEnrollment(courseId);
      router.refresh();
      showToast.success("Enrolled in course successfully");
      setIsEnrollConfirmOpen(false);
    } catch (error) {
      console.error("Error enrolling in course:", error);
      showToast.error("Error enrolling in course");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnenrollCourse = async () => {
    try {
      setIsLoading(true);
      await enrollmentService.deleteEnrollment(courseId);
      router.refresh();
      showToast.success("Unenrolled from course successfully");
      setIsUnenrollConfirmOpen(false);
    } catch (error) {
      console.error("Error unenrolling from course:", error);
      showToast.error("Error unenrolling from course");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex gap-3 transition-all duration-300">
      {isTeacher && isCourseOwner ? (
        <>
          {/* Publish/Unpublish Button */}
          {course.published_at ? (
            <Button
              size="md"
              variant="outline"
              className="px-6 transition-all duration-200 hover:bg-orange-50 hover:border-orange-300"
              onClick={() => setIsUnpublishConfirmOpen(true)}
              disabled={isLoading}
            >
              {isLoading ? "Unpublishing..." : "Unpublish Course"}
            </Button>
          ) : (
            <Button
              size="md"
              variant="default"
              className="px-6 transition-all duration-200 hover:bg-green-600"
              onClick={() => setIsPublishConfirmOpen(true)}
              disabled={isLoading}
            >
              {isLoading ? "Publishing..." : "Publish Course"}
            </Button>
          )}

          {/* Edit Course Button */}
          <CourseFormDialog
            mode="edit"
            course={course}
          />

          {/* Restrictions Management Button */}
          <Button
            size="md"
            variant="outline"
            className="px-6 transition-all duration-200 hover:bg-red-50 hover:border-red-300"
            onClick={() => router.push("/restrictions")}
          >
            Manage Restrictions
          </Button>

          {/* Delete Course Button */}
          <Dialog
            open={isDeleteDialogOpen}
            onOpenChange={setIsDeleteDialogOpen}
          >
            <DialogTrigger asChild>
              <Button
                size="md"
                variant="destructive"
                className="px-6 transition-all duration-200 hover:bg-red-700"
              >
                Delete Course
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogTitle className="text-lg">Delete Course</DialogTitle>
              <DialogDescription className="text-base">
                Are you sure you want to delete this course? This action cannot be undone.
              </DialogDescription>
              <div className="flex justify-end gap-2 mt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsDeleteDialogOpen(false)}
                  disabled={isLoading}
                  className="transition-all duration-200"
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteCourse}
                  disabled={isLoading}
                  className="transition-all duration-200 hover:bg-red-700"
                >
                  {isLoading ? "Deleting..." : "Delete Course"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </>
      ) : isTeacher ? (
        <Button
          size="md"
          className="px-6 transition-all duration-200 hover:bg-blue-600"
          onClick={() => router.push(`/courses/${courseId}`)}
        >
          View Course
        </Button>
      ) : isEnrolled ? (
        <Button
          size="md"
          className="px-6 transition-all duration-200 hover:bg-red-600"
          onClick={() => setIsUnenrollConfirmOpen(true)}
          disabled={isLoading}
        >
          {isLoading ? "Unenrolling..." : "Unenroll from Course"}
        </Button>
      ) : (
        <Button
          size="md"
          className="px-6 transition-all duration-200 hover:bg-green-600"
          onClick={() => setIsEnrollConfirmOpen(true)}
          disabled={isLoading}
        >
          {isLoading ? "Enrolling..." : "Enroll in Course"}
        </Button>
      )}

      {/* Confirm Dialogs */}
      <ConfirmDialog
        isOpen={isPublishConfirmOpen}
        onClose={() => setIsPublishConfirmOpen(false)}
        onConfirm={handlePublishCourse}
        title="Publish Course"
        description="Are you sure you want to publish this course? Students will be able to enroll once published."
        confirmText="Publish"
        cancelText="Cancel"
        variant="info"
      />

      <ConfirmDialog
        isOpen={isUnpublishConfirmOpen}
        onClose={() => setIsUnpublishConfirmOpen(false)}
        onConfirm={handleUnpublishCourse}
        title="Unpublish Course"
        description="Are you sure you want to unpublish this course? Students will no longer be able to enroll."
        confirmText="Unpublish"
        cancelText="Cancel"
        variant="warning"
      />

      <ConfirmDialog
        isOpen={isUnenrollConfirmOpen}
        onClose={() => setIsUnenrollConfirmOpen(false)}
        onConfirm={handleUnenrollCourse}
        title="Unenroll from Course"
        description="Are you sure you want to unenroll from this course? You will lose access to course content and chat."
        confirmText="Unenroll"
        cancelText="Cancel"
        variant="warning"
      />

      <ConfirmDialog
        isOpen={isEnrollConfirmOpen}
        onClose={() => setIsEnrollConfirmOpen(false)}
        onConfirm={handleEnrollCourse}
        title="Enroll in Course"
        description="Are you sure you want to enroll in this course? You will gain access to course content and chat."
        confirmText="Enroll"
        cancelText="Cancel"
        variant="info"
      />
    </div>
  );
};

export default CourseActions;
