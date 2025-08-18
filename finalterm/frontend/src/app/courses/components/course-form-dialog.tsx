"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { courseService } from "@/services/courseService";
import { showToast } from "@/lib/toast";
import Input from "@/components/ui/Input";
import { Course } from "@/lib/types";
import { useEffect, useState } from "react";

const formSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
});

type FormData = z.infer<typeof formSchema>;

interface CourseFormDialogProps {
  mode: "create" | "edit";
  course?: Course; // Required for edit mode
}

const CourseFormDialog = ({
  mode,
  course,
}: CourseFormDialogProps) => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      description: "",
    },
  });

  // Reset form when dialog opens/closes or course changes
  useEffect(() => {
    if (isOpen) {
      if (mode === "edit" && course) {
        form.reset({
          title: course.title,
          description: course.description,
        });
      } else {
        form.reset({
          title: "",
          description: "",
        });
      }
    }
  }, [isOpen, mode, course, form]);

  const onSubmit = async (data: FormData) => {
    try {
      if (mode === "create") {
        const newCourse = await courseService.createCourse(data);
        showToast.success("Course created successfully!");
        setIsOpen(false);
        router.push(`/courses/${newCourse.id}`);
      } else {
        // Edit mode
        if (!course) return;
        await courseService.updateCourse(course.id, data);
        showToast.success("Course updated successfully!");
        setIsOpen(false);
        router.refresh(); // Refresh to show updated data
      }
    } catch (error) {
      const action = mode === "create" ? "create" : "update";
      showToast.error(`Failed to ${action} course`);
      console.error(error);
    }
  };

  const isSubmitting = form.formState.isSubmitting;
  const isEditMode = mode === "edit";

  return (
    <Dialog
      open={isOpen}
      onOpenChange={setIsOpen}
    >
      <DialogTrigger asChild>
        <Button
          size="md"
          variant="outline"
        >
          {mode === "create" ? "Create Course" : "Edit Course"}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <div className="mb-6">
          <DialogTitle>{isEditMode ? "Edit Course" : "Create New Course"}</DialogTitle>
          <DialogDescription>
            {isEditMode
              ? "Update your course information below."
              : "Fill in the details below to create a new course."}
          </DialogDescription>
        </div>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="space-y-6"
          >
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Course Title</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter course title"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Course Description</FormLabel>
                  <FormControl>
                    <textarea
                      placeholder="Describe your course..."
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex gap-2 justify-end mt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsOpen(false)}
                disabled={isSubmitting}
                className="w-full"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                loading={isSubmitting}
                disabled={isSubmitting}
                className="w-full"
              >
                {isSubmitting
                  ? isEditMode
                    ? "Updating..."
                    : "Creating..."
                  : isEditMode
                  ? "Update Course"
                  : "Create Course"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default CourseFormDialog;
