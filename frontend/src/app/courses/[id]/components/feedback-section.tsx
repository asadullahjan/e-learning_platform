"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import Typography from "@/components/ui/Typography";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Star, Plus, Edit, Trash2 } from "lucide-react";
import { feedbackService, Feedback } from "@/services/feedbackService";
import FeedbackDialog from "@/app/courses/[id]/components/feedback-dialog";
import ConfirmDialog from "@/components/ui/confirm-dialog";
import { useToast } from "@/components/hooks/use-toast";
import { useAuthStore } from "@/store/authStore";

interface FeedbackSectionProps {
  courseId: number;
  isEnrolled: boolean;
}

export default function FeedbackSection({ courseId, isEnrolled }: FeedbackSectionProps) {
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingFeedback, setEditingFeedback] = useState<Feedback | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [feedbackToDelete, setFeedbackToDelete] = useState<Feedback | null>(null);
  const { user } = useAuthStore();
  const { toast } = useToast();

  const userFeedback = feedback.find((f) => f.user?.id === user?.id);

  const loadFeedback = async () => {
    try {
      const data = await feedbackService.getCourseFeedbacks(courseId);
      setFeedback(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load feedback",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFeedback();
  }, [courseId]);

  const handleCreateFeedback = () => {
    setEditingFeedback(null);
    setIsDialogOpen(true);
  };

  const handleEditFeedback = (feedback: Feedback) => {
    setEditingFeedback(feedback);
    setIsDialogOpen(true);
  };

  const handleDeleteFeedback = (feedback: Feedback) => {
    setFeedbackToDelete(feedback);
    setIsConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (!feedbackToDelete) return;

    try {
      await feedbackService.deleteFeedback(courseId, feedbackToDelete.id);
      toast({
        title: "Success",
        description: "Feedback deleted successfully",
      });
      loadFeedback();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete feedback",
        variant: "destructive",
      });
    }
  };

  const handleFeedbackSuccess = () => {
    loadFeedback();
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Course Feedback</CardTitle>
        </CardHeader>
        <CardContent>
          <Typography
            variant="p"
            size="sm"
            className="text-gray-500"
          >
            Loading feedback...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Course Feedback</CardTitle>
          {isEnrolled && !userFeedback && (
            <Button
              onClick={handleCreateFeedback}
              size="sm"
            >
              <Plus className="w-4 h-4 mr-1" />
              Leave Feedback
            </Button>
          )}
          {!isEnrolled && (
            <Typography
              variant="p"
              size="sm"
              className="text-gray-500"
            >
              Enroll in this course to leave feedback
            </Typography>
          )}
        </CardHeader>

        <CardContent className="space-y-4">
          {feedback.length === 0 ? (
            <Typography
              variant="p"
              size="sm"
              className="text-gray-500 text-center py-4"
            >
              No feedback yet. Be the first to leave a review!
            </Typography>
          ) : (
            feedback.map((item) => (
              <div
                key={item.id}
                className="border-b border-gray-100 pb-4 last:border-b-0"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Typography
                        variant="p"
                        size="sm"
                        className="font-medium"
                      >
                        {item.user?.username || "Deleted User"}
                      </Typography>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`w-3 h-3 ${
                              star <= item.rating
                                ? "fill-yellow-400 text-yellow-400"
                                : "text-gray-300"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <Typography
                      variant="p"
                      size="sm"
                      className="text-gray-700"
                    >
                      {item.text}
                    </Typography>
                    <Typography
                      variant="p"
                      size="sm"
                      className="text-gray-500 mt-2"
                    >
                      {new Date(item.created_at).toLocaleDateString()}
                    </Typography>
                  </div>

                  {item.user?.id === user?.id && (
                    <div className="flex gap-1">
                      <Button
                        onClick={() => handleEditFeedback(item)}
                        size="sm"
                        variant="outline"
                      >
                        <Edit className="w-3 h-3" />
                      </Button>
                      <Button
                        onClick={() => handleDeleteFeedback(item)}
                        size="sm"
                        variant="outline"
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <FeedbackDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        courseId={courseId}
        existingFeedback={editingFeedback}
        onSuccess={handleFeedbackSuccess}
      />

      <ConfirmDialog
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={confirmDelete}
        title="Delete Feedback"
        description="Are you sure you want to delete this feedback? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />
    </>
  );
}
