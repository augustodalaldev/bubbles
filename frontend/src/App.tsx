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
import { MOCK_COMMUNITIES } from "@/features/profile/mockData";
import { Community } from "@/types";

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
  const [communities, setCommunities] = useState<Community[]>(MOCK_COMMUNITIES);
  const [selectedCommunity, setSelectedCommunity] = useState<Community | null>(null);
  const [profileUsername, setProfileUsername] = useState<string | null>(null);

  const handleJoinToggleCommunity = (communityId: number) => {
    setCommunities((prev) =>
      prev.map((c) => {
        if (c.id !== communityId) return c;
        const isMember = !!c.my_membership;
        return {
          ...c,
          member_count: isMember ? Math.max(1, c.member_count - 1) : c.member_count + 1,
          my_membership: isMember
            ? null
            : {
                role: "MEMBER",
                current_state: "ACTIVE",
                joined_at: new Date().toISOString(),
              },
        };
      })
    );
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col justify-between font-sans">
      <div>
        {/* Straight Classic Header with View Navigator */}
        <Header 
          currentView={currentView === "community-detail" ? "communities" : currentView}
          onNavigate={(view) => {
            if (view === "communities") {
              setSelectedCommunity(null);
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
              setSelectedCommunity(comm);
              setCurrentView("community-detail");
            }}
            searchTerm={searchTerm}
            onClearSearch={() => setSearchTerm("")}
          />
        )}

        {currentView === "communities" && (
          <CommunityListView
            communities={communities}
            currentUser={user}
            onSelectCommunity={(comm) => {
              setSelectedCommunity(comm);
              setCurrentView("community-detail");
            }}
            onJoinToggleCommunity={handleJoinToggleCommunity}
            onCommunityCreated={(newComm) => {
              setCommunities((prev) => [newComm, ...prev]);
            }}
          />
        )}

        {currentView === "community-detail" && selectedCommunity && (
          <CommunityDetailView
            community={selectedCommunity}
            currentUser={user}
            onBackToHub={() => setCurrentView("communities")}
            onSelectOtherCommunity={(other) => {
              setSelectedCommunity(other);
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
              setSelectedCommunity(comm);
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
