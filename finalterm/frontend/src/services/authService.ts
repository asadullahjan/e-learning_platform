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

class AuthService {
  async login(data: LoginData): Promise<AuthResponse> {
    const response = await api.post("/auth/login/", data);
    return response.data;
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post("/auth/register/", data);
    return response.data;
  }

  async logout(): Promise<{ message: string }> {
    const response = await api.post("/auth/logout/");
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await api.get("/auth/profile/");
    return response.data;
  }

  async updateProfile(data: FormData): Promise<AuthResponse> {
    const response = await api.put("/auth/profile/update/", data);
    return response.data;
  }
}

export const authService = new AuthService();
