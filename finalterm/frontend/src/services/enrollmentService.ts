import api, { createServerApi } from "./api";

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  profile_picture?: string;
}

export interface Course {
  id: string;
  title: string;
  description: string;
  teacher: User;
  published_at?: string;
}

export interface Enrollment {
  id: string;
  enrolled_at: string;
  is_active: boolean;
  unenrolled_at?: string;
}

// When courseId is present (teacher view) - returns user data, no course data
export interface TeacherEnrollment extends Enrollment {
  user: User;
}

// When courseId is NOT present (student view) - returns course data, no user data
export interface StudentEnrollment extends Enrollment {
  course: Course;
}

export interface EnrollmentListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: TeacherEnrollment[] | StudentEnrollment[];
}

export const enrollmentService = {
  // For teachers viewing enrollments in their course (returns user data)
  getCourseEnrollments: async (
    courseId: string, 
    filters?: {
      search?: string;
      status?: "all" | "active" | "inactive";
    }
  ): Promise<TeacherEnrollment[]> => {
    const params: any = { course: courseId };
    
    if (filters?.search) {
      params.search = filters.search;
    }
    
    if (filters?.status && filters.status !== "all") {
      params.is_active = filters.status === "active";
    }
    
    const response = await api.get<EnrollmentListResponse>("/enrollments", { params });
    return response.data.results as TeacherEnrollment[];
  },

  // For students viewing their own enrollments (returns course data)
  getUserEnrollments: async (): Promise<StudentEnrollment[]> => {
    const response = await api.get<EnrollmentListResponse>("/enrollments");
    return response.data.results as StudentEnrollment[];
  },

  // Generic method that automatically determines the right endpoint
  getEnrollments: async (courseId?: string): Promise<TeacherEnrollment[] | StudentEnrollment[]> => {
    if (courseId) {
      return enrollmentService.getCourseEnrollments(courseId);
    } else {
      return enrollmentService.getUserEnrollments();
    }
  },

  getEnrollment: async (enrollmentId: string): Promise<Enrollment> => {
    const response = await api.get<Enrollment>(`/enrollments/${enrollmentId}/`);
    return response.data;
  },

  createEnrollment: async (courseId: string): Promise<Enrollment> => {
    const response = await api.post<Enrollment>("/enrollments/", { course: courseId });
    return response.data;
  },

  updateEnrollment: async (
    enrollmentId: string,
    data: Partial<Enrollment>
  ): Promise<Enrollment> => {
    const response = await api.patch<Enrollment>(`/enrollments/${enrollmentId}/`, data);
    return response.data;
  },

  deleteEnrollment: async (enrollmentId: string): Promise<void> => {
    await api.delete(`/enrollments/${enrollmentId}/`);
  },

  // Additional methods for better enrollment management
  activateEnrollment: async (enrollmentId: string): Promise<Enrollment> => {
    return enrollmentService.updateEnrollment(enrollmentId, { is_active: true });
  },

  deactivateEnrollment: async (enrollmentId: string): Promise<Enrollment> => {
    return enrollmentService.updateEnrollment(enrollmentId, { is_active: false });
  },

  // Server-side methods (GET operations only)
  server: {
    getCourseEnrollments: async (
      courseId: string,
      filters?: {
        search?: string;
        status?: "all" | "active" | "inactive";
      }
    ): Promise<TeacherEnrollment[]> => {
      const serverApi = await createServerApi();
      const params: any = { course: courseId };
      
      if (filters?.search) {
        params.search = filters.search;
      }
      
      if (filters?.status && filters.status !== "all") {
        params.is_active = filters.status === "active";
      }
      
      const response = await serverApi.get<EnrollmentListResponse>("/enrollments", { params });
      return response.data.results as TeacherEnrollment[];
    },

    getUserEnrollments: async (): Promise<StudentEnrollment[]> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<EnrollmentListResponse>("/enrollments");
      return response.data.results as StudentEnrollment[];
    },
  },
};
