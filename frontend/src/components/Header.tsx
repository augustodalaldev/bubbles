import React from "react";
import { Search, Compass, Users, Store, Mail, LogOut } from "lucide-react";
import { useAuthStore } from "@/features/auth/authStore";
import { Avatar } from "./Avatar";
import { BrandLogo } from "./BrandLogo";
import { SoapIcon } from "./SoapIcon";

export type AppView = "feed" | "profile" | "communities" | "store" | "letters";

interface HeaderProps {
  currentView?: AppView;
  onNavigate?: (view: AppView) => void;
  onSearchChange?: (term: string) => void;
}

const TABS: { view: AppView; label: string }[] = [
  { view: "feed", label: "Início" },
  { view: "profile", label: "Perfil" },
  { view: "communities", label: "Comunidades" },
  { view: "store", label: "Loja" },
  { view: "letters", label: "Cartas" },
];

const ICONS: { view: AppView; title: string; Icon: typeof Compass }[] = [
  { view: "feed", title: "Feed / Início", Icon: Compass },
  { view: "communities", title: "Comunidades", Icon: Users },
  { view: "store", title: "Loja de soap", Icon: Store },
  { view: "letters", title: "Cartas", Icon: Mail },
];

export const Header: React.FC<HeaderProps> = ({ currentView = "feed", onNavigate, onSearchChange }) => {
  const user = useAuthStore((s) => s.user);
  const economy = useAuthStore((s) => s.economy);
  const logout = useAuthStore((s) => s.logout);

  const balance = user?.soap_balance ?? user?.wallet?.soap_balance ?? 0;
  const passiveHint = economy
    ? `+${economy.default_passive_earn_rate} a cada ${economy.passive_interval_minutes} min`
    : null;
  const passiveTitle = economy
    ? `Ganho passivo: ${economy.default_passive_earn_rate} soap a cada ${economy.passive_interval_minutes} minutos de uso, até ${economy.passive_daily_cap} por dia.`
    : "";

  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <button onClick={() => onNavigate?.("feed")} className="flex items-center" aria-label="Ir para o início">
          <BrandLogo height={32} />
        </button>

        <div className="flex-1 max-w-md hidden md:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="search"
              aria-label="Buscar perfis e comunidades"
              placeholder="Buscar perfis e comunidades..."
              onChange={(e) => onSearchChange?.(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white transition-colors"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <div className="flex items-center bg-slate-100 p-0.5 border border-slate-200 rounded-sm text-xs font-semibold">
            {TABS.map(({ view, label }) => (
              <button
                key={view}
                onClick={() => onNavigate?.(view)}
                className={`px-2.5 py-1 rounded-sm transition-all ${
                  currentView === view
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <nav className="hidden lg:flex items-center gap-1">
            {ICONS.map(({ view, title, Icon }) => (
              <button
                key={view}
                onClick={() => onNavigate?.(view)}
                title={title}
                aria-label={title}
                className={`p-1.5 rounded-sm transition-colors ${
                  currentView === view
                    ? "text-pink-600 bg-pink-50"
                    : "text-slate-600 hover:text-pink-600 hover:bg-slate-100"
                }`}
              >
                <Icon className="w-4 h-4" />
              </button>
            ))}
          </nav>

          <button
            onClick={() => onNavigate?.("store")}
            title={passiveTitle || "Seu saldo de soap (clique para abrir a Loja)"}
            className="flex items-center gap-2 px-2.5 py-1 bg-pink-50 border border-pink-200 rounded-sm hover:bg-pink-100/70 transition-colors"
          >
            <SoapIcon size={20} />
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold text-pink-900 leading-tight">{balance} soap</span>
              {passiveHint && (
                <span className="text-[10px] text-slate-500 leading-none">{passiveHint}</span>
              )}
            </div>
          </button>

          {user && (
            <button
              onClick={() => onNavigate?.("profile")}
              className="flex items-center gap-2 pl-1 border-l border-slate-200"
              title="Meu perfil"
              aria-label="Meu perfil"
            >
              <Avatar user={user} />
            </button>
          )}

          <button
            onClick={() => void logout()}
            title="Sair"
            aria-label="Sair"
            className="p-1.5 rounded-sm text-slate-600 hover:text-pink-600 hover:bg-slate-100 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
