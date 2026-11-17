import React from "react";
import { Community, SearchResult } from "@/types";
import { Avatar } from "@/components/Avatar";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { Search, X } from "lucide-react";

interface SearchResultsPanelProps {
  term: string;
  result: SearchResult | null;
  error: string | null;
  loading: boolean;
  onRetry: () => void;
  onClear?: () => void;
  onOpenProfile: (username: string) => void;
  onSelectCommunity: (community: Community) => void;
}

export const SearchResultsPanel: React.FC<SearchResultsPanelProps> = ({
  term,
  result,
  error,
  loading,
  onRetry,
  onClear,
  onOpenProfile,
  onSelectCommunity,
}) => (
  <div className="panel-classic mb-4">
    <div className="panel-classic-header flex items-center justify-between">
      <span className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
        <Search className="w-3.5 h-3.5 text-pink-600" />
        Resultados para "{term}"
      </span>
      {onClear && (
        <button onClick={onClear} className="text-pink-700 hover:text-pink-900 text-xs font-bold flex items-center gap-0.5">
          <X className="w-3.5 h-3.5" />
          Limpar
        </button>
      )}
    </div>

    {error ? (
      <ErrorState message={error} onRetry={onRetry} />
    ) : loading && !result ? (
      <LoadingState />
    ) : result && result.users.length === 0 && result.communities.length === 0 ? (
      <EmptyState message="Nada encontrado" hint="Tente outro nome de usuário ou de comunidade." />
    ) : (
      result && (
        <div className="p-2 space-y-3">
          {result.users.length > 0 && (
            <div>
              <h3 className="text-[11px] font-bold text-slate-600 mb-1 px-1">Pessoas</h3>
              {result.users.map((u) => (
                <button
                  key={u.id}
                  onClick={() => onOpenProfile(u.username)}
                  className="w-full flex items-center gap-2 p-1.5 hover:bg-slate-50 rounded-sm text-left"
                >
                  <Avatar user={u} className="w-8 h-8" />
                  <span className="min-w-0">
                    <span className="block text-xs font-bold text-slate-800 truncate">{u.name}</span>
                    <span className="block text-[10px] text-slate-400">@{u.username}</span>
                  </span>
                </button>
              ))}
            </div>
          )}
          {result.communities.length > 0 && (
            <div>
              <h3 className="text-[11px] font-bold text-slate-600 mb-1 px-1">Comunidades</h3>
              {result.communities.map((c) => (
                <button
                  key={c.id}
                  onClick={() => onSelectCommunity(c)}
                  className="w-full flex items-center justify-between gap-2 p-1.5 hover:bg-slate-50 rounded-sm text-left"
                >
                  <span className="min-w-0">
                    <span className="block text-xs font-bold text-slate-800 truncate">{c.name}</span>
                    <span className="block text-[10px] text-slate-400">c/{c.commname}</span>
                  </span>
                  <span className="text-[10px] text-slate-500 flex-shrink-0">
                    {c.member_count.toLocaleString("pt-BR")} membros
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )
    )}
  </div>
);
