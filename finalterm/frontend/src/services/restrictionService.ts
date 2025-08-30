import { Course, ListResponse } from "@/lib/types";
import api, { createServerApi } from "./api";
import { User } from "./userService";

export interface StudentRestriction {
  id: string;
  student: User;
  course: Course;
  teacher: User;
  reason: string;
  created_at: string;
}

export interface CreateRestrictionData {
  student: number;
  course?: number;
  reason: string;
}

export interface RestrictionCheckResponse {
  is_restricted: boolean;
  reason?: string;
}

export const restrictionService = {
  getRestrictions: async ({
    courseId,
  }: {
    courseId?: string;
  }): Promise<ListResponse<StudentRestriction>> => {
    const response = await api.get<ListResponse<StudentRestriction>>("/restrictions/", {
      params: {
        course: courseId,
      },
    });
    return response.data;
  },

  createRestriction: async (data: CreateRestrictionData): Promise<StudentRestriction> => {
    const response = await api.post<StudentRestriction>("/restrictions/", data);
    return response.data;
  },

  deleteRestriction: async (restrictionId: string): Promise<void> => {
    await api.delete(`/restrictions/${restrictionId}/`);
  },

  server: {
    checkStudentRestriction: async (courseId: number): Promise<RestrictionCheckResponse> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<RestrictionCheckResponse>(
        "/restrictions/check_student/",
        {
          params: {
            course_id: courseId,
          },
        }
      );
      return response.data;
    },
  },
};
