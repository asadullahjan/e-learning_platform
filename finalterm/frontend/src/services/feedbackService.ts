import { ListResponse } from "@/lib/types";
import api from "./api";

export interface Feedback {
  id: string;
  user: {
    id: string;
    username: string;
    role: string;
  } | null;
  rating: number;
  text: string;
  created_at: string;
}

export interface CreateFeedbackData {
  rating: number;
  text: string;
}

export const feedbackService = {
  getCourseFeedbacks: async (courseId: string): Promise<Feedback[]> => {
    const response = await api.get<ListResponse<Feedback>>(`/courses/${courseId}/feedbacks/`);
    return response.data.results;
  },

  createFeedback: async (courseId: string, data: CreateFeedbackData): Promise<Feedback> => {
    const response = await api.post<Feedback>(`/courses/${courseId}/feedbacks/`, data);
    return response.data;
  },

  updateFeedback: async (
    courseId: string,
    feedbackId: string,
    data: CreateFeedbackData
  ): Promise<Feedback> => {
    const response = await api.patch<Feedback>(
      `/courses/${courseId}/feedbacks/${feedbackId}/`,
      data
    );
    return response.data;
  },

  deleteFeedback: async (courseId: string, feedbackId: string): Promise<void> => {
    await api.delete(`/courses/${courseId}/feedbacks/${feedbackId}/`);
  },
};
