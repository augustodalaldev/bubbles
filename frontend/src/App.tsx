import { useState } from "react";
import { Header } from "@/components/Header";
import { ProfileView } from "@/features/profile/ProfileView";
import { FeedView } from "@/features/feed/FeedView";
import { CommunityListView } from "@/features/communities/CommunityListView";
import { CommunityDetailView } from "@/features/communities/CommunityDetailView";
import { StoreView } from "@/features/customization/StoreView";
import { LettersInboxView } from "@/features/letters/LettersInboxView";
import { LoginView } from "@/features/auth/LoginView";
import { RegisterView } from "@/features/auth/RegisterView";
import { MOCK_COMMUNITIES, MOCK_USER } from "@/features/profile/mockData";
import { Community } from "@/types";

type View = "feed" | "profile" | "communities" | "community-detail" | "store" | "letters" | "login" | "register";

export default function App() {
  const [currentView, setCurrentView] = useState<View>("feed");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [communities, setCommunities] = useState<Community[]>(MOCK_COMMUNITIES);
  const [selectedCommunity, setSelectedCommunity] = useState<Community | null>(null);

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
            onNavigateToProfile={() => setCurrentView("profile")}
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
            currentUser={MOCK_USER}
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
            currentUser={MOCK_USER}
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
            currentUser={MOCK_USER}
            onNavigateToView={(v) => setCurrentView(v as View)}
            onNavigateToProfile={() => setCurrentView("profile")}
          />
        )}

        {currentView === "profile" && <ProfileView />}

        {currentView === "login" && (
          <LoginView
            onNavigateToRegister={() => setCurrentView("register")}
            onLoginSuccess={() => setCurrentView("feed")}
          />
        )}

        {currentView === "register" && (
          <RegisterView
            onNavigateToLogin={() => setCurrentView("login")}
            onRegisterSuccess={() => setCurrentView("feed")}
          />
        )}
      </div>

      {/* Footer (Rendered on Profile, Hub, Auth, while Feed, CommunityDetail, Store & Letters have internal stream note) */}
      {currentView !== "feed" && currentView !== "community-detail" && currentView !== "store" && currentView !== "letters" && (
        <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-200 mt-8">
          Bubbles • Rede Social
        </footer>
      )}
    </div>
  );
}
