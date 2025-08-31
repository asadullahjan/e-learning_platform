"use client";
import { useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import Typography from "@/components/ui/Typography";
import { Plus, Upload, X, Edit } from "lucide-react";
import { lessonService } from "@/services/lessonService";
import { useToast } from "@/components/hooks/use-toast";
import Input from "@/components/ui/Input";
import { useRouter } from "next/navigation";
import { CourseLesson } from "@/lib/types";

interface LessonFormDialogProps {
  courseId: number;
  lesson?: CourseLesson; // For edit mode
  mode?: "create" | "edit";
}

export function LessonFormDialog({ courseId, lesson, mode = "create" }: LessonFormDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: lesson?.title || "",
    description: lesson?.description || "",
    content: lesson?.content || "",
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [removeExistingFile, setRemoveExistingFile] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  const handleRemoveExistingFile = () => {
    setRemoveExistingFile(true);
    setSelectedFile(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim() || !formData.description.trim()) {
      toast({
        title: "Validation Error",
        description: "Title and description are required.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      if (mode === "edit" && lesson) {
        // Update existing lesson
        const updateData: any = { ...formData };

        if (selectedFile) {
          updateData.file = selectedFile;
        } else if (removeExistingFile) {
          updateData.file = null; // This will remove the existing file
        }

        await lessonService.updateLesson(courseId, lesson.id, updateData);

        toast({
          title: "Success",
          description: "Lesson updated successfully!",
        });

        // Navigate to lesson detail page
        router.push(`/courses/${courseId}/lessons/${lesson.id}`);
      } else {
        // Create new lesson
        const newLesson = await lessonService.createLesson(courseId, {
          ...formData,
          file: selectedFile || undefined,
        });

        toast({
          title: "Success",
          description: "Lesson created successfully!",
        });

        // Navigate to lesson detail page
        router.push(`/courses/${courseId}/lessons/${newLesson.id}`);
      }

      // Reset form and close dialog
      setFormData({ title: "", description: "", content: "" });
      setSelectedFile(null);
      setRemoveExistingFile(false);
      setIsOpen(false);
    } catch (error) {
      console.log(error);
      toast({
        title: "Error",
        description: `Failed to ${mode === "edit" ? "update" : "create"} lesson. Please try again.`,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: lesson?.title || "",
      description: lesson?.description || "",
      content: lesson?.content || "",
    });
    setSelectedFile(null);
    setRemoveExistingFile(false);
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={setIsOpen}
    >
      <DialogTrigger asChild>
        <Button size="sm">
          {mode === "edit" ? (
            <>
              <Edit className="w-4 h-4 mr-2" />
              Edit Lesson
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-2" />
              Add Lesson
            </>
          )}
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogTitle>
          <Typography variant="h3">
            {mode === "edit" ? "Edit Lesson" : "Create New Lesson"}
          </Typography>
        </DialogTitle>

        <form
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Lesson Title *</Label>
            <Input
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Enter lesson title"
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Input
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Enter lesson description"
              required
            />
          </div>

          {/* Content */}
          <div className="space-y-2">
            <Label htmlFor="content">Content</Label>
            <textarea
              id="content"
              name="content"
              value={formData.content}
              onChange={handleInputChange}
              placeholder="Enter lesson content (optional)"
              className="w-full min-h-[120px] p-3 border border-gray-300 rounded-md resize-vertical focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* File Upload */}
          <div className="space-y-2">
            <Label>Attach File (Optional)</Label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center gap-2">
                    <Upload className="w-5 h-5 text-blue-600" />
                    <Typography
                      variant="p"
                      className="font-medium"
                    >
                      {selectedFile.name}
                    </Typography>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={removeFile}
                  >
                    <X className="w-4 h-4 mr-2" />
                    Remove File
                  </Button>
                </div>
              ) : lesson?.file && mode === "edit" ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      📎
                    </div>
                    <Typography
                      variant="p"
                      className="font-medium"
                    >
                      {lesson.file.original_name}
                    </Typography>
                  </div>
                  <Typography
                    variant="span"
                    size="sm"
                    color="muted"
                  >
                    Current file (upload new file to replace)
                  </Typography>
                  <div className="flex gap-2 justify-center">
                    <Input
                      type="file"
                      onChange={handleFileChange}
                      accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.zip"
                      className="hidden"
                      id="file-upload"
                      name="file-upload"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      asChild
                    >
                      <Label
                        htmlFor="file-upload"
                        className="cursor-pointer"
                      >
                        Replace File
                      </Label>
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleRemoveExistingFile}
                    >
                      Remove File
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto" />
                  <Typography
                    variant="p"
                    color="muted"
                  >
                    Click to upload
                  </Typography>
                  <Typography
                    variant="span"
                    size="sm"
                    color="muted"
                  >
                    PDF, DOC, Images, etc. (Max 10MB)
                  </Typography>
                  <Input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.zip"
                    className="hidden"
                    id="file-upload"
                    name="file-upload"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    asChild
                  >
                    <Label
                      htmlFor="file-upload"
                      className="cursor-pointer"
                    >
                      Choose File
                    </Label>
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={resetForm}
              disabled={isLoading}
            >
              Reset
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="min-w-[100px]"
            >
              {isLoading
                ? mode === "edit"
                  ? "Updating..."
                  : "Creating..."
                : mode === "edit"
                ? "Update Lesson"
                : "Create Lesson"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
