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

interface CourseActionsProps {
  isTeacher: boolean;
  isCourseOwner: boolean;
  courseId: string;
  isEnrolled: boolean;
}

const CourseActions = ({ isTeacher, isCourseOwner, courseId, isEnrolled }: CourseActionsProps) => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
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

  const handleEnrollCourse = async () => {
    try {
      setIsLoading(true);
      await enrollmentService.createEnrollment(courseId);
      router.refresh();
      showToast.success("Enrolled in course successfully");
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
    } catch (error) {
      console.error("Error unenrolling from course:", error);
      showToast.error("Error unenrolling from course");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex gap-3">
      {isTeacher && isCourseOwner ? (
        <>
          <Button
            size="md"
            variant="outline"
            className="px-6"
            onClick={() => router.push(`/courses/${courseId}/edit`)}
          >
            Edit Course
          </Button>
          <Dialog
            open={isDeleteDialogOpen}
            onOpenChange={setIsDeleteDialogOpen}
          >
            <DialogTrigger asChild>
              <Button
                size="md"
                variant="destructive"
                className="px-6"
              >
                Delete Course
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogTitle>Delete Course</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete this course? This action cannot be undone.
              </DialogDescription>
              <div className="flex justify-end gap-2 mt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsDeleteDialogOpen(false)}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteCourse}
                  disabled={isLoading}
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
          className="px-6"
          onClick={() => router.push(`/courses/${courseId}`)}
        >
          View Course
        </Button>
      ) : isEnrolled ? (
        <Button
          size="md"
          className="px-6"
          onClick={handleUnenrollCourse}
          disabled={isLoading}
        >
          {isLoading ? "Unenrolling..." : "Unenroll from Course"}
        </Button>
      ) : (
        <Button
          size="md"
          className="px-6"
          onClick={handleEnrollCourse}
          disabled={isLoading}
        >
          {isLoading ? "Enrolling..." : "Enroll in Course"}
        </Button>
      )}
    </div>
  );
};

export default CourseActions;
