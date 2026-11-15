import { create } from "zustand";
import { User } from "@/types";
import { api } from "@/services/api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  fetchCurrentUser: () => Promise<void>;
  sendHeartbeat: () => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem("bubbles_access_token"),
  isLoading: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  fetchCurrentUser: async () => {
    try {
      set({ isLoading: true });
      const res = await api.get("/users/me/");
      set({ user: res.data, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  sendHeartbeat: async () => {
    try {
      const res = await api.post("/auth/heartbeat/");
      if (res.data?.last_seen_at) {
        set((state) => ({
          user: state.user ? { ...state.user, last_seen_at: res.data.last_seen_at } : null,
        }));
      }
    } catch {
      // Silently fail on network jitter
    }
  },

  logout: () => {
    localStorage.removeItem("bubbles_access_token");
    set({ user: null, isAuthenticated: false });
  },
}));
