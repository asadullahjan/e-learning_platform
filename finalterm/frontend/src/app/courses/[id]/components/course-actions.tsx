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

interface CourseActionsProps {
  isTeacher: boolean;
  isCourseOwner: boolean;
  courseId: string;
}

const CourseActions = ({ isTeacher, isCourseOwner, courseId }: CourseActionsProps) => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const router = useRouter();
  const handleDeleteCourse = () => {
    setIsDeleteDialogOpen(false);
    console.log("delete course");
  };

  const handleEnrollCourse = () => {
    console.log("enroll course");
  };

  return (
    <div className="flex ">
      {isTeacher && isCourseOwner ? (
        <div className="flex gap-3">
          <Button
            size="md"
            variant="outline"
            className="px-8"
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
                className="px-8"
              >
                Delete Course
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogTitle>Delete Course</DialogTitle>
              <DialogDescription>Are you sure you want to delete this course?</DialogDescription>
              <div className="flex justify-end gap-2">
                <Button
                  size="md"
                  variant="destructive"
                  className="px-8"
                  onClick={handleDeleteCourse}
                >
                  Delete Course
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      ) : isTeacher ? (
        <Button
          size="md"
          className="px-8"
          onClick={() => router.push(`/courses/${courseId}`)}
        >
          View Course
        </Button>
      ) : (
        <Button
          size="md"
          className="px-8"
          onClick={handleEnrollCourse}
        >
          Enroll in Course
        </Button>
      )}
    </div>
  );
};

export default CourseActions;
