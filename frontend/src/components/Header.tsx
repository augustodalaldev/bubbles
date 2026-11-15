import { Search, Sparkles, Compass, Users, Store, Bell } from "lucide-react";
import { MOCK_USER } from "@/features/profile/mockData";

interface HeaderProps {
  onSearchChange?: (term: string) => void;
}

export const Header = ({ onSearchChange }: HeaderProps) => {
  return (
    <header className="sticky top-0 z-40 w-full px-4 py-2.5 backdrop-blur-xl bg-white/60 border-b border-white/80 shadow-[0_4px_20px_-2px_rgba(8,196,219,0.12)]">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="relative w-10 h-10 rounded-full bubble-sphere flex items-center justify-center shadow-bubble group-hover:scale-105 transition-transform">
            <span className="text-xl select-none">🫧</span>
            <div className="bubble-reflection" />
          </div>
          <div className="flex flex-col">
            <span className="text-2xl font-black tracking-tight bg-gradient-to-r from-bubble-600 via-sky-500 to-soap-500 bg-clip-text text-transparent drop-shadow-sm font-sans">
              Bubbles
            </span>
            <span className="text-[10px] -mt-1 font-semibold text-bubble-700/70 tracking-widest uppercase">
              Liquid Social
            </span>
          </div>
        </div>

        {/* Global Search Bar (Frutiger Glossy Search) */}
        <div className="flex-1 max-w-md hidden md:block">
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-bubble-600/60" />
            <input
              type="text"
              placeholder="Pesquisar perfis, comunidades ou bolhas..."
              onChange={(e) => onSearchChange?.(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm rounded-full bg-white/70 border border-white/90 text-slate-800 placeholder-bubble-900/40 shadow-[inset_0_1.5px_3px_rgba(0,0,0,0.06),0_2px_8px_rgba(8,196,219,0.08)] focus:outline-none focus:ring-2 focus:ring-bubble-400 focus:bg-white/90 transition-all"
            />
          </div>
        </div>

        {/* Navigation & User Capsule */}
        <div className="flex items-center gap-3">
          {/* Quick Nav Icons */}
          <nav className="hidden lg:flex items-center gap-1">
            <button 
              title="Explorar"
              className="p-2 rounded-full hover:bg-white/70 text-slate-700 hover:text-bubble-600 transition-colors"
            >
              <Compass className="w-5 h-5" />
            </button>
            <button 
              title="Comunidades"
              className="p-2 rounded-full hover:bg-white/70 text-slate-700 hover:text-bubble-600 transition-colors"
            >
              <Users className="w-5 h-5" />
            </button>
            <button 
              title="Loja de Sabão"
              className="p-2 rounded-full hover:bg-white/70 text-slate-700 hover:text-soap-600 transition-colors relative"
            >
              <Store className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-soap-500 animate-ping" />
            </button>
            <button 
              title="Notificações"
              className="p-2 rounded-full hover:bg-white/70 text-slate-700 hover:text-bubble-600 transition-colors relative"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-bubble-500" />
            </button>
          </nav>

          {/* Soap Balance Pill */}
          <div 
            title="Seu saldo de Sabões para apoiar conteúdos e comprar itens"
            className="soap-counter-pill flex items-center gap-2 px-3.5 py-1.5 rounded-full cursor-pointer hover:scale-105 transition-transform"
          >
            <span className="text-base select-none">🧼</span>
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold text-soap-700 leading-tight flex items-center gap-1">
                {MOCK_USER.soap_balance} Sabões
                <Sparkles className="w-3 h-3 text-soap-500 fill-soap-400" />
              </span>
              <span className="text-[9px] font-medium text-slate-500 leading-none">
                +5/dia
              </span>
            </div>
          </div>

          {/* User Mini Avatar */}
          <div className="flex items-center gap-2 pl-1 border-l border-white/60">
            <div className="relative cursor-pointer group">
              <img
                src={MOCK_USER.profile_photo || ""}
                alt={MOCK_USER.name}
                className="w-9 h-9 rounded-full object-cover border-2 border-white shadow-md group-hover:ring-2 group-hover:ring-bubble-400 transition-all"
              />
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-400 ring-2 ring-white" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
