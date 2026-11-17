import { useEffect, useState } from "react";
import { Header, AppView } from "@/components/Header";
import { LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { useHeartbeat } from "@/features/auth/useHeartbeat";
import { ProfileView } from "@/features/profile/ProfileView";
import { FeedView } from "@/features/feed/FeedView";
import { CommunityListView } from "@/features/communities/CommunityListView";
import { CommunityDetailView } from "@/features/communities/CommunityDetailView";
import { StoreView } from "@/features/customization/StoreView";
import { LettersInboxView } from "@/features/letters/LettersInboxView";
import { LoginView } from "@/features/auth/LoginView";
import { RegisterView } from "@/features/auth/RegisterView";

type View = AppView | "community-detail";

export default function App() {
  const status = useAuthStore((s) => s.status);
  const user = useAuthStore((s) => s.user);
  const bootstrap = useAuthStore((s) => s.bootstrap);
  const [authScreen, setAuthScreen] = useState<"login" | "register">("login");

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  useHeartbeat(status === "authenticated");

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <LoadingState label="Entrando..." />
      </div>
    );
  }

  if (status === "anonymous" || !user) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] text-slate-800 font-sans">
        {authScreen === "login" ? (
          <LoginView onNavigateToRegister={() => setAuthScreen("register")} />
        ) : (
          <RegisterView onNavigateToLogin={() => setAuthScreen("login")} />
        )}
      </div>
    );
  }

  return <AuthenticatedApp />;
}

function AuthenticatedApp() {
  const user = useAuthStore((s) => s.user)!;
  const [currentView, setCurrentView] = useState<View>("feed");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedCommname, setSelectedCommname] = useState<string | null>(null);
  const [profileUsername, setProfileUsername] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col justify-between font-sans">
      <div>
        {/* Straight Classic Header with View Navigator */}
        <Header 
          currentView={currentView === "community-detail" ? "communities" : currentView}
          onNavigate={(view) => {
            if (view === "communities") {
              setSelectedCommname(null);
            }
            if (view === "profile") setProfileUsername(null);
            setCurrentView(view);
          }}
          onSearchChange={(term) => {
            setSearchTerm(term);
            if (term.trim() && currentView !== "feed") {
              setCurrentView("feed");
            }
          }}
        />

        {/* Dynamic Section Render according to Plan */}
        {currentView === "feed" && (
          <FeedView
            onNavigateToProfile={() => {
              setProfileUsername(null);
              setCurrentView("profile");
            }}
            onOpenProfile={(username) => {
              setProfileUsername(username === user.username ? null : username);
              setCurrentView("profile");
            }}
            onNavigateToView={(v) => {
              if (v === "profile") setCurrentView("profile");
              else if (v === "feed") setCurrentView("feed");
              else if (v === "communities") setCurrentView("communities");
              else if (v === "store") setCurrentView("store");
              else if (v === "letters") setCurrentView("letters");
            }}
            onSelectCommunity={(comm) => {
              setSelectedCommname(comm.commname);
              setCurrentView("community-detail");
            }}
            searchTerm={searchTerm}
            onClearSearch={() => setSearchTerm("")}
          />
        )}

        {currentView === "communities" && (
          <CommunityListView
            onSelectCommunity={(comm) => {
              setSelectedCommname(comm.commname);
              setCurrentView("community-detail");
            }}
          />
        )}

        {currentView === "community-detail" && selectedCommname && (
          <CommunityDetailView
            commname={selectedCommname}
            onBackToHub={() => setCurrentView("communities")}
            onOpenProfile={(username) => {
              setProfileUsername(username === user.username ? null : username);
              setCurrentView("profile");
            }}
          />
        )}

        {currentView === "store" && (
          <StoreView
            onNavigateToView={(v) => setCurrentView(v as View)}
            onNavigateToProfile={() => setCurrentView("profile")}
          />
        )}

        {currentView === "letters" && (
          <LettersInboxView
            currentUser={user}
            onNavigateToView={(v) => setCurrentView(v as View)}
            onNavigateToProfile={() => setCurrentView("profile")}
          />
        )}

        {currentView === "profile" && (
          <ProfileView
            username={profileUsername}
            onOpenProfile={(username) => setProfileUsername(username === user.username ? null : username)}
            onNavigateToView={(v) => setCurrentView(v as View)}
            onSelectCommunity={(comm) => {
              setSelectedCommname(comm.commname);
              setCurrentView("community-detail");
            }}
          />
        )}
      </div>

      {/* Footer (Rendered on Profile, Hub, Auth, while Feed, CommunityDetail, Store & Letters have internal stream note) */}
      {currentView === "profile" || currentView === "communities" ? (
        <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-200 mt-8">
          Bubbles • Rede Social
        </footer>
      ) : null}
    </div>
  );
}
