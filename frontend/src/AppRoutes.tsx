import { Suspense, lazy, useEffect, useState } from "react";
import {
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { Header } from "@/components/Header";
import { NotFoundView } from "@/components/NotFoundView";
import { ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { PostDetailModal } from "@/features/profile/PostDetailModal";
import { getBubblegram } from "@/services/content";
import { errorMessage, toApiError } from "@/services/errors";
import { authPath, paths, safeNext, viewFromPath } from "@/routes";
import type { Bubblegram } from "@/types";

// Each screen is its own chunk: the first page only downloads what it shows.
const LoginView = lazy(() => import("@/features/auth/LoginView").then((m) => ({ default: m.LoginView })));
const RegisterView = lazy(() => import("@/features/auth/RegisterView").then((m) => ({ default: m.RegisterView })));
const FeedView = lazy(() => import("@/features/feed/FeedView").then((m) => ({ default: m.FeedView })));
const ProfileView = lazy(() => import("@/features/profile/ProfileView").then((m) => ({ default: m.ProfileView })));
const CommunityListView = lazy(() =>
  import("@/features/communities/CommunityListView").then((m) => ({ default: m.CommunityListView }))
);
const CommunityDetailView = lazy(() =>
  import("@/features/communities/CommunityDetailView").then((m) => ({ default: m.CommunityDetailView }))
);
const FollowListView = lazy(() =>
  import("@/features/profile/FollowListView").then((m) => ({ default: m.FollowListView }))
);
const StoreView = lazy(() => import("@/features/customization/StoreView").then((m) => ({ default: m.StoreView })));
const LettersInboxView = lazy(() =>
  import("@/features/letters/LettersInboxView").then((m) => ({ default: m.LettersInboxView }))
);

/** Routes that need a session. Anonymous visitors go to /login and come back to the URL they wanted. */
function RequireAuth() {
  const status = useAuthStore((s) => s.status);
  const sessionEnded = useAuthStore((s) => s.sessionEnded);
  const location = useLocation();
  if (status !== "authenticated") {
    // After an explicit logout there is no page to return to; after an expiry there is.
    const target = sessionEnded === "logout" ? paths.login : authPath(paths.login, location);
    return <Navigate to={target} replace />;
  }
  return <Outlet />;
}

/** Login/register: signed-in users have nothing to do there, so send them where they were headed. */
function PublicOnly() {
  const status = useAuthStore((s) => s.status);
  const [params] = useSearchParams();
  if (status === "authenticated") return <Navigate to={safeNext(params.get("next"))} replace />;
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 font-sans">
      <Outlet />
    </div>
  );
}

function AppLayout() {
  const user = useAuthStore((s) => s.user)!;
  const location = useLocation();
  const view = viewFromPath(location.pathname, user.username);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col justify-between font-sans">
      <div>
        <Header />
        <Suspense fallback={<LoadingState />}>
          <Outlet />
        </Suspense>
      </div>

      {view === "profile" || view === "communities" ? (
        <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-200 mt-8">
          Bubbles • Rede Social
        </footer>
      ) : null}
    </div>
  );
}

function FeedRoute() {
  const [params] = useSearchParams();
  return <FeedView searchTerm={params.get("q") ?? ""} />;
}

function ProfileRoute() {
  const { username = "" } = useParams();
  const handle = username.toLowerCase();
  return <ProfileView key={handle} username={handle} />;
}

function FollowRoute({ kind }: { kind: "followers" | "following" }) {
  const { username = "" } = useParams();
  const handle = username.toLowerCase();
  return <FollowListView key={`${kind}:${handle}`} username={handle} kind={kind} />;
}

function CommunityRoute() {
  const { commname = "" } = useParams();
  const handle = commname.toLowerCase();
  return <CommunityDetailView key={handle} commname={handle} />;
}

function LettersRoute() {
  const [params] = useSearchParams();
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const letterId = id === undefined ? null : Number(id);
  return (
    <LettersInboxView
      composeTo={params.get("to")}
      openLetterId={letterId !== null && Number.isInteger(letterId) && letterId > 0 ? letterId : null}
      invalidLetterId={id !== undefined && !(letterId !== null && Number.isInteger(letterId) && letterId > 0)}
      onOpenLetter={(letterId) => navigate(paths.letter(letterId))}
      // Back to wherever the person came from; a direct visit goes to the list.
      onCloseLetter={() =>
        location.key !== "default" ? navigate(-1) : navigate(paths.letters, { replace: true })
      }
      // The composer was opened by `?to=`: drop it so reloading does not reopen it.
      onComposeClosed={() => navigate(paths.letters, { replace: true })}
    />
  );
}

/** Deep link to a post: the same detail modal the feed opens, but addressable. */
function PostRoute() {
  const { id = "" } = useParams();
  const postId = Number(id);
  const navigate = useNavigate();
  const location = useLocation();
  const [post, setPost] = useState<Bubblegram | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "notfound" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const valid = Number.isInteger(postId) && postId > 0;

  useEffect(() => {
    if (!valid) return;
    setStatus("loading");
    getBubblegram(postId)
      .then((data) => {
        setPost(data);
        setStatus("ready");
      })
      .catch((err) => {
        if (toApiError(err).status === 404) setStatus("notfound");
        else {
          setError(errorMessage(err));
          setStatus("error");
        }
      });
  }, [postId, valid]);

  // Back to wherever the person came from; a direct visit goes to the feed.
  const close = () => (location.key !== "default" ? navigate(-1) : navigate(paths.home, { replace: true }));

  if (!valid || status === "notfound") return <NotFoundView message="Esta publicação não existe ou foi excluída." />;
  if (status === "loading") return <LoadingState label="Carregando publicação..." />;
  if (status === "error" || !post) {
    return <ErrorState message={error ?? "Não foi possível carregar a publicação."} />;
  }
  return (
    <PostDetailModal
      post={post}
      story={null}
      onClose={close}
      onPostUpdate={setPost}
      onPostDeleted={() => navigate(paths.home, { replace: true })}
    />
  );
}

export function AppRoutes() {
  return (
    <Suspense fallback={<LoadingState />}>
      <Routes>
        <Route element={<PublicOnly />}>
          <Route path={paths.login} element={<LoginView />} />
          <Route path={paths.register} element={<RegisterView />} />
        </Route>

        <Route element={<RequireAuth />}>
          <Route element={<AppLayout />}>
            <Route index element={<FeedRoute />} />
            <Route path="u/:username" element={<ProfileRoute />} />
            <Route path="u/:username/followers" element={<FollowRoute kind="followers" />} />
            <Route path="u/:username/following" element={<FollowRoute kind="following" />} />
            <Route path="communities" element={<CommunityListView />} />
            <Route path="c/:commname" element={<CommunityRoute />} />
            <Route path="store" element={<StoreView />} />
            <Route path="letters/:id?" element={<LettersRoute />} />
            <Route path="p/:id" element={<PostRoute />} />
            <Route path="*" element={<NotFoundView />} />
          </Route>
        </Route>
      </Routes>
    </Suspense>
  );
}
