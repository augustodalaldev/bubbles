import React, { useState, useMemo } from "react";
import { Bubblegram, Bubblepop, Community, User } from "@/types";
import { 
  MOCK_USER, 
  MOCK_COMMUNITIES, 
  MOCK_FEED_BUBBLEGRAMS, 
  MOCK_FEED_BUBBLEPOPS, 
  MOCK_SUGGESTED_USERS 
} from "@/features/profile/mockData";
import { FeedBubblepopsTray } from "./FeedBubblepopsTray";
import { CreateBubblePopup } from "./CreateBubblePopup";
import { FeedItemCard } from "./FeedItemCard";
import { FeedSidebarLeft } from "./FeedSidebarLeft";
import { FeedSidebarRight } from "./FeedSidebarRight";
import { PostDetailModal } from "@/features/profile/PostDetailModal";
import { CheckCircle2, Compass, Search, X } from "lucide-react";

interface FeedViewProps {
  onNavigateToProfile: () => void;
  onNavigateToView?: (view: string) => void;
  onSelectCommunity?: (community: Community) => void;
  searchTerm?: string;
  onClearSearch?: () => void;
}

export const FeedView: React.FC<FeedViewProps> = ({
  onNavigateToProfile,
  onNavigateToView,
  onSelectCommunity,
  searchTerm = "",
  onClearSearch,
}) => {
  const [currentUser, setCurrentUser] = useState<User>(MOCK_USER);
  const [bubblegrams, setBubblegrams] = useState<Bubblegram[]>(MOCK_FEED_BUBBLEGRAMS);
  const [bubblepops] = useState<Bubblepop[]>(MOCK_FEED_BUBBLEPOPS);
  const [activeFilter, setActiveFilter] = useState<"all" | "following" | "communities" | "popular">("all");

  // Modal inspection state
  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);
  const [selectedStory, setSelectedStory] = useState<Bubblepop | null>(null);

  // Handle post creation with soap deduction
  const handlePostCreated = (newPost: Bubblegram) => {
    setBubblegrams((prev) => [newPost, ...prev]);
  };

  const handleDeductSoap = (amount: number) => {
    setCurrentUser((prev) => ({
      ...prev,
      soap_balance: Math.max(0, (prev.soap_balance ?? 0) - amount),
    }));
  };

  const handleDeletePost = (postId: number) => {
    setBubblegrams((prev) => prev.filter((p) => p.id !== postId));
  };

  const handleSupportPost = (postId: number) => {
    setBubblegrams((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, soap_count: p.soap_count + 1 } : p))
    );
  };

  // Filtered bubblegrams based on tab and search term
  const filteredBubblegrams = useMemo(() => {
    let list = bubblegrams;

    // Apply Tab Filter
    if (activeFilter === "following") {
      list = list.filter((p) => !p.is_suggested || p.user.id === currentUser.id);
    } else if (activeFilter === "communities") {
      list = list.filter((p) => p.community !== null);
    } else if (activeFilter === "popular") {
      list = [...list].sort((a, b) => b.soap_count - a.soap_count);
    }

    // Apply Search Term
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      list = list.filter(
        (p) =>
          p.text.toLowerCase().includes(term) ||
          p.user.name.toLowerCase().includes(term) ||
          p.user.username.toLowerCase().includes(term) ||
          (p.community && p.community.name.toLowerCase().includes(term))
      );
    }

    return list;
  }, [bubblegrams, activeFilter, searchTerm, currentUser.id]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-3 h-[calc(100vh-3.5rem)] overflow-hidden">
      
      {/* 3-Column Classic Grid (Left 3 cols, Center 6 cols, Right 3 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start h-full">
        
        {/* Left Sidebar (3 Cols) - Static / Follows the View without scroll */}
        <div className="lg:col-span-3 h-full overflow-y-auto scrollbar-none hidden lg:block">
          <FeedSidebarLeft
            currentUser={currentUser}
            onNavigateToProfile={onNavigateToProfile}
            onNavigateToView={onNavigateToView}
            unreadLettersCount={2}
          />
        </div>

        {/* Center Stream (6 Cols) - THE ONLY SCROLLABLE AREA */}
        <div className="lg:col-span-6 min-w-0 h-full overflow-y-auto pr-1.5 scrollbar-thin">
          
          {/* Bubblepops 24h Stories Tray */}
          <FeedBubblepopsTray
            bubblepops={bubblepops}
            onSelectBubblepop={(story) => setSelectedStory(story)}
            onOpenCreateModal={() => alert("Para publicar um Bubblepop, utilize o botão de criação no perfil.")}
          />

          {/* Feed Filter Tabs & Search Indicator */}
          <div className="panel-classic mb-4">
            <div className="p-2 flex flex-wrap items-center justify-between gap-2">
              
              {/* Tab Filters */}
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setActiveFilter("all")}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeFilter === "all"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setActiveFilter("following")}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeFilter === "following"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  Seguindo
                </button>
                <button
                  onClick={() => setActiveFilter("communities")}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeFilter === "communities"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  Comunidades
                </button>
                <button
                  onClick={() => setActiveFilter("popular")}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                    activeFilter === "popular"
                      ? "bg-pink-600 text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  Em Alta
                </button>
              </div>

              {/* Feed Count Indicator */}
              <div className="text-[11px] text-slate-500 font-medium">
                {filteredBubblegrams.length} publicaç{filteredBubblegrams.length === 1 ? "ão" : "ões"}
              </div>
            </div>

            {/* Active Search Filter Badge */}
            {searchTerm.trim() && (
              <div className="px-3 py-1.5 bg-pink-50 border-t border-pink-100 flex items-center justify-between text-xs text-pink-900">
                <div className="flex items-center gap-1.5">
                  <Search className="w-3.5 h-3.5 text-pink-600" />
                  <span>Resultados para: <strong>"{searchTerm}"</strong></span>
                </div>
                {onClearSearch && (
                  <button
                    onClick={onClearSearch}
                    className="text-pink-700 hover:text-pink-900 text-xs font-bold flex items-center gap-0.5"
                  >
                    <X className="w-3.5 h-3.5" />
                    Limpar
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Posts Stream */}
          <div className="space-y-4">
            {filteredBubblegrams.length > 0 ? (
              filteredBubblegrams.map((post) => (
                <FeedItemCard
                  key={post.id}
                  post={post}
                  currentUser={currentUser}
                  onOpenDetail={(p) => setSelectedPost(p)}
                  onDeletePost={handleDeletePost}
                  onSupportPost={handleSupportPost}
                />
              ))
            ) : (
              <div className="panel-classic p-8 text-center text-slate-500">
                <Compass className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-700">
                  Nenhuma bolha encontrada.
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Tente alterar seus filtros ou publique uma nova bolha clicando no botão + no canto inferior direito.
                </p>
              </div>
            )}
          </div>

          {/* End of Feed Indicator (Orkut / Classic Style) */}
          {filteredBubblegrams.length > 0 && (
            <div className="panel-classic mt-6 mb-6 p-4 text-center bg-slate-50/70 border border-slate-200">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
              <h3 className="text-xs font-bold text-slate-800">
                Você está em dia com todas as novidades!
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Não há mais publicações recentes no momento. É tudo por hoje.
              </p>
            </div>
          )}

          {/* Classic subtle footer at the bottom of the feed stream */}
          <div className="py-4 text-center text-[11px] text-slate-400">
            Bubbles • Rede Social
          </div>

        </div>

        {/* Right Sidebar (3 Cols) - Static / Follows the View without scroll */}
        <div className="lg:col-span-3 h-full overflow-y-auto scrollbar-none hidden lg:block">
          <FeedSidebarRight
            communities={MOCK_COMMUNITIES}
            suggestedUsers={MOCK_SUGGESTED_USERS}
            onSelectCommunity={(comm) => {
              if (onSelectCommunity) onSelectCommunity(comm);
              else onNavigateToView?.("communities");
            }}
            onSelectUser={(username) => alert(`Perfil selecionado: @${username}`)}
          />
        </div>

      </div>

      {/* Floating Action Button & Popup in the Bottom-Left */}
      <CreateBubblePopup
        currentUser={currentUser}
        onPostCreated={handlePostCreated}
        onDeductSoap={handleDeductSoap}
      />

      {/* Post & Story Detail Inspection Modal */}
      {(selectedPost || selectedStory) && (
        <PostDetailModal
          post={selectedPost}
          story={selectedStory}
          currentUser={currentUser}
          onClose={() => {
            setSelectedPost(null);
            setSelectedStory(null);
          }}
        />
      )}

    </div>
  );
};
