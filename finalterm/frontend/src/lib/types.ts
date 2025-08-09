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
};
