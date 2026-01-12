"use client";
import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogTitle } from "../../../../components/ui/dialog";
import { Button } from "../../../../components/ui/button";
import { Star, Edit, Plus } from "lucide-react";
import Typography from "../../../../components/ui/Typography";
import { feedbackService, Feedback, CreateFeedbackData } from "@/services/feedbackService";
import { useToast } from "@/components/hooks/use-toast";

interface FeedbackDialogProps {
  isOpen: boolean;
  onClose: () => void;
  courseId: number;
  existingFeedback?: Feedback | null;
  onSuccess: () => void;
}

export default function FeedbackDialog({
  isOpen,
  onClose,
  courseId,
  existingFeedback,
  onSuccess,
}: FeedbackDialogProps) {
  const [rating, setRating] = useState(5);
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const isEditing = !!existingFeedback;

  useEffect(() => {
    if (existingFeedback) {
      setRating(existingFeedback.rating);
      setText(existingFeedback.text);
    } else {
      setRating(5);
      setText("");
    }
  }, [existingFeedback]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (text.length < 10) {
      toast({
        title: "Error",
        description: "Review must be at least 10 characters long",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      const data: CreateFeedbackData = { rating, text };

      if (isEditing) {
        await feedbackService.updateFeedback(courseId, existingFeedback.id, data);
        toast({
          title: "Success",
          description: "Feedback updated successfully",
        });
      } else {
        await feedbackService.createFeedback(courseId, data);
        toast({
          title: "Success",
          description: "Feedback submitted successfully",
        });
      }

      onSuccess();
      onClose();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to save feedback",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={onClose}
    >
      <DialogContent>
        <DialogTitle>{isEditing ? "Edit Feedback" : "Leave Feedback"}</DialogTitle>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          {/* Rating */}
          <div>
            <Typography
              variant="p"
              size="sm"
              className="mb-2 block"
            >
              Rating
            </Typography>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className="p-1 hover:scale-110 transition-transform"
                >
                  <Star
                    className={`w-5 h-5 ${
                      star <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Review Text */}
          <div>
            <Typography
              variant="p"
              size="sm"
              className="mb-2 block"
            >
              Review
            </Typography>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              maxLength={500}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Share your experience with this course..."
            />
            <Typography
              variant="p"
              size="sm"
              className="text-gray-500 mt-1"
            >
              {text.length}/500 characters
            </Typography>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              size="sm"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              size="sm"
            >
              {isSubmitting ? (
                "Saving..."
              ) : isEditing ? (
                <>
                  <Edit className="w-4 h-4 mr-1" />
                  Update
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4 mr-1" />
                  Submit
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
