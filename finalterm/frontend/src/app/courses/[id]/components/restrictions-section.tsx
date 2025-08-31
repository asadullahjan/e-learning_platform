"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Typography from "@/components/ui/Typography";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Trash2, UserX, Calendar } from "lucide-react";
import { restrictionService, StudentRestriction } from "@/services/restrictionService";
import { enrollmentService } from "@/services/enrollmentService";
import { useToast } from "@/components/hooks/use-toast";
import { useAuthStore } from "@/store/authStore";
import CreateRestrictionDialog from "./create-restriction-dialog";
import ConfirmDialog from "@/components/ui/confirm-dialog";
import { ListResponse } from "@/lib/types";
import { User } from "@/services/userService";

interface RestrictionsSectionProps {
  courseId: number;
  courseTitle: string;
}

export default function RestrictionsSection({ courseId, courseTitle }: RestrictionsSectionProps) {
  const [restrictions, setRestrictions] = useState<ListResponse<StudentRestriction>>({
    results: [],
    count: 0,
    next: null,
    previous: null,
  });
  const [enrolledStudents, setEnrolledStudents] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [restrictionToDelete, setRestrictionToDelete] = useState<StudentRestriction | null>(null);
  const { user } = useAuthStore();
  const { toast } = useToast();

  const isTeacher = user?.role === "teacher";

  useEffect(() => {
    if (isTeacher) {
      loadRestrictions();
      loadEnrolledStudents();
    }
  }, [isTeacher]);

  const loadRestrictions = async () => {
    try {
      const data = await restrictionService.getRestrictions({ courseId });
      setRestrictions(data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load restrictions",
        variant: "destructive",
      });
    }
  };

  const loadEnrolledStudents = async () => {
    try {
      const enrollments = await enrollmentService.getCourseEnrollments(courseId);
      const activeStudents = enrollments.filter((e) => e.is_active).map((e) => e.user);
      setEnrolledStudents(activeStudents);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load enrolled students",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateRestriction = () => {
    setIsDialogOpen(true);
  };

  const handleRestrictionSuccess = () => {
    loadRestrictions();
  };

  const handleDeleteRestriction = (restriction: StudentRestriction) => {
    setRestrictionToDelete(restriction);
    setIsConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!restrictionToDelete) return;

    try {
      await restrictionService.deleteRestriction(restrictionToDelete.id);
      toast({
        title: "Success",
        description: "Restriction removed successfully",
      });
      loadRestrictions();
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to remove restriction",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (!isTeacher) {
    return null;
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Student Restrictions</CardTitle>
        </CardHeader>
        <CardContent>
          <Typography
            variant="p"
            size="sm"
            className="text-gray-500"
          >
            Loading restrictions...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">Student Restrictions</CardTitle>
          <Button
            onClick={handleCreateRestriction}
            size="sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            Restrict Student
          </Button>
        </CardHeader>

        <CardContent className="space-y-4">
          {restrictions.results.length === 0 ? (
            <div className="text-center py-8">
              <UserX className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <Typography
                variant="p"
                size="sm"
                className="text-gray-500"
              >
                No students are currently restricted from this course
              </Typography>
            </div>
          ) : (
            <div className="space-y-3">
              {restrictions.results.map((restriction) => (
                <div
                  key={restriction.id}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Typography
                          variant="p"
                          size="sm"
                          className="font-medium"
                        >
                          {restriction.student?.username || "Unknown Student"}
                        </Typography>
                        <span className="text-xs text-gray-500">
                          ({restriction.student?.email || "No email"})
                        </span>
                      </div>

                      {restriction.reason && (
                        <Typography
                          variant="p"
                          size="sm"
                          className="text-gray-700 mb-2"
                        >
                          {restriction.reason}
                        </Typography>
                      )}

                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          Restricted on {formatDate(restriction.created_at)}
                        </div>
                      </div>
                    </div>

                    <Button
                      onClick={() => handleDeleteRestriction(restriction)}
                      size="sm"
                      variant="outline"
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <CreateRestrictionDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSuccess={handleRestrictionSuccess}
        courseId={courseId}
        courseTitle={courseTitle}
        enrolledStudents={enrolledStudents}
      />

      <ConfirmDialog
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={confirmDelete}
        title="Remove Restriction"
        description="Are you sure you want to remove this restriction? The student will regain access to the course."
        confirmText="Remove"
        cancelText="Cancel"
        variant="danger"
      />
    </>
  );
}
