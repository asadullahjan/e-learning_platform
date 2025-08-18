import api, { createServerApi } from "./api";
import { ListResponse } from "@/lib/types";
import { User } from "./authService";

export interface Chat {
  id: string;
  name: string;
  chat_type: "direct" | "group" | "course";
  description: string;
  created_at: string;
  is_public: boolean;
  course?: string; // Course ID for course chats
  current_user_status?: {
    is_participant: boolean;
    role: string | null;
  };
}

export interface Message {
  id: string;
  content: string;
  created_at: string;
  sender: User;
}

export const chatService = {
  getChats: async (search?: string) => {
    const response = await api.get("/chats/", {
      params: {
        search,
      },
    });
    return response.data;
  },

  getUserChats: async () => {
    const response = await api.get("/chats/my_chats/");
    return response.data;
  },

  getChat: async (id: string) => {
    const response = await api.get(`/chats/${id}/`);
    return response.data;
  },

  getCourseChat: async (courseId: string) => {
    const response = await api.get(`/chats/course/${courseId}/`);
    return response.data;
  },

  getMessages: async (id: string) => {
    const response = await api.get(`/chats/${id}/messages/`);
    return response.data;
  },

  createChat: async (data: {
    name: string;
    description: string;
    chat_type: string;
    is_public: boolean;
    course?: string; // Course ID for course chats
  }) => {
    const response = await api.post("/chats/", data);
    return response.data;
  },

  createMessage: async ({ id, content }: { id: string; content: string }) => {
    const response = await api.post(`/chats/${id}/messages/`, { content });
    return response.data;
  },

  joinChatRoom: async (id: string) => {
    const response = await api.post(`/chats/${id}/participants/`);
    return response.data;
  },

  server: {
    getChats: async () => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Chat>>("/chats/");
      return response.data.results as Chat[];
    },
    getUserChats: async () => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<Chat[]>("/chats/my_chats/");
      return response.data;
    },
    getChat: async (id: string) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<Chat>(`/chats/${id}/`);
      return response.data;
    },
    getCourseChat: async (courseId: string) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<Chat>(`/chats/course/${courseId}/`);
      return response.data;
    },
    getMessages: async (id: string) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Message>>(`/chats/${id}/messages/`);
      return response.data.results as Message[];
    },
  },
};
