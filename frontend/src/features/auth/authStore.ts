import { create } from "zustand";
import type { EconomySettings, User } from "@/types";
import { refreshAccessToken, setSessionExpiredHandler } from "@/services/api";
import * as authApi from "@/services/auth";
import { getEconomySettings } from "@/services/economy";

type SessionStatus = "loading" | "authenticated" | "anonymous";

interface AuthState {
  status: SessionStatus;
  user: User | null;
  economy: EconomySettings | null;
  /** Recovers the session on page load through the httpOnly refresh cookie. */
  bootstrap: () => Promise<void>;
  login: (identifier: string, password: string) => Promise<void>;
  register: (payload: authApi.RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  /** Re-reads /users/me/ (e.g. to refresh the soap balance after spending). */
  refreshUser: () => Promise<void>;
}

async function loadEconomy(): Promise<EconomySettings | null> {
  try {
    return await getEconomySettings();
  } catch {
    return null; // Not critical: the UI falls back to not showing rates.
  }
}

export const useAuthStore = create<AuthState>((set) => {
  setSessionExpiredHandler(() => set({ status: "anonymous", user: null }));

  return {
    status: "loading",
    user: null,
    economy: null,

    bootstrap: async () => {
      const token = await refreshAccessToken();
      if (!token) {
        set({ status: "anonymous", user: null });
        return;
      }
      try {
        const [user, economy] = await Promise.all([authApi.fetchCurrentUser(), loadEconomy()]);
        set({ status: "authenticated", user, economy });
      } catch {
        set({ status: "anonymous", user: null });
      }
    },

    login: async (identifier, password) => {
      const user = await authApi.login(identifier, password);
      set({ status: "authenticated", user, economy: await loadEconomy() });
    },

    register: async (payload) => {
      const user = await authApi.register(payload);
      set({ status: "authenticated", user, economy: await loadEconomy() });
    },

    logout: async () => {
      try {
        await authApi.logout();
      } finally {
        set({ status: "anonymous", user: null });
      }
    },

    refreshUser: async () => {
      try {
        set({ user: await authApi.fetchCurrentUser() });
      } catch {
        // Keep the stale user; a 401 is handled by the session-expired handler.
      }
    },
  };
});
