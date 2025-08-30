"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Typography from "@/components/ui/Typography";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Trash2, UserX, Calendar, BookOpen, Filter, Plus } from "lucide-react";
import { restrictionService, StudentRestriction } from "@/services/restrictionService";
import { courseService } from "@/services/courseService";
import { userService, User } from "@/services/userService";
import { useToast } from "@/components/hooks/use-toast";
import ConfirmDialog from "@/components/ui/confirm-dialog";
import CreateRestrictionDialog from "@/app/restrictions/components/create-restriction-dialog";
import { Course, ListResponse } from "@/lib/types";
import { useAuthStore } from "@/store/authStore";

export default function RestrictionsManagement() {
  const [restrictions, setRestrictions] = useState<ListResponse<StudentRestriction>>({
    results: [],
    count: 0,
    next: null,
    previous: null,
  });
  const [filteredRestrictions, setFilteredRestrictions] = useState<StudentRestriction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [courseFilter, setCourseFilter] = useState<string>("all");
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [restrictionToDelete, setRestrictionToDelete] = useState<StudentRestriction | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const { toast } = useToast();
  const { user } = useAuthStore();

  useEffect(() => {
    loadRestrictions();
    loadCourses();
  }, [user]);

  useEffect(() => {
    filterRestrictions();
  }, [restrictions, courseFilter]);

  const loadRestrictions = async () => {
    try {
      const data = await restrictionService.getRestrictions({});
      setRestrictions(data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load restrictions",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadCourses = async () => {
    try {
      if (!user) return;
      const data = await courseService.getTeacherCourses(user.id);
      setCourses(data);
    } catch (error: any) {
      console.error("Failed to load courses:", error);
    }
  };

  const filterRestrictions = () => {
    if (courseFilter === "all") {
      setFilteredRestrictions(restrictions.results);
    } else {
      const filtered = restrictions.results.filter((r) => r.course?.id === parseInt(courseFilter));
      setFilteredRestrictions(filtered);
    }
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

  const handleCreateRestriction = () => {
    setIsCreateDialogOpen(true);
  };

  const handleRestrictionCreated = () => {
    loadRestrictions();
    setIsCreateDialogOpen(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getUniqueCourses = () => {
    const courses = restrictions.results.filter((r) => r.course).map((r) => r.course!);

    return Array.from(new Map(courses.map((c) => [c.id, c])).values());
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Loading Restrictions</CardTitle>
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

  const uniqueCourses = getUniqueCourses();

  return (
    <>
      {/* Filter Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filter Restrictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Typography
                variant="p"
                size="sm"
              >
                Course:
              </Typography>
              <Select
                value={courseFilter}
                onValueChange={setCourseFilter}
              >
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="All courses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All courses</SelectItem>
                  {uniqueCourses.map((course) => (
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

            <Typography
              variant="p"
              size="sm"
              className="text-gray-600"
            >
              {filteredRestrictions.length} restriction
              {filteredRestrictions.length !== 1 ? "s" : ""} found
            </Typography>
          </div>
        </CardContent>
      </Card>

      {/* Restrictions List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-sm font-medium">All Restrictions</CardTitle>
          <Button
            onClick={handleCreateRestriction}
            className="bg-red-600 hover:bg-red-700"
          >
            <UserX className="w-4 h-4 mr-2" />
            Restrict User
          </Button>
        </CardHeader>

        <CardContent className="space-y-4">
          {filteredRestrictions.length === 0 ? (
            <div className="text-center py-12">
              <UserX className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <Typography
                variant="p"
                size="sm"
                className="text-gray-500 mb-2"
              >
                {courseFilter === "all"
                  ? "No restrictions found"
                  : "No restrictions found for this course"}
              </Typography>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRestrictions.map((restriction) => (
                <div
                  key={restriction.id}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-3">
                        <div className="flex items-center gap-2">
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

                        {restriction.course && (
                          <div className="flex items-center gap-1 text-xs text-gray-600">
                            <BookOpen className="w-3 h-3" />
                            {restriction.course.title}
                          </div>
                        )}
                      </div>

                      {restriction.reason && (
                        <Typography
                          variant="p"
                          size="sm"
                          className="text-gray-700 mb-3"
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

      {/* Create Restriction Dialog */}
      <CreateRestrictionDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onSuccess={handleRestrictionCreated}
        courses={courses}
      />

      {/* Delete Confirmation Dialog */}
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
