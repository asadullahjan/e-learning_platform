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
import { User } from "@/services/userService";

interface CreateRestrictionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  courseId: number;
  courseTitle: string;
  enrolledStudents: User[];
}

export default function CreateRestrictionDialog({
  isOpen,
  onClose,
  onSuccess,
  courseId,
  courseTitle,
  enrolledStudents,
}: CreateRestrictionDialogProps) {
  const [studentId, setStudentId] = useState<number>(0);
  const [reason, setReason] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!studentId) {
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
        student: studentId,
        course: courseId,
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
    setStudentId(0);
    setReason("");
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={handleClose}
    >
      <DialogContent>
        <DialogTitle className="text-sm font-medium">Restrict Student from Course</DialogTitle>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          <div>
            <Label htmlFor="course">Course</Label>
            <Typography
              variant="p"
              size="sm"
              className="text-gray-600 mt-1"
            >
              {courseTitle}
            </Typography>
          </div>

          <div>
            <Label htmlFor="student">Student *</Label>
            <Select
              value={studentId.toString()}
              onValueChange={(value) => setStudentId(parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a student to restrict" />
              </SelectTrigger>
              <SelectContent>
                {enrolledStudents.map((student) => (
                  <SelectItem
                    key={student.id}
                    value={student.id.toString()}
                  >
                    {student.username} ({student.email})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
              disabled={isLoading}
              loading={isLoading}
              size="sm"
            >
              Block Student
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
