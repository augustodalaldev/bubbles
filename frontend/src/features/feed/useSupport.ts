import { useState } from "react";
import { supportBubblegram } from "@/services/content";
import { errorMessage, toApiError } from "@/services/errors";
import { useAuthStore } from "@/features/auth/authStore";

/**
 * Supporting costs soap, so the count and the balance always come from the server:
 * nothing is incremented optimistically.
 */
export function useSupportBubblegram(
  postId: number,
  initialCount: number,
  onCount?: (count: number) => void
) {
  const [count, setCount] = useState(initialCount);
  const [supported, setSupported] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const support = async () => {
    if (busy || supported) return;
    setBusy(true);
    setError(null);
    try {
      const result = await supportBubblegram(postId);
      setCount(result.soap_count);
      setSupported(true);
      onCount?.(result.soap_count);
      await refreshUser();
    } catch (err) {
      if (toApiError(err).code === "already_supported") setSupported(true);
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return { count, supported, busy, error, support };
}
