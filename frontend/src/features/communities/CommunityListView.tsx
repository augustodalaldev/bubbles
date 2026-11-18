import React, { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { paths } from "@/routes";
import { Community } from "@/types";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { joinCommunity, leaveCommunity, listCommunities } from "@/services/communities";
import { errorMessage } from "@/services/errors";
import { Users, Plus, Search, UserCheck, ChevronRight } from "lucide-react";
import { CreateCommunityModal } from "./CreateCommunityModal";

export const CommunityListView: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"all" | "my">("all");
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [communities, setCommunities] = useState<Community[]>([]);
  const [nextPage, setNextPage] = useState<number | null>(null);
  const [total, setTotal] = useState(0);
  const [myIds, setMyIds] = useState<Set<number>>(new Set());
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Debounce the search box before hitting the API.
  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(searchInput.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [searchInput]);

  const load = useCallback(
    async (page: number, reset: boolean) => {
      if (reset) setStatus("loading");
      else setLoadingMore(true);
      try {
        const data = await listCommunities({ search, mine: activeTab === "my", page });
        setCommunities((prev) => (reset ? data.results : [...prev, ...data.results]));
        setTotal(data.count);
        setNextPage(data.next ? page + 1 : null);
        setStatus("ready");
      } catch (err) {
        setError(errorMessage(err));
        if (reset) setStatus("error");
      } finally {
        setLoadingMore(false);
      }
    },
    [search, activeTab]
  );

  // The list payload does not say which communities I belong to, so ask for "mine" separately.
  const loadMine = useCallback(async () => {
    try {
      const data = await listCommunities({ mine: true });
      setMyIds(new Set(data.results.map((c) => c.id)));
    } catch {
      // Membership badges are optional; the list itself still works.
    }
  }, []);

  useEffect(() => {
    void load(1, true);
  }, [load]);

  useEffect(() => {
    void loadMine();
  }, [loadMine]);

  const toggleMembership = async (community: Community) => {
    setBusyId(community.id);
    setActionError(null);
    try {
      if (myIds.has(community.id)) await leaveCommunity(community.commname);
      else await joinCommunity(community.commname);
      await Promise.all([load(1, true), loadMine()]);
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="panel-classic mb-5">
        <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-pink-600" />
              <h1 className="text-base font-bold text-slate-900 tracking-tight">Comunidades</h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Descubra espaços temáticos e publicações criadas pelos membros.
            </p>
          </div>

          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs transition-all self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Criar comunidade</span>
          </button>
        </div>

        <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-1" role="tablist">
            {(
              [
                ["all", "Todas"],
                ["my", "Minhas"],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                role="tab"
                aria-selected={activeTab === id}
                onClick={() => setActiveTab(id)}
                className={`px-3 py-1 text-xs font-semibold rounded-sm transition-all ${
                  activeTab === id
                    ? "bg-pink-600 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                }`}
              >
                {label}
                {activeTab === id && status === "ready" ? ` (${total})` : ""}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="search"
              aria-label="Buscar comunidades"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Buscar por nome ou identificador..."
              className="w-full pl-8 pr-3 py-1 text-xs bg-white border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 text-slate-800 placeholder-slate-400"
            />
          </div>
        </div>
      </div>

      {actionError && (
        <p role="alert" className="mb-3 text-xs text-red-700">
          {actionError}
        </p>
      )}

      {status === "loading" ? (
        <LoadingState label="Carregando comunidades..." />
      ) : status === "error" ? (
        <ErrorState message={error ?? "Não foi possível carregar as comunidades."} onRetry={() => void load(1, true)} />
      ) : communities.length === 0 ? (
        <div className="panel-classic">
          <EmptyState
            message="Nenhuma comunidade encontrada"
            hint={activeTab === "my" ? "Você ainda não participa de nenhuma." : "Tente outros termos ou crie a sua."}
          />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {communities.map((community) => {
              const isMember = myIds.has(community.id);
              return (
                <div
                  key={community.id}
                  className="panel-classic relative hover:shadow-md transition-shadow p-4 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start gap-3 mb-2.5">
                      <div className="relative w-14 h-14 rounded-full overflow-hidden flex-shrink-0 shadow-xs border border-slate-200 bg-purple-50 flex items-center justify-center text-purple-700 font-bold">
                        {community.community_photo ? (
                          <img src={community.community_photo} alt={community.name} className="w-full h-full object-cover" />
                        ) : (
                          community.name.charAt(0).toUpperCase()
                        )}
                        <BubbleOverlay opacity={0.4} />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <h2 className="text-xs font-bold text-slate-900 truncate">
                            <Link
                              to={paths.community(community.commname)}
                              className="hover:text-pink-600 after:absolute after:inset-0"
                            >
                              {community.name}
                            </Link>
                          </h2>
                          <span className="text-[11px] text-slate-400 font-mono">@{community.commname}</span>
                        </div>
                        {isMember && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 rounded-sm border border-emerald-200 mt-0.5">
                            <UserCheck className="w-3 h-3 text-emerald-600" />
                            Membro
                          </span>
                        )}
                        {community.is_archived && (
                          <span className="ml-1 inline-flex text-[10px] font-bold text-slate-600 bg-slate-100 px-1.5 rounded-sm border border-slate-300 mt-0.5">
                            Arquivada
                          </span>
                        )}
                        {community.moderation_status && (
                          <span className="ml-1 inline-flex text-[10px] font-bold text-amber-800 bg-amber-50 px-1.5 rounded-sm border border-amber-300 mt-0.5">
                            {community.moderation_status === "BANNED" ? "Banida" : "Suspensa"}
                          </span>
                        )}
                        <span className="block text-[11px] text-slate-500 font-medium mt-1">
                          {community.member_count.toLocaleString("pt-BR")} membros
                        </span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed line-clamp-2">
                      {community.description || "Nenhuma descrição fornecida."}
                    </p>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400">
                      Criada em {new Date(community.created_at).toLocaleDateString("pt-BR")}
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => void toggleMembership(community)}
                        disabled={busyId === community.id}
                        className={`relative z-10 text-xs px-2.5 py-0.5 rounded-sm font-semibold transition-all disabled:opacity-60 ${
                          isMember
                            ? "border border-slate-300 text-slate-600 hover:bg-slate-100"
                            : "bg-pink-50 border border-pink-200 text-pink-700 hover:bg-pink-100"
                        }`}
                      >
                        {isMember ? "Sair" : "Participar"}
                      </button>
                      <span className="flex items-center text-xs font-semibold text-pink-600" aria-hidden="true">
                        Abrir
                        <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {nextPage !== null && (
            <div className="text-center mt-4">
              <button
                onClick={() => void load(nextPage, false)}
                disabled={loadingMore}
                className="btn-outline px-4 py-1.5 text-xs font-semibold"
              >
                {loadingMore ? "Carregando..." : "Carregar mais"}
              </button>
            </div>
          )}
        </>
      )}

      {isCreateModalOpen && (
        <CreateCommunityModal
          onClose={() => setIsCreateModalOpen(false)}
          onCommunityCreated={(community) => navigate(paths.community(community.commname))}
        />
      )}
    </div>
  );
};
