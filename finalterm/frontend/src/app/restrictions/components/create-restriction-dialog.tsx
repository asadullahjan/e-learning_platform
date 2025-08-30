"use client";
import { useState } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Typography from "@/components/ui/Typography";
import { restrictionService, CreateRestrictionData } from "@/services/restrictionService";
import { useToast } from "@/components/hooks/use-toast";

interface CreateRestrictionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  courses: any[];
  users: any[];
}

export default function CreateRestrictionDialog({
  isOpen,
  onClose,
  onSuccess,
  courses,
  users,
}: CreateRestrictionDialogProps) {
  const [courseId, setCourseId] = useState<string>("");
  const [studentId, setStudentId] = useState<string>("");
  const [reason, setReason] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!courseId || !studentId) {
      toast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const data: CreateRestrictionData = {
        student: parseInt(studentId),
        course: parseInt(courseId),
        reason: reason.trim(),
      };

      await restrictionService.createRestriction(data);

      toast({
        title: "Success",
        description: "Student restriction created successfully",
      });

      onSuccess();
      onClose();
      resetForm();
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.non_field_errors?.[0] ||
        "Failed to create restriction";

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setCourseId("");
    setStudentId("");
    setReason("");
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  // Filter students to only show those who are not already restricted in the selected course
  const getAvailableStudents = () => {
    if (!courseId) return users;

    // Get students who are not already restricted in this course
    const restrictedStudentIds = new Set();
    // You might want to add logic here to check existing restrictions

    return users.filter((user) => user.role === "student" && !restrictedStudentIds.has(user.id));
  };

  const availableStudents = getAvailableStudents();

  return (
    <Dialog
      open={isOpen}
      onOpenChange={handleClose}
    >
      <DialogContent>
        <DialogTitle className="text-sm font-medium">Create New Restriction</DialogTitle>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          <div>
            <Label htmlFor="course">Course *</Label>
            <Select
              value={courseId}
              onValueChange={setCourseId}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a course" />
              </SelectTrigger>
              <SelectContent>
                {courses.map((course) => (
                  <SelectItem
                    key={course.id}
                    value={course.id.toString()}
                  >
                    {course.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="student">Student *</Label>
            <Select
              value={studentId}
              onValueChange={setStudentId}
              disabled={!courseId}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={courseId ? "Select a student to restrict" : "Select a course first"}
                />
              </SelectTrigger>
              <SelectContent>
                {availableStudents.map((student) => (
                  <SelectItem
                    key={student.id}
                    value={student.id.toString()}
                  >
                    {student.username} ({student.email})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {!courseId && (
              <Typography
                variant="p"
                size="xs"
                className="text-gray-500 mt-1"
              >
                Please select a course first to see available students
              </Typography>
            )}
          </div>

          <div>
            <Label htmlFor="reason">Reason</Label>
            <textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter reason for restriction..."
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
              size="sm"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !courseId || !studentId}
              loading={isLoading}
              size="sm"
              className="bg-red-600 hover:bg-red-700"
            >
              Create Restriction
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
