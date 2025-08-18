import { User } from "@/services/authService";

export type ListResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Course = {
  id: string;
  title: string;
  description: string;
  teacher: User;
  created_at: string;
  updated_at: string;
  published_at: string;
  enrollment_count: number;
  total_enrollments: number;
  is_enrolled: boolean;
  can_enroll: boolean;
  course_chat_id?: string; // ID of the course chat if it exists
};

export type Enrollment = {
  id: string;
  course: Course;
  user: User;
  is_active: boolean;
  enrolled_at: string;
  unenrolled_at: string | null;
};
