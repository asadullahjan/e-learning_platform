import api, { createServerApi } from "./api";
import { ListResponse } from "@/lib/types";
import { User } from "./userService";

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
  getChats: async (search?: string): Promise<ListResponse<Chat>> => {
    const response = await api.get<ListResponse<Chat>>("/chats/", {
      params: {
        search,
      },
    });
    return response.data;
  },

  getUserChats: async (): Promise<Chat[]> => {
    const response = await api.get("/chats/my_chats/");
    return response.data;
  },

  getChat: async (id: string): Promise<Chat> => {
    const response = await api.get(`/chats/${id}/`);
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
    participants?: number[]; // Array of user IDs for participants
  }): Promise<Chat> => {
    const response = await api.post("/chats/", data);
    return response.data;
  },

  createMessage: async ({ id, content }: { id: string; content: string }): Promise<Message> => {
    const response = await api.post(`/chats/${id}/messages/`, { content });
    return response.data;
  },

  joinChatRoom: async (id: string): Promise<Chat> => {
    const response = await api.post(`/chats/${id}/participants/`);
    return response.data;
  },

  findOrCreateDirectChat: async (otherUserId: number): Promise<Chat> => {
    const response = await api.post<Chat>("/chats/", {
      name: "Direct Chat",
      description: "Direct message conversation",
      chat_type: "direct",
      is_public: false,
      participants: [otherUserId],
    });
    return response.data;
  },

  addUserToChat: async (chatId: string, userId: number): Promise<Chat> => {
    const response = await api.post(`/chats/${chatId}/participants/`, {
      user: userId,
    });
    return response.data;
  },

  getChatParticipants: async (chatId: string): Promise<Chat> => {
    const response = await api.get(`/chats/${chatId}/participants/`);
    return response.data;
  },

  deactivateChat: async (chatId: string, userId?: number): Promise<Chat> => {
    const response = await api.post(
      `/chats/${chatId}/participants/deactivate/`,
      userId ? { user: userId } : {}
    );
    return response.data;
  },

  reactivateChat: async (chatId: string, userId?: number): Promise<Chat> => {
    const response = await api.post(
      `/chats/${chatId}/participants/reactivate/`,
      userId ? { user: userId } : {}
    );
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
    getMessages: async (id: string, page: number = 1) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Message>>(`/chats/${id}/messages/`, {
        params: { page },
      });
      return response.data;
    },
  },
};
