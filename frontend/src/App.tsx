import { useState } from "react";
import { Header } from "@/components/Header";
import { ProfileView } from "@/features/profile/ProfileView";
import { FeedView } from "@/features/feed/FeedView";
import { LoginView } from "@/features/auth/LoginView";
import { RegisterView } from "@/features/auth/RegisterView";

type View = "feed" | "profile" | "login" | "register";

export default function App() {
  const [currentView, setCurrentView] = useState<View>("feed");
  const [searchTerm, setSearchTerm] = useState<string>("");

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col justify-between font-sans">
      <div>
        {/* Straight Classic Header with View Navigator */}
        <Header 
          currentView={currentView}
          onNavigate={(view) => setCurrentView(view)}
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
            }}
            searchTerm={searchTerm}
            onClearSearch={() => setSearchTerm("")}
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

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-slate-400 border-t border-slate-200 mt-8">
        Bubbles • Rede Social
      </footer>
    </div>
  );
}
