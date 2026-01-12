import api, { createServerApi } from "./api";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: "student" | "teacher";
  profile_picture: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ProfileUpdateData {
  username?: string;
  first_name?: string;
  last_name?: string;
  profile_picture?: File;
}

export const userService = {
  // User listing and search
  listUsers: async (): Promise<User[]> => {
    const response = await api.get<{ results: User[] }>("/users/");
    return response.data.results;
  },

  searchUsers: async (query: string): Promise<User[]> => {
    // Use the ModelViewSet search functionality
    const response = await api.get<{ results: User[] }>("/users/", {
      params: { search: query },
    });
    return response.data.results;
  },

  // User retrieval
  getUserByUsername: async (username: string): Promise<User> => {
    const response = await api.get<User>(`/users/${username}/`);
    return response.data;
  },

  getUserById: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}/`);
    return response.data;
  },

  // User updates
  updateUser: async (id: number, userData: Partial<User>): Promise<User> => {
    const response = await api.patch<User>(`/users/${id}/`, userData);
    return response.data;
  },

  // Current user operations
  getCurrentUserProfile: async (): Promise<User> => {
    const response = await api.get<User>("/users/me/");
    return response.data;
  },

  // Update current user profile - requires userId (should come from auth store)
  updateCurrentUserProfile: async (userId: number, userData: Partial<User>): Promise<User> => {
    const response = await api.patch<User>(`/users/${userId}/`, userData);
    return response.data;
  },

  // Convenience method for profile updates with FormData
  updateProfile: async (userId: number, data: FormData): Promise<User> => {
    const response = await api.patch<User>(`/users/${userId}/`, data);
    return response.data;
  },

  server: {
    getUserByUsername: async (username: string): Promise<User> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<User>(`/users/${username}/`);
      return response.data;
    },
  },
};
