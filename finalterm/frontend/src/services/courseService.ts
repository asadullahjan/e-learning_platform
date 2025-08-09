import { Course } from "@/lib/types";

export const courseService = {
  getCourse: async (courseId: string) => {
    const response = await fetch(`/api/courses/${courseId}`);
    return response.json();
  },
  createCourse: async (course: Course) => {
    const response = await fetch("/api/courses", {
      method: "POST",
      body: JSON.stringify(course),
    });
    return response.json();
  },
  updateCourse: async (courseId: string, course: Partial<Course>) => {
    const response = await fetch(`/api/courses/${courseId}`, {
      method: "PATCH",
      body: JSON.stringify(course),
    });
    return response.json();
  },
  deleteCourse: async (courseId: string) => {
    const response = await fetch(`/api/courses/${courseId}`, {
      method: "DELETE",
    });
    return response.json();
  },
};
