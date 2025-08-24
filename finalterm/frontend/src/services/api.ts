import axios from "axios";

const API_BASE_URL = `${process.env.NEXT_PUBLIC_SERVER_URL}/api/`;

// Check environment once
const isServer = typeof window === "undefined";

// Client-side cookie parsing
const getClientCookie = (name: string) => {
  if (isServer || !document.cookie) return null;

  try {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const [cookieName, cookieValue] = cookie.trim().split("=");
      if (cookieName === name) {
        return decodeURIComponent(cookieValue);
      }
    }
  } catch (error) {
    console.error(`Error parsing cookie ${name}:`, error);
  }
  return null;
};

// Create the API instance
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: !isServer, // Only on client-side
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    try {
      if (!isServer) {
        // Client-side: Add CSRF token for unsafe methods
        if (["post", "put", "patch", "delete"].includes(config.method?.toLowerCase() || "")) {
          const csrfToken = getClientCookie("csrftoken");
          if (csrfToken) {
            config.headers["X-CSRFToken"] = csrfToken;
          }
        }
      }
    } catch (error) {
      console.error("Request interceptor error:", error);
    }

    return config;
  },
  (error) => {
    console.error("Request interceptor setup error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.log("Unauthorized access");
    } else if (error.response?.status === 403) {
      console.log("Forbidden: Insufficient permissions");
    } else if (error.code === "ECONNABORTED") {
      console.log("Request timeout");
    } else if (!error.response) {
      console.log("Network error");
    }

    return Promise.reject(error);
  }
);

export default api;

// Server-side helper function
export const createServerApi = async () => {
  if (!isServer) {
    return api; // Return client instance if somehow called on client
  }

  try {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    const cookieString = cookieStore.toString();
    const csrfToken = cookieStore.get("csrftoken")?.value;

    // Create server API instance with cookies
    const serverApi = axios.create({
      baseURL: API_BASE_URL,
      withCredentials: false,
      timeout: 10000,
    });

    // Add cookies to all requests
    serverApi.interceptors.request.use((config) => {
      if (cookieString) {
        config.headers.Cookie = cookieString;
      }
      if (
        csrfToken &&
        ["post", "put", "patch", "delete"].includes(config.method?.toLowerCase() || "")
      ) {
        config.headers["X-CSRFToken"] = csrfToken;
      }
      return config;
    });

    return serverApi;
  } catch (error) {
    console.error("Error creating server API:", error);
    return api; // Fallback to basic instance
  }
};
