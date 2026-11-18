import type { User } from "@/types";
import { api, setAccessToken } from "./api";

interface AuthResponse {
  access: string;
  user: User;
}

export interface RegisterPayload {
  name: string;
  username: string;
  email: string;
  birth_date: string;
  password: string;
  description?: string;
}

export async function login(identifier: string, password: string): Promise<User> {
  const { data } = await api.post<AuthResponse>("/auth/login/", { identifier, password });
  setAccessToken(data.access);
  return data.user;
}

export async function register(payload: RegisterPayload): Promise<User> {
  const { data } = await api.post<AuthResponse>("/auth/register/", payload);
  setAccessToken(data.access);
  return data.user;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout/");
  } finally {
    setAccessToken(null);
  }
}

export async function sendHeartbeat(): Promise<void> {
  await api.post("/auth/heartbeat/");
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/users/me/");
  return data;
}
