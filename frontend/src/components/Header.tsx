import React from "react";
import { Search, Compass, Users, Store, Bell } from "lucide-react";
import { MOCK_USER } from "@/features/profile/mockData";
import { BrandLogo } from "./BrandLogo";
import { SoapIcon } from "./SoapIcon";

interface HeaderProps {
  currentView?: "feed" | "profile" | "communities" | "store" | "login" | "register";
  onNavigate?: (view: "feed" | "profile" | "communities" | "store" | "login" | "register") => void;
  onSearchChange?: (term: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentView = "feed",
  onNavigate,
  onSearchChange,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        
        {/* Brand Logo with Official SVG (Click goes to Feed) */}
        <div 
          onClick={() => onNavigate?.("feed")}
          className="flex items-center cursor-pointer"
        >
          <BrandLogo height={32} />
        </div>

        {/* Global Search Bar (Straight, Clean style) */}
        <div className="flex-1 max-w-md hidden md:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar perfis, comunidades ou postagens..."
              onChange={(e) => onSearchChange?.(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-pink-500 focus:bg-white transition-colors"
            />
          </div>
        </div>

        {/* Navigation, Auth Switcher & User Pill */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Section Switcher Tabs */}
          <div className="flex items-center bg-slate-100 p-0.5 border border-slate-200 rounded-sm text-xs font-semibold">
            <button
              onClick={() => onNavigate?.("feed")}
              className={`px-2.5 py-1 rounded-sm transition-all ${
                currentView === "feed"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Início
            </button>
            <button
              onClick={() => onNavigate?.("profile")}
              className={`px-2.5 py-1 rounded-sm transition-all ${
                currentView === "profile"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Perfil
            </button>
            <button
              onClick={() => onNavigate?.("communities")}
              className={`px-2.5 py-1 rounded-sm transition-all ${
                currentView === "communities"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Comunidades
            </button>
            <button
              onClick={() => onNavigate?.("store")}
              className={`px-2.5 py-1 rounded-sm transition-all ${
                currentView === "store"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Loja
            </button>
            <button
              onClick={() => onNavigate?.("login")}
              className={`px-2.5 py-1 rounded-sm transition-all ${
                currentView === "login"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Entrar
            </button>
            <button
              onClick={() => onNavigate?.("register")}
              className={`px-2.5 py-1 rounded-sm transition-all ${
                currentView === "register"
                  ? "bg-white text-slate-900 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              Cadastrar
            </button>
          </div>

          {/* Quick Nav Icons */}
          <nav className="hidden lg:flex items-center gap-1">
            <button 
              onClick={() => onNavigate?.("feed")}
              title="Feed / Início"
              className={`p-1.5 rounded-sm transition-colors ${
                currentView === "feed"
                  ? "text-pink-600 bg-pink-50"
                  : "text-slate-600 hover:text-pink-600 hover:bg-slate-100"
              }`}
            >
              <Compass className="w-4 h-4" />
            </button>
            <button 
              onClick={() => onNavigate?.("communities")}
              title="Comunidades"
              className={`p-1.5 rounded-sm transition-colors ${
                currentView === "communities"
                  ? "text-pink-600 bg-pink-50"
                  : "text-slate-600 hover:text-pink-600 hover:bg-slate-100"
              }`}
            >
              <Users className="w-4 h-4" />
            </button>
            <button 
              onClick={() => onNavigate?.("store")}
              title="Loja de Soap"
              className={`p-1.5 rounded-sm transition-colors ${
                currentView === "store"
                  ? "text-pink-600 bg-pink-50"
                  : "text-slate-600 hover:text-pink-600 hover:bg-slate-100"
              }`}
            >
              <Store className="w-4 h-4" />
            </button>
            <button 
              title="Notificações"
              className="p-1.5 text-slate-600 hover:text-pink-600 hover:bg-slate-100 rounded-sm transition-colors"
            >
              <Bell className="w-4 h-4" />
            </button>
          </nav>

          {/* Soap Balance Badge with Enlarged SoapIcon */}
          <div 
            onClick={() => onNavigate?.("store")}
            title="Seu saldo de soap (clique para abrir a Loja)"
            className="flex items-center gap-2 px-2.5 py-1 bg-pink-50 border border-pink-200 rounded-sm cursor-pointer hover:bg-pink-100/70 transition-colors"
          >
            <SoapIcon size={20} />
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold text-pink-900 leading-tight">
                {MOCK_USER.soap_balance} soap
              </span>
              <span className="text-[10px] text-slate-500 leading-none">
                +5/dia
              </span>
            </div>
          </div>

          {/* User Mini Avatar (Click to go to Profile) */}
          <div 
            onClick={() => onNavigate?.("profile")}
            className="flex items-center gap-2 pl-1 border-l border-slate-200 cursor-pointer"
            title="Meu Perfil"
          >
            <img
              src={MOCK_USER.profile_photo || ""}
              alt={MOCK_USER.name}
              className="w-8 h-8 rounded-full object-cover border border-slate-200"
            />
          </div>
        </div>

      </div>
    </header>
  );
};
