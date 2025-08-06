import axios from "axios";

const API_BASE_URL = `${process.env.NEXT_PUBLIC_URL}/api/`;

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Function to get CSRF token from cookies
const getCsrfToken = () => {
  const name = "csrftoken";
  let cookieValue = null;
  if (typeof document !== "undefined" && document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// Request interceptor to add CSRF token
api.interceptors.request.use((config) => {
  // Add CSRF token for unsafe methods
  if (["post", "put", "patch", "delete"].includes(config.method?.toLowerCase() || "")) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.log("Unauthorized access");
    }
    return Promise.reject(error);
  }
);

export default api;
