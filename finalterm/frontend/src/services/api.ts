import axios from "axios";
import Cookies from "js-cookie";

const API_BASE_URL = `${process.env.NEXT_PUBLIC_SERVER_URL}/api/`;

// Check environment once
const getIsServer = () => typeof window === "undefined";

// Client-side cookie parsing
const getClientCookie = (name: string) => {
  const cookie = Cookies.get(name);
  return cookie;
};

// Track if cookies have been initialized
let cookiesInitialized = false;
let initializationPromise: Promise<void> | null = null;

// Function to initialize cookies by making a simple GET request
const initializeCookies = async (): Promise<void> => {
  if (getIsServer()) return;

  try {
    console.log("Initializing cookies...");

    // Make a simple GET request to set cookies
    const response = await axios.get(`${API_BASE_URL}auth/csrf_token/`, {
      withCredentials: true,
      headers: {
        Accept: "application/json",
      },
    });

    console.log("Cookie initialization response:", response.status);

    // Wait a bit for cookies to be set
    await new Promise((resolve) => setTimeout(resolve, 100));

    const csrfToken = getClientCookie("csrftoken");
    const sessionId = getClientCookie("sessionid");

    console.log("After initialization - CSRF:", !!csrfToken, "Session:", !!sessionId);

    cookiesInitialized = true;
  } catch (error) {
    console.error("Failed to initialize cookies:", error);
    // Don't throw here, let requests proceed even if initialization fails
    cookiesInitialized = true;
  }
};

// Ensure cookies are initialized before making requests
const ensureCookies = async (): Promise<void> => {
  if (getIsServer()) return;

  if (cookiesInitialized) return;

  // Check if cookies already exist
  if (getClientCookie("csrftoken") && getClientCookie("sessionid")) {
    cookiesInitialized = true;
    return;
  }

  // Initialize cookies if they don't exist
  if (!initializationPromise) {
    initializationPromise = initializeCookies();
  }

  await initializationPromise;
};

// Create the API instance
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: !getIsServer(), // Only on client-side
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Request interceptor
api.interceptors.request.use(
  async (config) => {
    try {
      if (!getIsServer()) {
        // Ensure cookies are set before making any request
        await ensureCookies();

        // Client-side: Add CSRF token for unsafe methods
        if (["post", "put", "patch", "delete"].includes(config.method?.toLowerCase() || "")) {
          const csrfToken = getClientCookie("csrftoken");
          if (csrfToken) {
            config.headers["X-CSRFToken"] = csrfToken;
          } else {
            console.warn("CSRF token not found after initialization");
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
  async (error) => {
    if (error.response?.status === 401) {
      console.log("Unauthorized access");
    } else if (error.response?.status === 403) {
      const detail = error.response?.data?.detail;
      if (detail && detail.includes("CSRF")) {
        console.error("CSRF Error:", detail);
        console.log("Current CSRF token:", getClientCookie("csrftoken"));

        // Reset initialization and try again
        cookiesInitialized = false;
        initializationPromise = null;
      } else {
        console.log("Forbidden: Insufficient permissions");
      }
    } else if (error.code === "ECONNABORTED") {
      console.log("Request timeout");
    } else if (!error.response) {
      console.log("Network error");
    }

    return Promise.reject(error);
  }
);

// Server-side helper function
export const createServerApi = async () => {
  if (!getIsServer()) {
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
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
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

// Export the initialization function for manual use
export const initializeAppCookies = async (): Promise<void> => {
  await ensureCookies();
};

// Helper functions for debugging and checking cookie status
export const hasCSRFToken = (): boolean => {
  return getClientCookie("csrftoken") !== null;
};

export const hasSessionId = (): boolean => {
  return getClientCookie("sessionid") !== null;
};

export const debugCookies = () => {
  if (getIsServer()) {
    console.log("Cannot debug cookies on server side");
    return;
  }

  console.log("=== Cookie Debug ===");
  console.log("CSRF Token:", getClientCookie("csrftoken"));
  console.log("Session ID:", getClientCookie("sessionid"));
  console.log("All cookies:", document.cookie);
  console.log("Cookies initialized:", cookiesInitialized);
};

// Reset cookie initialization (useful for testing)
export const resetCookieInitialization = () => {
  cookiesInitialized = false;
  initializationPromise = null;
};

// Check if cookies are already initialized
export const areCookiesInitialized = (): boolean => {
  return cookiesInitialized;
};

export default api;

// Auto-initialize cookies when module loads (browser only)
if (typeof window !== "undefined") {
  // Small delay to ensure DOM is ready
  setTimeout(() => {
    initializeAppCookies().catch(() => {
      // Silent fail for auto-initialization
      console.log("Auto cookie initialization completed");
    });
  }, 100);
}
