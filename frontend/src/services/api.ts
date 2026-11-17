import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

/**
 * The access token lives only in memory (docs/DECISIONS.md): an XSS cannot read it from
 * storage. After a page reload the session is recovered through the httpOnly refresh cookie.
 */
let accessToken: string | null = null;
let onSessionExpired: (() => void) | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
};
export const getAccessToken = () => accessToken;
export const setSessionExpiredHandler = (handler: (() => void) | null) => {
  onSessionExpired = handler;
};

export const api = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
});

const isAuthUrl = (url?: string) => !!url && url.startsWith("/auth/");

api.interceptors.request.use((config) => {
  // Auth endpoints must not receive a (possibly expired) Bearer header.
  if (accessToken && !isAuthUrl(config.url)) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

/** Single-flight refresh: concurrent callers share one request, so the rotating cookie is used once. */
export function refreshAccessToken(): Promise<string | null> {
  if (!refreshing) {
    refreshing = axios
      .post<{ access: string }>("/api/v1/auth/refresh/", {}, { withCredentials: true })
      .then((response) => {
        accessToken = response.data.access;
        return accessToken;
      })
      .catch(() => {
        accessToken = null;
        return null;
      })
      .finally(() => {
        refreshing = null;
      });
  }
  return refreshing;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    if (error.response?.status === 401 && original && !original._retried && !isAuthUrl(original.url)) {
      original._retried = true;
      const token = await refreshAccessToken();
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
      onSessionExpired?.();
    }
    return Promise.reject(error);
  }
);
