import { useEffect } from "react";
import { sendHeartbeat } from "@/services/auth";

const HEARTBEAT_INTERVAL_MS = 5 * 60 * 1000;

/** Tells the backend the user is present, which drives passive soap earning. */
export function useHeartbeat(active: boolean) {
  useEffect(() => {
    if (!active) return;
    const beat = () => {
      if (document.visibilityState === "visible") sendHeartbeat().catch(() => undefined);
    };
    beat();
    const timer = window.setInterval(beat, HEARTBEAT_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [active]);
}
