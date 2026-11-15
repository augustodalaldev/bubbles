import { AmbientBubbles } from "@/components/AmbientBubbles";
import { Header } from "@/components/Header";
import { ProfileView } from "@/features/profile/ProfileView";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#b8f2f8]/70 via-[#e2f9fc]/80 to-[#fedbe9]/60 text-slate-800 relative selection:bg-bubble-300 selection:text-bubble-950">
      {/* Frutiger Aero Ambient Water Caustics & Floating Background Bubbles */}
      <AmbientBubbles />

      {/* Liquid Glass Header */}
      <Header />

      {/* Orkut-inspired Profile Screen MVP */}
      <ProfileView />

      {/* Subtle Footer with 2000s tech optimism tagline */}
      <footer className="relative z-10 py-6 text-center text-xs font-semibold text-bubble-800/60">
        Bubbles © 2026 • Frutiger Aero & Liquid Glass Social Network
      </footer>
    </div>
  );
}
