import { useState } from "react";
import { Header } from "@/components/Header";
import { ProfileView } from "@/features/profile/ProfileView";
import { LoginView } from "@/features/auth/LoginView";
import { RegisterView } from "@/features/auth/RegisterView";

type View = "profile" | "login" | "register";

export default function App() {
  const [currentView, setCurrentView] = useState<View>("profile");

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col justify-between">
      <div>
        {/* Straight Classic Header with View Navigator */}
        <Header 
          currentView={currentView}
          onNavigate={(view) => setCurrentView(view)}
        />

        {/* Dynamic Section Render according to Plan */}
        {currentView === "profile" && <ProfileView />}
        {currentView === "login" && (
          <LoginView
            onNavigateToRegister={() => setCurrentView("register")}
            onLoginSuccess={() => setCurrentView("profile")}
          />
        )}
        {currentView === "register" && (
          <RegisterView
            onNavigateToLogin={() => setCurrentView("login")}
            onRegisterSuccess={() => setCurrentView("profile")}
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
