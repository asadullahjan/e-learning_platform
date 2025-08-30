import { Course, ListResponse } from "@/lib/types";
import api from "./api";
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
  student_id: number;
  course_id?: number;
  is_restricted: boolean;
}

export const restrictionService = {
  getRestrictions: async (): Promise<StudentRestriction[]> => {
    const response = await api.get<ListResponse<StudentRestriction>>("/restrictions/");
    return response.data.results;
  },

  createRestriction: async (data: CreateRestrictionData): Promise<StudentRestriction> => {
    const response = await api.post<StudentRestriction>("/restrictions/", data);
    return response.data;
  },

  deleteRestriction: async (restrictionId: string): Promise<void> => {
    await api.delete(`/restrictions/${restrictionId}/`);
  },

  checkStudentRestriction: async (
    studentId: number,
    courseId?: number
  ): Promise<RestrictionCheckResponse> => {
    const params: any = { student_id: studentId };
    if (courseId) {
      params.course_id = courseId;
    }

    const response = await api.get<RestrictionCheckResponse>("/restrictions/check_student/", {
      params,
    });
    return response.data;
  },
};
