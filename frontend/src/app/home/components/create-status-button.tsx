"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { statusService } from "@/services/statusService";
import { useToast } from "@/components/hooks/use-toast";
import { Plus } from "lucide-react";

interface CreateStatusButtonProps {
  onStatusCreated?: () => void;
}

export default function CreateStatusButton({ onStatusCreated }: CreateStatusButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!content.trim()) {
      toast({
        title: "Error",
        description: "Status content cannot be empty",
        variant: "destructive",
      });
      return;
    }

    if (content.length > 500) {
      toast({
        title: "Error",
        description: "Status content cannot exceed 500 characters",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      await statusService.createStatus({ content: content.trim() });

      toast({
        title: "Success",
        description: "Status posted successfully!",
      });

      setContent("");
      setIsOpen(false);

      // Call the callback to refresh the status list
      if (onStatusCreated) {
        onStatusCreated();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to post status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={setIsOpen}
    >
      <DialogTrigger asChild>
        <Button className="mb-4">
          <Plus className="w-4 h-4 mr-2" />
          Add Status
        </Button>
      </DialogTrigger>

      <DialogContent>
        <div className="mb-3">
          <DialogTitle>Share a Status Update</DialogTitle>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          <div>
            <Label htmlFor="status-content">What's on your mind?</Label>
            <textarea
              id="status-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share your thoughts, achievements, or questions..."
              maxLength={500}
              rows={4}
              className="mt-2 w-full px-4 py-2 border border-gray-300 rounded-md bg-white outline-primary/40 focus:outline-1 resize-none"
            />
            <div className="text-right mt-1">
              <span className="text-sm text-gray-500">{content.length}/500</span>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Posting..." : "Post Status"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
