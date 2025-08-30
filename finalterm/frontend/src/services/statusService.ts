import api, { createServerApi } from "./api";
import { User } from "./userService";

export interface Status {
  id: string;
  user: User;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CreateStatusData {
  content: string;
}

export interface StatusListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Status[];
}

export const statusService = {
  // Get all statuses (for home page)
  getStatuses: async (searchParams?: {
    [key: string]: string | string[] | undefined;
  }): Promise<StatusListResponse> => {
    const response = await api.get<StatusListResponse>("/statuses/", { params: searchParams });
    return response.data;
  },

  // Get statuses for a specific user
  getUserStatuses: async (userId: string): Promise<StatusListResponse> => {
    const response = await api.get<StatusListResponse>("/statuses/", {
      params: { user: userId },
    });
    return response.data;
  },

  // Create a new status
  createStatus: async (status: CreateStatusData): Promise<Status> => {
    const response = await api.post<Status>("/statuses/", status);
    return response.data;
  },

  // Update a status
  updateStatus: async (statusId: string, status: Partial<CreateStatusData>): Promise<Status> => {
    const response = await api.patch<Status>(`/statuses/${statusId}/`, status);
    return response.data;
  },

  // Delete a status
  deleteStatus: async (statusId: string): Promise<void> => {
    await api.delete(`/statuses/${statusId}/`);
  },

  // Server-side methods (GET operations only)
  server: {
    getStatuses: async (searchParams?: {
      [key: string]: string | string[] | undefined;
    }): Promise<StatusListResponse> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<StatusListResponse>("/statuses/", { params: searchParams });
      return response.data;
    },

    getUserStatuses: async (userId: string): Promise<StatusListResponse> => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<StatusListResponse>("/statuses/", {
        params: { user: userId },
      });
      return response.data;
    },
  },
};
