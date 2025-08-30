import { Course, ListResponse } from "@/lib/types";
import api, { createServerApi } from "./api";

export interface CreateCourseData {
  title: string;
  description: string;
  content?: string;
  published_at?: string;
}

export interface UpdateCourseData extends Partial<CreateCourseData> {
  // Additional fields that can be updated
  is_active?: boolean;
}

export const courseService = {
  getCourses: async (searchParams?: {
    [key: string]: string | string[] | undefined;
  }): Promise<ListResponse<Course>> => {
    const response = await api.get<ListResponse<Course>>("/courses/", { params: searchParams });
    return response.data;
  },

  getCourse: async (courseId: string): Promise<Course> => {
    const response = await api.get<Course>(`/courses/${courseId}/`);
    return response.data;
  },

  createCourse: async (course: CreateCourseData): Promise<Course> => {
    const response = await api.post<Course>("/courses/", course);
    return response.data;
  },

  updateCourse: async (courseId: string, course: UpdateCourseData): Promise<Course> => {
    const response = await api.patch<Course>(`/courses/${courseId}/`, course);
    return response.data;
  },

  deleteCourse: async (courseId: string): Promise<void> => {
    await api.delete(`/courses/${courseId}/`);
  },

  // Additional methods for better course management
  publishCourse: async (courseId: string): Promise<Course> => {
    return courseService.updateCourse(courseId, {
      published_at: new Date().toISOString(),
    });
  },

  unpublishCourse: async (courseId: string): Promise<Course> => {
    return courseService.updateCourse(courseId, {
      published_at: undefined,
    });
  },

  // Get courses by teacher
  getTeacherCourses: async (teacherId: string): Promise<Course[]> => {
    const response = await api.get<ListResponse<Course>>("/courses/", {
      params: { teacher: teacherId },
    });
    return response.data.results;
  },

  // Server-side methods (GET operations only)
  server: {
    getCourses: async (searchParams?: {
      [key: string]: string | string[] | undefined;
    }): Promise<ListResponse<Course>> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Course>>("/courses/", {
        params: searchParams,
      });
      return response.data;
    },

    getCourse: async (courseId: string): Promise<Course> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<Course>(`/courses/${courseId}/`);
      return response.data;
    },
  },
};
