import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Bubblegram, Bubblepop, Community, SearchResult } from "@/types";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { PostDetailModal } from "@/features/profile/PostDetailModal";
import { getFeed, getFeedBubblepops } from "@/services/feed";
import { listCommunities } from "@/services/communities";
import { listInbox } from "@/services/letters";
import { search } from "@/services/users";
import { errorMessage } from "@/services/errors";
import { CheckCircle2 } from "lucide-react";
import { CreateBubblePopup } from "./CreateBubblePopup";
import { FeedBubblepopsTray } from "./FeedBubblepopsTray";
import { FeedItemCard } from "./FeedItemCard";
import { FeedSidebarLeft } from "./FeedSidebarLeft";
import { FeedSidebarRight } from "./FeedSidebarRight";
import { SearchResultsPanel } from "./SearchResultsPanel";

interface FeedViewProps {
  /** Search term from the URL (`?q=`). */
  searchTerm?: string;
}

type FeedFilter = "all" | "following" | "communities";

const FILTERS: { id: FeedFilter; label: string }[] = [
  { id: "all", label: "Todos" },
  { id: "following", label: "Seguindo" },
  { id: "communities", label: "Comunidades" },
];

export const FeedView: React.FC<FeedViewProps> = ({ searchTerm = "" }) => {
  const currentUser = useAuthStore((s) => s.user)!;

  const [posts, setPosts] = useState<Bubblegram[]>([]);
  const [nextPage, setNextPage] = useState<number | null>(1);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FeedFilter>("all");

  const [bubblepops, setBubblepops] = useState<Bubblepop[]>([]);
  const [myCommunities, setMyCommunities] = useState<Community[] | null>(null);
  const [communitiesError, setCommunitiesError] = useState<string | null>(null);
  const [unreadLetters, setUnreadLetters] = useState(0);

  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);
  const [selectedStory, setSelectedStory] = useState<Bubblepop | null>(null);

  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [searching, setSearching] = useState(false);

  const loadFeed = useCallback(async (page: number, reset: boolean) => {
    if (reset) setStatus("loading");
    else setLoadingMore(true);
    try {
      const data = await getFeed(page);
      // Suggestions are recomputed per page, so the same post can reappear: dedupe by id.
      setPosts((prev) => {
        const base = reset ? [] : prev;
        const seen = new Set(base.map((p) => p.id));
        return [...base, ...data.results.filter((p) => !seen.has(p.id))];
      });
      setNextPage(data.next ? page + 1 : null);
      setStatus("ready");
    } catch (err) {
      setError(errorMessage(err));
      if (reset) setStatus("error");
    } finally {
      setLoadingMore(false);
    }
  }, []);

  const loadSideData = useCallback(async () => {
    setCommunitiesError(null);
    const [pops, communities, inbox] = await Promise.allSettled([
      getFeedBubblepops(),
      listCommunities({ mine: true }),
      listInbox(1),
    ]);
    if (pops.status === "fulfilled") setBubblepops(pops.value);
    if (communities.status === "fulfilled") setMyCommunities(communities.value.results);
    else setCommunitiesError(errorMessage(communities.reason));
    if (inbox.status === "fulfilled") setUnreadLetters(inbox.value.results.filter((l) => !l.is_read).length);
  }, []);

  useEffect(() => {
    void loadFeed(1, true);
    void loadSideData();
  }, [loadFeed, loadSideData]);

  const term = searchTerm.trim();
  const runSearch = useCallback(async () => {
    setSearching(true);
    setSearchError(null);
    try {
      setSearchResult(await search(term));
    } catch (err) {
      setSearchError(errorMessage(err));
    } finally {
      setSearching(false);
    }
  }, [term]);

  useEffect(() => {
    if (!term) {
      setSearchResult(null);
      return;
    }
    const timer = window.setTimeout(() => void runSearch(), 300);
    return () => window.clearTimeout(timer);
  }, [term, runSearch]);

  const visiblePosts = useMemo(() => {
    if (filter === "following") return posts.filter((p) => p.community === null && !p.is_suggested);
    if (filter === "communities") return posts.filter((p) => p.community !== null);
    return posts;
  }, [posts, filter]);

  const replacePost = (updated: Bubblegram) => {
    setPosts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  };
  const removePost = (id: number) => setPosts((prev) => prev.filter((p) => p.id !== id));

  return (
    <div className="max-w-7xl mx-auto px-4 py-3 lg:h-[calc(100vh-3.5rem)] lg:overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start lg:h-full">
        <div className="lg:col-span-3 lg:h-full lg:overflow-y-auto scrollbar-none">
          <FeedSidebarLeft
            currentUser={currentUser}
            unreadLettersCount={unreadLetters}
          />
        </div>

        <div className="lg:col-span-6 min-w-0 lg:h-full lg:overflow-y-auto pr-1.5 scrollbar-thin">
          <FeedBubblepopsTray
            bubblepops={bubblepops}
            onSelectBubblepop={(story) => setSelectedStory(story)}
          />

          {term ? (
            <SearchResultsPanel
              term={term}
              result={searchResult}
              error={searchError}
              loading={searching}
              onRetry={() => void runSearch()}
            />
          ) : (
            <>
              <div className="panel-classic mb-4">
                <div className="p-2 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-1" role="tablist">
                    {FILTERS.map((f) => (
                      <button
                        key={f.id}
                        role="tab"
                        aria-selected={filter === f.id}
                        onClick={() => setFilter(f.id)}
                        className={`px-2.5 py-1 text-xs font-semibold rounded-sm transition-all ${
                          filter === f.id
                            ? "bg-pink-600 text-white shadow-xs"
                            : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                        }`}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium">
                    {visiblePosts.length} publicaç{visiblePosts.length === 1 ? "ão" : "ões"}
                  </div>
                </div>
              </div>

              {status === "loading" ? (
                <LoadingState label="Carregando o feed..." />
              ) : status === "error" ? (
                <ErrorState message={error ?? "Não foi possível carregar o feed."} onRetry={() => void loadFeed(1, true)} />
              ) : visiblePosts.length === 0 ? (
                <div className="panel-classic">
                  <EmptyState
                    message="Nenhuma bolha por aqui"
                    hint="Siga pessoas, entre em comunidades ou publique pelo botão + no canto inferior direito."
                  />
                </div>
              ) : (
                <div className="space-y-4">
                  {visiblePosts.map((post) => (
                    <FeedItemCard
                      key={post.id}
                      post={post}
                      onOpenDetail={(p) => setSelectedPost(p)}
                      onDeleted={removePost}
                    />
                  ))}
                </div>
              )}

              {status === "ready" && nextPage !== null && (
                <div className="text-center my-4">
                  <button
                    onClick={() => void loadFeed(nextPage, false)}
                    disabled={loadingMore}
                    className="btn-outline px-4 py-1.5 text-xs font-semibold"
                  >
                    {loadingMore ? "Carregando..." : "Carregar mais"}
                  </button>
                  {error && <p role="alert" className="mt-1 text-[11px] text-red-700">{error}</p>}
                </div>
              )}

              {status === "ready" && nextPage === null && posts.length > 0 && (
                <div className="panel-classic mt-6 mb-6 p-4 text-center bg-slate-50/70 border border-slate-200">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
                  <h3 className="text-xs font-bold text-slate-800">Você está em dia com as novidades</h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">Não há mais publicações por enquanto.</p>
                </div>
              )}
            </>
          )}

          <div className="py-4 text-center text-[11px] text-slate-400">Bubbles • Rede Social</div>
        </div>

        <div className="lg:col-span-3 lg:h-full lg:overflow-y-auto scrollbar-none hidden lg:block">
          <FeedSidebarRight
            communities={myCommunities}
            error={communitiesError}
            onRetry={() => void loadSideData()}
          />
        </div>
      </div>

      <CreateBubblePopup
        onPostCreated={(post) => setPosts((prev) => [post, ...prev])}
        onPopCreated={(pop) => setBubblepops((prev) => [...prev, pop])}
      />

      {(selectedPost || selectedStory) && (
        <PostDetailModal
          post={selectedPost}
          story={selectedStory}
          stories={bubblepops}
          onStoryChange={setSelectedStory}
          onClose={() => {
            setSelectedPost(null);
            setSelectedStory(null);
          }}
          onPostUpdate={(updated) => {
            replacePost(updated);
            setSelectedPost(updated);
          }}
          onPostDeleted={removePost}
          onStoryDeleted={(id) => setBubblepops((prev) => prev.filter((b) => b.id !== id))}
        />
      )}
    </div>
  );
};
