import { CourseLesson, ListResponse } from "@/lib/types";
import api, { createServerApi } from "./api";

export interface LessonListResponse extends ListResponse<CourseLesson> {}

export interface CreateLessonData {
  title: string;
  description: string;
  content?: string;
  file?: File;
}

export interface UpdateLessonData extends Partial<CreateLessonData> {
  published_at?: string;
}

export const lessonService = {
  // Get lessons for a specific course
  getCourseLessons: async (
    courseId: string,
    searchParams?: {
      [key: string]: string | string[] | undefined;
    }
  ): Promise<LessonListResponse> => {
    const response = await api.get<LessonListResponse>(`/courses/${courseId}/lessons/`, {
      params: searchParams,
    });
    return response.data;
  },

  // Get a specific lesson
  getLesson: async (courseId: string, lessonId: string): Promise<CourseLesson> => {
    const response = await api.get<CourseLesson>(`/courses/${courseId}/lessons/${lessonId}/`);
    return response.data;
  },

  // Create a new lesson
  createLesson: async (courseId: string, lesson: CreateLessonData): Promise<CourseLesson> => {
    const formData = new FormData();
    formData.append("title", lesson.title);
    formData.append("description", lesson.description);

    if (lesson.content) {
      formData.append("content", lesson.content);
    }

    if (lesson.file) {
      formData.append("file", lesson.file);
    }

    const response = await api.post<CourseLesson>(`/courses/${courseId}/lessons/`, formData);
    return response.data;
  },

  // Update a lesson
  updateLesson: async (
    courseId: string,
    lessonId: string,
    lesson: UpdateLessonData
  ): Promise<CourseLesson> => {
    const formData = new FormData();

    if (lesson.title) formData.append("title", lesson.title);
    if (lesson.description) formData.append("description", lesson.description);
    if (lesson.content) formData.append("content", lesson.content);
    if (lesson.file) formData.append("file", lesson.file);
    if (lesson.published_at) formData.append("published_at", lesson.published_at);

    const response = await api.patch<CourseLesson>(
      `/courses/${courseId}/lessons/${lessonId}/`,
      formData
    );
    return response.data;
  },

  // Delete a lesson
  deleteLesson: async (courseId: string, lessonId: string): Promise<void> => {
    await api.delete(`/courses/${courseId}/lessons/${lessonId}/`);
  },

  // Publish/unpublish a lesson
  toggleLessonPublish: async (
    courseId: string,
    lessonId: string,
    published: boolean
  ): Promise<CourseLesson> => {
    const published_at = published ? new Date().toISOString() : undefined;
    return lessonService.updateLesson(courseId, lessonId, { published_at });
  },

  // Get published lessons only
  getPublishedLessons: async (
    courseId: string,
    searchParams?: {
      [key: string]: string | string[] | undefined;
    }
  ): Promise<CourseLesson[]> => {
    const params = { ...searchParams, published: true };
    const response = await api.get<LessonListResponse>(`/courses/${courseId}/lessons/`, { params });
    return response.data.results;
  },

  // Search lessons by title or description
  searchLessons: async (courseId: string, query: string): Promise<CourseLesson[]> => {
    const response = await api.get<LessonListResponse>(`/courses/${courseId}/lessons/`, {
      params: { search: query },
    });
    return response.data.results;
  },

  // Server-side methods (GET operations only)
  server: {
    getCourseLessons: async (
      courseId: string,
      searchParams?: {
        [key: string]: string | string[] | undefined;
      }
    ): Promise<LessonListResponse> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<LessonListResponse>(`/courses/${courseId}/lessons/`, {
        params: searchParams,
      });
      return response.data;
    },

    getLesson: async (courseId: string, lessonId: string): Promise<CourseLesson> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<CourseLesson>(
        `/courses/${courseId}/lessons/${lessonId}/`
      );
      return response.data;
    },
  },
};
