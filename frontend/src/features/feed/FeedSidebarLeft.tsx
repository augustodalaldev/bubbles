import React from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { User } from "@/types";
import { Avatar } from "@/components/Avatar";
import { UserName } from "@/components/UserName";
import { SoapIcon } from "@/components/SoapIcon";
import { useAuthStore } from "@/features/auth/authStore";
import { Compass, User as UserIcon, Users, Store, Mail } from "lucide-react";

interface FeedSidebarLeftProps {
  currentUser: User;
  unreadLettersCount?: number;
}

export const FeedSidebarLeft: React.FC<FeedSidebarLeftProps> = ({
  currentUser,
  unreadLettersCount = 0,
}) => {
  const economy = useAuthStore((s) => s.economy);
  return (
    <aside className="space-y-4">
      
      {/* Mini Profile Card */}
      <div className="panel-classic">
        <div className="p-3 text-center">
          
          {/* User Avatar (Clean, no filter overlay) */}
          <Link
            to={paths.profile(currentUser.username)}
            aria-label="Meu perfil"
            className="inline-block mx-auto mb-2 relative"
          >
            <Avatar
              user={currentUser}
              className="w-16 h-16 mx-auto hover:border-pink-500 transition-colors"
            />
          </Link>

          <h2 className="text-xs font-bold text-slate-900 truncate">
            <Link to={paths.profile(currentUser.username)} className="hover:text-pink-600">
              <UserName user={currentUser} showBadge={false} />
            </Link>
          </h2>
          <span className="text-[11px] text-slate-400 block -mt-0.5 mb-2">
            @{currentUser.username}
          </span>

          {/* Followers / Following Row */}
          <div className="flex items-center justify-center gap-3 py-1.5 border-t border-b border-slate-100 text-[11px] text-slate-600 mb-2.5">
            <Link to={paths.followers(currentUser.username)} className="hover:text-pink-700">
              <span className="font-bold text-slate-900">{currentUser.followers_count ?? 0}</span>
              <span className="text-slate-400 ml-1">seguidores</span>
            </Link>
            <span className="text-slate-300">•</span>
            <Link to={paths.following(currentUser.username)} className="hover:text-pink-700">
              <span className="font-bold text-slate-900">{currentUser.following_count ?? 0}</span>
              <span className="text-slate-400 ml-1">seguindo</span>
            </Link>
          </div>

          {/* Soap Wallet Mini Banner */}
          <div className="flex items-center justify-between p-2 bg-pink-50/80 border border-pink-200 rounded-sm">
            <div className="flex items-center gap-1.5">
              <SoapIcon size={18} />
              <div className="text-left">
                <span className="text-xs font-bold text-pink-900 block leading-tight">
                  {currentUser.soap_balance ?? 0} soap
                </span>
                <span className="text-[9px] text-slate-500 leading-tight">
                  saldo atual
                </span>
              </div>
            </div>
            <span className="text-[10px] font-semibold text-pink-700 bg-white px-1.5 py-0.5 rounded-sm border border-pink-200 shadow-2xs">
              {economy
                ? `+${economy.default_passive_earn_rate}/${economy.passive_interval_minutes} min`
                : ""}
            </span>
          </div>

        </div>
      </div>

      {/* Classic Menu Navigation Links (phones use the header tabs) */}
      <div className="panel-classic hidden lg:block">
        <div className="panel-classic-header">
          <span className="text-xs font-bold text-slate-800">
            Navegação
          </span>
        </div>
        <div className="p-1 text-xs">
          
          <Link to={paths.home}
            
            className="w-full flex items-center gap-2.5 px-3 py-2 text-pink-700 font-semibold bg-pink-50/60 rounded-sm transition-colors text-left"
          >
            <Compass className="w-4 h-4 text-pink-600" />
            <span>Início (feed)</span>
          </Link>

          <Link to={paths.profile(currentUser.username)}
            
            className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <UserIcon className="w-4 h-4 text-slate-400" />
            <span>Meu perfil</span>
          </Link>

          <Link to={paths.communities}
            
            className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <Users className="w-4 h-4 text-slate-400" />
            <span>Comunidades</span>
          </Link>

          <Link to={paths.store}
            
            className="w-full flex items-center gap-2.5 px-3 py-2 text-slate-700 hover:text-slate-900 hover:bg-slate-50 rounded-sm transition-colors text-left"
          >
            <Store className="w-4 h-4 text-slate-400" />
            <span>Loja de soap</span>
          </Link>

          <Link to={paths.letters}
            
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
          </Link>

        </div>
      </div>

    </aside>
  );
};
