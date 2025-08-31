import { ListResponse } from "@/lib/types";
import api from "./api";
import { User } from "./userService";

export interface Feedback {
  id: number;
  user: User;
  rating: number;
  text: string;
  created_at: string;
}

export interface CreateFeedbackData {
  rating: number;
  text: string;
}

export const feedbackService = {
  getCourseFeedbacks: async (courseId: number): Promise<Feedback[]> => {
    const response = await api.get<ListResponse<Feedback>>(`/courses/${courseId}/feedbacks/`);
    return response.data.results;
  },

  createFeedback: async (courseId: number, data: CreateFeedbackData): Promise<Feedback> => {
    const response = await api.post<Feedback>(`/courses/${courseId}/feedbacks/`, data);
    return response.data;
  },

  updateFeedback: async (
    courseId: number,
    feedbackId: number,
    data: CreateFeedbackData
  ): Promise<Feedback> => {
    const response = await api.patch<Feedback>(
      `/courses/${courseId}/feedbacks/${feedbackId}/`,
      data
    );
    return response.data;
  },

  deleteFeedback: async (courseId: number, feedbackId: number): Promise<void> => {
    await api.delete(`/courses/${courseId}/feedbacks/${feedbackId}/`);
  },
};
