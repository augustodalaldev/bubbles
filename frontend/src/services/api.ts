import axios from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request interceptor to attach JWT access token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("bubbles_access_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to auto-refresh expired JWT tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      originalRequest._retry = true;
      try {
        const refreshResponse = await axios.post(
          "/api/v1/auth/refresh/",
          {},
          { withCredentials: true }
        );
        const newAccess = refreshResponse.data?.access;
        if (newAccess) {
          localStorage.setItem("bubbles_access_token", newAccess);
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return api(originalRequest);
        }
      } catch (refreshErr) {
        localStorage.removeItem("bubbles_access_token");
        // Optional: redirect to login or trigger auth store reset
      }
    }
    return Promise.reject(error);
  }
);
