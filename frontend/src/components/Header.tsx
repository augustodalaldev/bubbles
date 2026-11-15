import React from "react";
import { Search, Compass, Users, Store, Bell } from "lucide-react";
import { MOCK_USER } from "@/features/profile/mockData";
import { BrandLogo } from "./BrandLogo";
import { SoapIcon } from "./SoapIcon";

interface HeaderProps {
  onSearchChange?: (term: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ onSearchChange }) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        
        {/* Brand Logo with Official SVG (Normal / Non-Bold) */}
        <div className="flex items-center cursor-pointer">
          <BrandLogo height={32} />
        </div>

        {/* Global Search Bar (Straight, Clean 2000s/Aero style) */}
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

        {/* Navigation & User Pill */}
        <div className="flex items-center gap-3">
          {/* Main Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            <button 
              title="Explorar"
              className="p-2 text-slate-600 hover:text-pink-600 hover:bg-slate-100 rounded-sm transition-colors"
            >
              <Compass className="w-4 h-4" />
            </button>
            <button 
              title="Comunidades"
              className="p-2 text-slate-600 hover:text-pink-600 hover:bg-slate-100 rounded-sm transition-colors"
            >
              <Users className="w-4 h-4" />
            </button>
            <button 
              title="Loja"
              className="p-2 text-slate-600 hover:text-pink-600 hover:bg-slate-100 rounded-sm transition-colors"
            >
              <Store className="w-4 h-4" />
            </button>
            <button 
              title="Notificações"
              className="p-2 text-slate-600 hover:text-pink-600 hover:bg-slate-100 rounded-sm transition-colors"
            >
              <Bell className="w-4 h-4" />
            </button>
          </nav>

          {/* Soap Balance Badge */}
          <div 
            title="Seu saldo de soap para apoios e customizações"
            className="flex items-center gap-2 px-3 py-1 bg-pink-50 border border-pink-200 rounded-sm cursor-pointer hover:bg-pink-100/70 transition-colors"
          >
            <SoapIcon size={16} />
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold text-pink-900 leading-tight">
                {MOCK_USER.soap_balance} soap
              </span>
              <span className="text-[10px] text-slate-500 leading-none">
                +5/dia
              </span>
            </div>
          </div>

          {/* User Mini Avatar */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
            <div className="relative cursor-pointer">
              <img
                src={MOCK_USER.profile_photo || ""}
                alt={MOCK_USER.name}
                className="w-8 h-8 rounded-full object-cover border border-slate-300"
              />
              <span 
                title="Ativo"
                className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-lime-400 border border-white"
              />
            </div>
          </div>
        </div>

      </div>
    </header>
  );
};
