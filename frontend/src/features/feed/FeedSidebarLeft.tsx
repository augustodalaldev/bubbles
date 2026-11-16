import React from "react";
import { User } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { Compass, User as UserIcon, Users, Store, Mail, Sparkles } from "lucide-react";

interface FeedSidebarLeftProps {
  currentUser: User;
  onNavigateToProfile: () => void;
  onNavigateToView?: (view: string) => void;
  unreadLettersCount?: number;
}

export const FeedSidebarLeft: React.FC<FeedSidebarLeftProps> = ({
  currentUser,
  onNavigateToProfile,
  onNavigateToView,
  unreadLettersCount = 2,
}) => {
  return (
    <aside className="space-y-4">
      
      {/* Mini Profile Card */}
      <div className="panel-classic">
        <div className="p-3 text-center">
          
          {/* User Avatar (Clean, no filter overlay) */}
          <div 
            onClick={onNavigateToProfile}
            className="cursor-pointer inline-block mx-auto mb-2 relative"
          >
            <img
              src={currentUser.profile_photo || ""}
              alt={currentUser.name}
              className="w-16 h-16 rounded-full object-cover border-2 border-slate-200 mx-auto hover:border-pink-500 transition-colors"
            />
          </div>

          <h2 
            onClick={onNavigateToProfile}
            className="text-xs font-bold text-slate-900 hover:text-pink-600 cursor-pointer truncate"
          >
            {currentUser.name}
          </h2>
          <span className="text-[11px] text-slate-400 block -mt-0.5 mb-2">
            @{currentUser.username}
          </span>

          {/* Followers / Following Row */}
          <div className="flex items-center justify-center gap-3 py-1.5 border-t border-b border-slate-100 text-[11px] text-slate-600 mb-2.5">
            <div>
              <span className="font-bold text-slate-900">{currentUser.followers_count ?? 148}</span>
              <span className="text-slate-400 ml-1">seguidores</span>
            </div>
            <span className="text-slate-300">•</span>
            <div>
              <span className="font-bold text-slate-900">{currentUser.following_count ?? 92}</span>
              <span className="text-slate-400 ml-1">seguindo</span>
            </div>
          </div>

          {/* Soap Wallet Mini Banner */}
          <div className="flex items-center justify-between p-2 bg-pink-50/80 border border-pink-200 rounded-sm">
            <div className="flex items-center gap-1.5">
              <SoapIcon size={18} />
              <div className="text-left">
                <span className="text-xs font-bold text-pink-900 block leading-tight">
                  {currentUser.soap_balance ?? 78} soap
                </span>
                <span className="text-[9px] text-slate-500 leading-tight">
                  saldo atual
                </span>
              </div>
            </div>
            <span className="text-[10px] font-semibold text-pink-700 bg-white px-1.5 py-0.5 rounded-sm border border-pink-200 shadow-2xs">
              +5/dia
            </span>
          </div>

        </div>
      </div>

      {/* Classic Menu Navigation Links */}
      <div className="panel-classic">
        <div className="panel-classic-header">
          <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
            Navegação
          </span>
        </div>
        <div className="p-1 text-xs">
          
          <button
            onClick={() => onNavigateToView?.("feed")}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-pink-700 font-semibold bg-pink-50/60 rounded-sm transition-colors text-left"
          >
            <Compass className="w-4 h-4 text-pink-600" />
            <span>Início (Feed)</span>
          </button>

          <button
            onClick={onNavigateToProfile}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <UserIcon className="w-4 h-4 text-slate-400" />
            <span>Meu Perfil</span>
          </button>

          <button
            onClick={() => onNavigateToView?.("communities")}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <Users className="w-4 h-4 text-slate-400" />
            <span>Comunidades</span>
          </button>

          <button
            onClick={() => onNavigateToView?.("store")}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <Store className="w-4 h-4 text-slate-400" />
            <span>Loja de Soap</span>
          </button>

          <button
            onClick={() => onNavigateToView?.("letters")}
            className="w-full flex items-center justify-between px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <div className="flex items-center gap-2.5">
              <Mail className="w-4 h-4 text-slate-400" />
              <span>Cartas</span>
            </div>
            {unreadLettersCount > 0 && (
              <span className="px-1.5 py-0.2 bg-pink-600 text-white text-[10px] font-bold rounded-sm">
                {unreadLettersCount}
              </span>
            )}
          </button>

        </div>
      </div>

      {/* Soap Economy Reminder */}
      <div className="panel-classic bg-slate-50/50">
        <div className="p-3">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-800 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-pink-600" />
            <span>Economia Solidária</span>
          </div>
          <p className="text-[11px] text-slate-600 leading-relaxed">
            Aqui sua atenção não é vendida. Você gera 5 soap diários para apoiar o conteúdo de quem faz a rede valer a pena.
          </p>
        </div>
      </div>

    </aside>
  );
};
