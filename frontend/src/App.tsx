import { Header } from "@/components/Header";
import { ProfileView } from "@/features/profile/ProfileView";

export default function App() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800">
      {/* Straight Classic Header */}
      <Header />

      {/* Orkut-inspired Profile Screen */}
      <ProfileView />

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-slate-400">
        Bubbles • Rede Social
      </footer>
    </div>
  );
}
