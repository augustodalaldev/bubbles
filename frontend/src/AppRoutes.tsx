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
import { useAppNavigation } from "@/useAppNavigation";

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
  const [params] = useSearchParams();
  const nav = useAppNavigation();
  const view = viewFromPath(location.pathname, user.username);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col justify-between font-sans">
      <div>
        <Header
          currentView={view ?? undefined}
          onNavigate={nav.goTo}
          searchValue={location.pathname === "/" ? (params.get("q") ?? "") : ""}
          onSearchChange={nav.search}
        />
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

function LoginRoute() {
  const navigate = useNavigate();
  return <LoginView onNavigateToRegister={() => navigate(paths.register)} />;
}

function RegisterRoute() {
  const navigate = useNavigate();
  return <RegisterView onNavigateToLogin={() => navigate(paths.login)} />;
}

function FeedRoute() {
  const nav = useAppNavigation();
  const [params] = useSearchParams();
  return (
    <FeedView
      searchTerm={params.get("q") ?? ""}
      onClearSearch={nav.goHome}
      onNavigateToProfile={nav.goToOwnProfile}
      onOpenProfile={nav.openProfile}
      onNavigateToView={nav.goTo}
      onSelectCommunity={nav.openCommunity}
    />
  );
}

function ProfileRoute() {
  const nav = useAppNavigation();
  const { username = "" } = useParams();
  const handle = username.toLowerCase();
  return (
    <ProfileView
      key={handle}
      username={handle}
      onOpenProfile={nav.openProfile}
      onNavigateToView={nav.goTo}
      onWriteLetter={nav.writeLetter}
      onSelectCommunity={nav.openCommunity}
    />
  );
}

function CommunitiesRoute() {
  const nav = useAppNavigation();
  return <CommunityListView onSelectCommunity={nav.openCommunity} />;
}

function CommunityRoute() {
  const nav = useAppNavigation();
  const { commname = "" } = useParams();
  const handle = commname.toLowerCase();
  return (
    <CommunityDetailView
      key={handle}
      commname={handle}
      onBackToHub={() => nav.goTo("communities")}
      onOpenProfile={nav.openProfile}
    />
  );
}

function StoreRoute() {
  const nav = useAppNavigation();
  return <StoreView onNavigateToView={nav.goTo} onNavigateToProfile={nav.goToOwnProfile} />;
}

function LettersRoute() {
  const nav = useAppNavigation();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  return (
    <LettersInboxView
      composeTo={params.get("to")}
      // The composer was opened by `?to=`: drop it so reloading does not reopen it.
      onComposeClosed={() => navigate(paths.letters, { replace: true })}
      onNavigateToView={nav.goTo}
      onNavigateToProfile={nav.goToOwnProfile}
    />
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicOnly />}>
        <Route path={paths.login} element={<LoginRoute />} />
        <Route path={paths.register} element={<RegisterRoute />} />
      </Route>

      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<FeedRoute />} />
          <Route path="u/:username" element={<ProfileRoute />} />
          <Route path="communities" element={<CommunitiesRoute />} />
          <Route path="c/:commname" element={<CommunityRoute />} />
          <Route path="store" element={<StoreRoute />} />
          <Route path="letters" element={<LettersRoute />} />
          <Route path="*" element={<Navigate to={paths.home} replace />} />
        </Route>
      </Route>
    </Routes>
  );
}
