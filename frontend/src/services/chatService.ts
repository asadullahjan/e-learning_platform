import api, { createServerApi } from "./api";
import { ListResponse } from "@/lib/types";
import { User } from "./userService";

export interface Chat {
  id: number;
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

export interface ChatParticipant {
  id: number;
  user: User;
  role: string;
  is_active: boolean;
  joined_at: string;
}

export interface Message {
  id: number;
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

  getChat: async (id: number): Promise<Chat> => {
    const response = await api.get(`/chats/${id}/`);
    return response.data;
  },

  getMessages: async (id: number, page: number = 1): Promise<ListResponse<Message>> => {
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

  createMessage: async ({ id, content }: { id: number; content: string }): Promise<Message> => {
    const response = await api.post(`/chats/${id}/messages/`, { content });
    return response.data;
  },

  joinChatRoom: async (id: number): Promise<Chat> => {
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

  addUserToChat: async (chatId: number, userId: number): Promise<Chat> => {
    const response = await api.post(`/chats/${chatId}/participants/`, {
      user: userId,
    });
    return response.data;
  },

  getChatParticipants: async (chatId: number): Promise<ListResponse<ChatParticipant>> => {
    const response = await api.get(`/chats/${chatId}/participants/`);
    return response.data;
  },

  deactivateChat: async (chatId: number, userId?: number): Promise<Chat> => {
    const response = await api.post(
      `/chats/${chatId}/participants/deactivate/`,
      userId ? { user: userId } : {}
    );
    return response.data;
  },

  reactivateChat: async (chatId: number, userId?: number): Promise<Chat> => {
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
    getChat: async (id: number) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<Chat>(`/chats/${id}/`);
      return response.data;
    },
    getMessages: async (id: number, page: number = 1) => {
      const serverApi = await createServerApi();
      const response = await serverApi.get<ListResponse<Message>>(`/chats/${id}/messages/`, {
        params: { page },
      });
      return response.data;
    },
  },
};
