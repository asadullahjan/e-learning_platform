import { ListResponse } from "@/lib/types";
import api from "./api";

export interface Notification {
  id: number;
  title: string;
  message: string;
  action_url: string;
  is_read: boolean;
  created_at: string;
}

export const notificationService = {
  getNotifications: async (page: number = 1): Promise<ListResponse<Notification>> => {
    const response = await api.get<ListResponse<Notification>>("/notifications/", {
      params: { page },
    });
    return response.data;
  },

  markAsRead: async (notificationId: number): Promise<void> => {
    await api.patch(`/notifications/${notificationId}/mark_as_read/`);
  },

  markAllAsRead: async (): Promise<void> => {
    await api.patch("/notifications/mark_all_as_read/");
  },

  server: {
    getNotifications: async (page: number = 1): Promise<ListResponse<Notification>> => {
      const { createServerApi } = await import("./api");
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Notification>>("/notifications/", {
        params: { page },
      });
      return response.data;
    },
  },
};
