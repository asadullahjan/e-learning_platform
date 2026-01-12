import api from "./api";
import { User } from "./userService";

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  role: "student" | "teacher";
}

export interface AuthResponse {
  message: string;
  user: User;
}

class AuthService {
  async login(data: LoginData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/login/", data);
    return response.data;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/auth/register/", data);
    return response.data;
  }

  async logout(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>("/auth/logout/");
    return response.data;
  }
}

export const authService = new AuthService();
