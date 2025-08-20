import api, { createServerApi } from "./api";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  profile_picture?: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export const userService = {
  getUserByUsername: async (username: string): Promise<User> => {
    const response = await api.get<User>(`/users/${username}/`);
    return response.data;
  },

  searchUsers: async (query: string): Promise<User[]> => {
    const response = await api.get<{ results: User[] }>("/users/search/", {
      params: { q: query },
    });
    return response.data.results;
  },

  server: {
    getUserByUsername: async (username: string): Promise<User> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<User>(`/users/${username}/`);
      return response.data;
    },
  },
};
