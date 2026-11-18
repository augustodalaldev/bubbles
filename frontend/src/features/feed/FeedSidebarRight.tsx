import React from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { Community } from "@/types";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { Users, ChevronRight } from "lucide-react";

interface FeedSidebarRightProps {
  communities: Community[] | null;
  error: string | null;
  onRetry: () => void;
}

export const FeedSidebarRight: React.FC<FeedSidebarRightProps> = ({
  communities,
  error,
  onRetry,
}) => (
  <aside className="space-y-4">
    <div className="panel-classic">
      <div className="panel-classic-header flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5 text-pink-600" />
          <h2 className="text-xs font-bold text-slate-900">Minhas comunidades</h2>
        </div>
        <Link to={paths.communities}
          
          className="text-[11px] text-pink-600 hover:text-pink-700 font-semibold flex items-center"
        >
          Ver todas
          <ChevronRight className="w-3 h-3 ml-0.5" />
        </Link>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={onRetry} />
      ) : communities === null ? (
        <LoadingState />
      ) : communities.length === 0 ? (
        <EmptyState message="Você ainda não participa de comunidades" hint="Explore e entre em uma." />
      ) : (
        <div className="p-2 divide-y divide-slate-100">
          {communities.slice(0, 5).map((comm) => (
            <Link to={paths.community(comm.commname)}
              key={comm.id}
              
              className="w-full py-2 px-1 flex items-center justify-between gap-2 hover:bg-slate-50 rounded-sm transition-colors text-left"
            >
              <div className="flex items-center gap-2 min-w-0">
                {comm.community_photo ? (
                  <img
                    src={comm.community_photo}
                    alt={comm.name}
                    className="w-8 h-8 rounded-full object-cover border border-slate-200 flex-shrink-0"
                  />
                ) : (
                  <span className="w-8 h-8 rounded-full bg-purple-50 border border-slate-200 text-purple-700 text-xs font-bold flex items-center justify-center flex-shrink-0">
                    {comm.name.charAt(0).toUpperCase()}
                  </span>
                )}
                <div className="min-w-0">
                  <h3 className="text-xs font-bold text-slate-800 truncate">{comm.name}</h3>
                  <span className="text-[10px] text-slate-500 block leading-tight">
                    {comm.member_count.toLocaleString("pt-BR")} membros
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  </aside>
);
