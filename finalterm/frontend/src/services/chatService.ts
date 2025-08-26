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

export interface DirectChatResponse {
  chat_room: Chat;
  created: boolean;
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

  getMessages: async (id: string, page: number = 1): Promise<ListResponse<Message>> => {
    const response = await api.get<ListResponse<Message>>(`/chats/${id}/messages/`, {
      params: { page },
    });
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

  findOrCreateDirectChat: async (otherUsername: string): Promise<DirectChatResponse> => {
    const response = await api.post<DirectChatResponse>("/chats/find_or_create_direct/", {
      username: otherUsername,
    });
    return response.data;
  },

  addUserToChat: async (chatId: string, username: string) => {
    const response = await api.post(`/chats/${chatId}/participants/`, {
      username,
    });
    return response.data;
  },

  getChatParticipants: async (chatId: string) => {
    const response = await api.get(`/chats/${chatId}/participants/`);
    return response.data;
  },

  getDirectChats: async (): Promise<Chat[]> => {
    const response = await api.get<{ results: Chat[] }>("/chats/", {
      params: { chat_type: "direct" },
    });
    return response.data.results;
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
    getMessages: async (id: string, page: number = 1) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Message>>(`/chats/${id}/messages/`, {
        params: { page },
      });
      return response.data;
    },
    deactivateChat: async (id: string) => {
      const serverApi = await createServerApi();
      const response = await serverApi.post(`/chats/${id}/participants/deactivate/`);
      return response.data;
    },
  },
};
