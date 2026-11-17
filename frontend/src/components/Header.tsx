import React from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Search, Compass, Users, Store, Mail, LogOut } from "lucide-react";
import { useAuthStore } from "@/features/auth/authStore";
import { paths, viewFromPath, viewPath } from "@/routes";
import type { AppView } from "@/routes";
import { Avatar } from "./Avatar";
import { BrandLogo } from "./BrandLogo";
import { SoapIcon } from "./SoapIcon";

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

export const Header: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  const economy = useAuthStore((s) => s.economy);
  const logout = useAuthStore((s) => s.logout);
  const location = useLocation();
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const ownUsername = user?.username;
  const currentView = viewFromPath(location.pathname, ownUsername);
  const to = (view: AppView) => viewPath(view, ownUsername);

  // The search term lives in the URL (?q=) so it survives reloads and the back button.
  const onFeed = location.pathname === paths.home;
  const searchValue = onFeed ? (params.get("q") ?? "") : "";

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
        <Link to={paths.home} className="flex items-center" aria-label="Ir para o início">
          <BrandLogo height={32} />
        </Link>

        <div className="flex-1 max-w-md hidden md:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="search"
              aria-label="Buscar perfis e comunidades"
              placeholder="Buscar perfis e comunidades..."
              value={searchValue}
              onChange={(e) => navigate(paths.search(e.target.value), { replace: onFeed })}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white transition-colors"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <nav aria-label="Seções" className="flex items-center bg-slate-100 p-0.5 border border-slate-200 rounded-sm text-xs font-semibold">
            {TABS.map(({ view, label }) => (
              <Link
                key={view}
                to={to(view)}
                aria-current={currentView === view ? "page" : undefined}
                className={`px-2.5 py-1 rounded-sm transition-all ${
                  currentView === view
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {label}
              </Link>
            ))}
          </nav>

          <div className="hidden lg:flex items-center gap-1">
            {ICONS.map(({ view, title, Icon }) => (
              <Link
                key={view}
                to={to(view)}
                title={title}
                aria-label={title}
                className={`p-1.5 rounded-sm transition-colors ${
                  currentView === view
                    ? "text-pink-600 bg-pink-50"
                    : "text-slate-600 hover:text-pink-600 hover:bg-slate-100"
                }`}
              >
                <Icon className="w-4 h-4" />
              </Link>
            ))}
          </div>

          <Link
            to={paths.store}
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
          </Link>

          {user && (
            <Link
              to={paths.profile(user.username)}
              className="flex items-center gap-2 pl-1 border-l border-slate-200"
              title="Meu perfil"
              aria-label="Meu perfil"
            >
              <Avatar user={user} />
            </Link>
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
