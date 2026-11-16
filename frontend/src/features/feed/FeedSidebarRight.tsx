import React, { useState } from "react";
import { Community } from "@/types";
import { SuggestedUser } from "@/features/profile/mockData";
import { Users, UserPlus, Check, ChevronRight } from "lucide-react";

interface FeedSidebarRightProps {
  communities: Community[];
  suggestedUsers: SuggestedUser[];
  onSelectCommunity?: (community: Community) => void;
  onSelectUser?: (username: string) => void;
}

export const FeedSidebarRight: React.FC<FeedSidebarRightProps> = ({
  communities,
  suggestedUsers,
  onSelectCommunity,
  onSelectUser,
}) => {
  const [followingMap, setFollowingMap] = useState<Record<number, boolean>>({});

  const toggleFollow = (userId: number) => {
    setFollowingMap((prev) => ({
      ...prev,
      [userId]: !prev[userId],
    }));
  };

  return (
    <aside className="space-y-4">
      
      {/* Trending Communities */}
      <div className="panel-classic">
        <div className="panel-classic-header flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-pink-600" />
            <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
              Comunidades em Alta
            </h2>
          </div>
          <button 
            title="Ver todas as comunidades"
            className="text-[11px] text-pink-600 hover:text-pink-700 font-semibold flex items-center"
          >
            Ver todas
            <ChevronRight className="w-3 h-3 ml-0.5" />
          </button>
        </div>

        <div className="p-2 divide-y divide-slate-100">
          {communities.slice(0, 4).map((comm) => (
            <div
              key={comm.id}
              onClick={() => onSelectCommunity?.(comm)}
              className="py-2 px-1 flex items-center justify-between gap-2 hover:bg-slate-50 cursor-pointer rounded-sm transition-colors"
            >
              <div className="flex items-center gap-2 min-w-0">
                <img
                  src={comm.community_photo || ""}
                  alt={comm.name}
                  className="w-8 h-8 rounded-full object-cover border border-slate-200 flex-shrink-0"
                />
                <div className="min-w-0">
                  <h3 className="text-xs font-bold text-slate-800 truncate">
                    {comm.name}
                  </h3>
                  <span className="text-[10px] text-slate-500 block leading-tight">
                    {comm.member_count.toLocaleString("pt-BR")} membros
                  </span>
                </div>
              </div>

              <span className="text-[10px] text-pink-600 font-semibold px-2 py-0.5 border border-pink-200 rounded-sm hover:bg-pink-50 transition-colors flex-shrink-0">
                Ver
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Suggested Users to Follow */}
      <div className="panel-classic">
        <div className="panel-classic-header">
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
            Quem Seguir
          </h2>
        </div>

        <div className="p-2 divide-y divide-slate-100">
          {suggestedUsers.map(({ user, mutualInfo }) => {
            const isFollowing = followingMap[user.id];

            return (
              <div
                key={user.id}
                className="py-2.5 px-1 flex items-center justify-between gap-2"
              >
                <div 
                  onClick={() => onSelectUser?.(user.username)}
                  className="flex items-center gap-2 min-w-0 cursor-pointer"
                >
                  <img
                    src={user.profile_photo || ""}
                    alt={user.name}
                    className="w-8 h-8 rounded-full object-cover border border-slate-200 flex-shrink-0"
                  />
                  <div className="min-w-0">
                    <span className="text-xs font-bold text-slate-800 block truncate hover:text-pink-600">
                      {user.name}
                    </span>
                    <span className="text-[10px] text-slate-400 block truncate leading-tight">
                      {mutualInfo}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => toggleFollow(user.id)}
                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded-sm transition-all shadow-xs flex-shrink-0 ${
                    isFollowing
                      ? "bg-slate-100 border border-slate-300 text-slate-700"
                      : "bg-pink-50 border border-pink-200 text-pink-700 hover:bg-pink-100 font-semibold"
                  }`}
                >
                  {isFollowing ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-600" />
                      <span className="text-[11px]">Seguindo</span>
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-3 h-3" />
                      <span className="text-[11px]">Seguir</span>
                    </>
                  )}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Topics / Tags */}
      <div className="panel-classic">
        <div className="p-3">
          <span className="text-xs font-bold text-slate-900 uppercase tracking-wide block mb-2">
            Explorar Temas
          </span>
          <div className="flex flex-wrap gap-1.5">
            {["frutigeraero", "liquidglass", "soap", "fotografia", "anos2000", "interfaces"].map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 text-[11px] bg-slate-100 border border-slate-200 rounded-sm text-slate-700 hover:bg-pink-50 hover:border-pink-300 hover:text-pink-800 cursor-pointer transition-colors"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>

    </aside>
  );
};
