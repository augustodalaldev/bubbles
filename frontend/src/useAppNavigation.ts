import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/features/auth/authStore";
import { paths, viewPath } from "@/routes";

/** Navigation helpers shared by the route components (views keep their callback props). */
export function useAppNavigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const ownUsername = useAuthStore((s) => s.user?.username);

  return useMemo(
    () => ({
      goHome: () => navigate(paths.home),
      goTo: (view: string) => navigate(viewPath(view, ownUsername)),
      goToOwnProfile: () => navigate(viewPath("profile", ownUsername)),
      openProfile: (username: string) => navigate(paths.profile(username)),
      openCommunity: (community: { commname: string }) => navigate(paths.community(community.commname)),
      writeLetter: (username: string) => navigate(paths.lettersTo(username)),
      /** Typing in the header search box: replace the entry while already on the feed. */
      search: (term: string) => navigate(paths.search(term), { replace: location.pathname === "/" }),
    }),
    [navigate, location.pathname, ownUsername]
  );
}
