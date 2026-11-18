import { useEffect } from "react";
import { AppRoutes } from "@/AppRoutes";
import { LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { useHeartbeat } from "@/features/auth/useHeartbeat";

export default function App() {
  const status = useAuthStore((s) => s.status);
  const bootstrap = useAuthStore((s) => s.bootstrap);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  useHeartbeat(status === "authenticated");

  // Wait for the session check before routing, so a reload keeps the current URL.
  if (status === "loading") {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <LoadingState label="Entrando..." />
      </div>
    );
  }

  return <AppRoutes />;
}
