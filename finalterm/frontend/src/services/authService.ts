import api from "./api";

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

export interface User {
  id: number;
  username?: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: "student" | "teacher";
  profile_picture?: string;
  created_at: string;
}

export interface AuthResponse {
  message: string;
  user: User;
}

export interface ProfileUpdateData {
  username?: string;
  first_name?: string;
  last_name?: string;
  profile_picture?: File;
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

  async getProfile(): Promise<User> {
    const response = await api.get<User>("/auth/profile/");
    return response.data;
  }

  async updateProfile(data: FormData): Promise<AuthResponse> {
    const response = await api.put<AuthResponse>("/auth/profile/update/", data);
    return response.data;
  }

  // Additional methods for better auth management
  async refreshToken(): Promise<{ access: string }> {
    const response = await api.post<{ access: string }>("/auth/refresh/");
    return response.data;
  }

  async changePassword(data: {
    old_password: string;
    new_password: string;
  }): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>("/auth/change-password/", data);
    return response.data;
  }

  async resetPassword(email: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>("/auth/reset-password/", { email });
    return response.data;
  }

  async verifyEmail(token: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>("/auth/verify-email/", { token });
    return response.data;
  }
}

export const authService = new AuthService();
