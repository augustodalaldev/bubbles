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
import { useAuthStore } from "@/features/auth/authStore";
import { LoginView } from "@/features/auth/LoginView";
import { RegisterView } from "@/features/auth/RegisterView";
import { CommunityDetailView } from "@/features/communities/CommunityDetailView";
import { CommunityListView } from "@/features/communities/CommunityListView";
import { StoreView } from "@/features/customization/StoreView";
import { FeedView } from "@/features/feed/FeedView";
import { LettersInboxView } from "@/features/letters/LettersInboxView";
import { ProfileView } from "@/features/profile/ProfileView";
import { paths, viewFromPath } from "@/routes";

/** Routes that need a session. Anonymous visitors are sent to the login screen. */
function RequireAuth() {
  const status = useAuthStore((s) => s.status);
  if (status !== "authenticated") return <Navigate to={paths.login} replace />;
  return <Outlet />;
}

/** Login/register: signed-in users have nothing to do there. */
function PublicOnly() {
  const status = useAuthStore((s) => s.status);
  if (status === "authenticated") return <Navigate to={paths.home} replace />;
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
        <Outlet />
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

function CommunityRoute() {
  const { commname = "" } = useParams();
  const handle = commname.toLowerCase();
  return <CommunityDetailView key={handle} commname={handle} />;
}

function LettersRoute() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  return (
    <LettersInboxView
      composeTo={params.get("to")}
      // The composer was opened by `?to=`: drop it so reloading does not reopen it.
      onComposeClosed={() => navigate(paths.letters, { replace: true })}
    />
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicOnly />}>
        <Route path={paths.login} element={<LoginView />} />
        <Route path={paths.register} element={<RegisterView />} />
      </Route>

      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<FeedRoute />} />
          <Route path="u/:username" element={<ProfileRoute />} />
          <Route path="communities" element={<CommunityListView />} />
          <Route path="c/:commname" element={<CommunityRoute />} />
          <Route path="store" element={<StoreView />} />
          <Route path="letters" element={<LettersRoute />} />
          <Route path="*" element={<Navigate to={paths.home} replace />} />
        </Route>
      </Route>
    </Routes>
  );
}
