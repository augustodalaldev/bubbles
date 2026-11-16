import React, { useState, useMemo } from "react";
import { Community, User } from "@/types";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { Users, Plus, Search, ShieldCheck, UserCheck, ChevronRight } from "lucide-react";
import { CreateCommunityModal } from "./CreateCommunityModal";

interface CommunityListViewProps {
  communities: Community[];
  currentUser: User;
  onSelectCommunity: (community: Community) => void;
  onJoinToggleCommunity?: (communityId: number) => void;
  onCommunityCreated?: (community: Community) => void;
}

export const CommunityListView: React.FC<CommunityListViewProps> = ({
  communities,
  currentUser,
  onSelectCommunity,
  onJoinToggleCommunity,
  onCommunityCreated,
}) => {
  const [activeTab, setActiveTab] = useState<"all" | "my">("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Filter communities by tab and search
  const filteredCommunities = useMemo(() => {
    let list = communities;

    if (activeTab === "my") {
      list = list.filter((c) => c.my_membership !== null && c.my_membership !== undefined);
    }

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      list = list.filter(
        (c) =>
          c.name.toLowerCase().includes(term) ||
          c.commname.toLowerCase().includes(term) ||
          c.description.toLowerCase().includes(term)
      );
    }

    return list;
  }, [communities, activeTab, searchTerm]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      
      {/* Top Banner & Stats */}
      <div className="panel-classic mb-5">
        <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-pink-600" />
              <h1 className="text-base font-bold text-slate-900 tracking-tight">
                Hub de Comunidades
              </h1>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Descubra espaços de debate, fóruns temáticos e publicações exclusivas criadas pelos membros.
            </p>
          </div>

          {/* Action: Create Community */}
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs transition-all self-start sm:self-auto cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Criar Comunidade</span>
          </button>
        </div>

        {/* Filter Bar & Search */}
        <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
          
          {/* Tabs: Todas vs Minhas */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab("all")}
              className={`px-3 py-1 text-xs font-semibold rounded-sm transition-all ${
                activeTab === "all"
                  ? "bg-pink-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
              }`}
            >
              Todas as Comunidades ({communities.length})
            </button>
            <button
              onClick={() => setActiveTab("my")}
              className={`px-3 py-1 text-xs font-semibold rounded-sm transition-all ${
                activeTab === "my"
                  ? "bg-pink-600 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-200"
              }`}
            >
              Minhas Comunidades ({communities.filter((c) => c.my_membership).length})
            </button>
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por nome ou tema..."
              className="w-full pl-8 pr-3 py-1 text-xs bg-white border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 text-slate-800 placeholder-slate-400"
            />
          </div>

        </div>
      </div>

      {/* Grid of Communities */}
      {filteredCommunities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
          {filteredCommunities.map((community) => {
            const isMember = !!community.my_membership;
            const role = community.my_membership?.role;

            return (
              <div
                key={community.id}
                onClick={() => onSelectCommunity(community)}
                className="panel-classic hover:shadow-md transition-shadow cursor-pointer p-4 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start gap-3 mb-2.5">
                    
                    {/* Spherical Community Avatar with BubbleOverlay */}
                    <div className="relative w-14 h-14 rounded-full overflow-hidden flex-shrink-0 shadow-xs border border-slate-200">
                      <img
                        src={community.community_photo || ""}
                        alt={community.name}
                        className="w-full h-full object-cover"
                      />
                      <BubbleOverlay opacity={0.4} />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <h2 className="text-xs font-bold text-slate-900 truncate hover:text-pink-600">
                          {community.name}
                        </h2>
                        <span className="text-[11px] text-slate-400 font-mono">
                          @{community.commname}
                        </span>
                      </div>

                      {/* Member role badge if user is part of community */}
                      {role === "LEADER" && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-purple-700 bg-purple-50 px-1.5 py-0.2 rounded-sm border border-purple-200 mt-0.5">
                          <ShieldCheck className="w-3 h-3 text-purple-600" />
                          Líder
                        </span>
                      )}
                      {role === "COMM_ADMIN" && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-pink-700 bg-pink-50 px-1.5 py-0.2 rounded-sm border border-pink-200 mt-0.5">
                          <ShieldCheck className="w-3 h-3 text-pink-600" />
                          Moderador
                        </span>
                      )}
                      {role === "MEMBER" && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded-sm border border-emerald-200 mt-0.5">
                          <UserCheck className="w-3 h-3 text-emerald-600" />
                          Membro
                        </span>
                      )}

                      <span className="block text-[11px] text-slate-500 font-medium mt-1">
                        {community.member_count.toLocaleString("pt-BR")} membros
                      </span>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-slate-600 leading-relaxed line-clamp-2">
                    {community.description || "Nenhuma descrição fornecida."}
                  </p>
                </div>

                {/* Footer Action */}
                <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[10px] text-slate-400">
                    Criada em {new Date(community.created_at).toLocaleDateString("pt-BR")}
                  </span>

                  <div className="flex items-center gap-2">
                    {onJoinToggleCommunity && role !== "LEADER" && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onJoinToggleCommunity(community.id);
                        }}
                        className={`text-xs px-2.5 py-0.5 rounded-sm font-semibold transition-all ${
                          isMember
                            ? "border border-slate-300 text-slate-600 hover:bg-slate-100"
                            : "bg-pink-50 border border-pink-200 text-pink-700 hover:bg-pink-100"
                        }`}
                      >
                        {isMember ? "Sair" : "Participar"}
                      </button>
                    )}

                    <span className="flex items-center text-xs font-semibold text-pink-600 hover:text-pink-700">
                      Entrar
                      <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                    </span>
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      ) : (
        <div className="panel-classic p-8 text-center text-slate-500">
          <Users className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-xs font-semibold text-slate-700">
            Nenhuma comunidade encontrada.
          </p>
          <p className="text-[11px] text-slate-400 mt-1">
            Tente buscar com outros termos ou crie sua própria comunidade!
          </p>
        </div>
      )}

      {/* Create Community Modal */}
      {isCreateModalOpen && (
        <CreateCommunityModal
          currentUser={currentUser}
          onClose={() => setIsCreateModalOpen(false)}
          onCommunityCreated={(newComm) => {
            if (onCommunityCreated) onCommunityCreated(newComm);
            onSelectCommunity(newComm);
          }}
        />
      )}

    </div>
  );
};
