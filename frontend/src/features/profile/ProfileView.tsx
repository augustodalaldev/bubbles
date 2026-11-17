import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { BubblegramBall } from "./BubblegramBall";
import { BubblepopStory } from "./BubblepopStory";
import { PostDetailModal } from "./PostDetailModal";
import { Bubblegram, Bubblepop, Community, FollowItem, Letter, User } from "@/types";
import { Avatar } from "@/components/Avatar";
import { SoapIcon } from "@/components/SoapIcon";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { CreateBubblepopModal } from "@/features/feed/CreateBubblepopModal";
import { listCommunities } from "@/services/communities";
import { errorMessage, toApiError } from "@/services/errors";
import { listInbox } from "@/services/letters";
import {
  followUser,
  getProfile,
  listFollowers,
  listUserBubblegrams,
  listUserBubblepops,
  unfollowUser,
} from "@/services/users";
import { timeAgo } from "@/utils/time";
import { UserPlus, Mail, Calendar, Layers, Grid, Plus, Clock, ShoppingBag } from "lucide-react";

interface ProfileViewProps {
  /** Profile to show; null means the signed-in user's own profile. */
  username: string | null;
}

/** Spreads real posts over the mural: two columns, growing downwards. */
const layoutFor = (index: number) => ({
  initialX: 20 + (index % 2) * 250 + ((index * 37) % 30),
  initialY: 10 + Math.floor(index / 2) * 215,
});

export const ProfileView: React.FC<ProfileViewProps> = ({
  username,
}) => {
  const me = useAuthStore((s) => s.user)!;
  const economy = useAuthStore((s) => s.economy);
  const isOwn = username === null || username === me.username;
  const targetUsername = isOwn ? me.username : username;

  const [other, setOther] = useState<User | null>(null);
  const [profileStatus, setProfileStatus] = useState<"loading" | "ready" | "error">(isOwn ? "ready" : "loading");
  const [profileError, setProfileError] = useState<string | null>(null);

  const [posts, setPosts] = useState<Bubblegram[]>([]);
  const [postsCount, setPostsCount] = useState(0);
  const [nextPage, setNextPage] = useState<number | null>(null);
  const [postsStatus, setPostsStatus] = useState<"loading" | "ready" | "error">("loading");
  const [postsError, setPostsError] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const [bubblepops, setBubblepops] = useState<Bubblepop[]>([]);
  const [followers, setFollowers] = useState<FollowItem[]>([]);
  const [myCommunities, setMyCommunities] = useState<Community[]>([]);
  const [recentLetters, setRecentLetters] = useState<Letter[]>([]);

  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);
  const [selectedStory, setSelectedStory] = useState<Bubblepop | null>(null);
  const [creatingPop, setCreatingPop] = useState(false);
  const [viewMode, setViewMode] = useState<"physics" | "grid">("physics");
  const [followBusy, setFollowBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const playgroundRef = useRef<HTMLDivElement>(null);

  const profile: User | null = isOwn ? me : other;

  const loadProfile = useCallback(async () => {
    if (isOwn) return;
    setProfileStatus("loading");
    setProfileError(null);
    try {
      setOther(await getProfile(targetUsername));
      setProfileStatus("ready");
    } catch (err) {
      setProfileError(toApiError(err).status === 404 ? "Perfil não encontrado." : errorMessage(err));
      setProfileStatus("error");
    }
  }, [isOwn, targetUsername]);

  const loadPosts = useCallback(
    async (page: number, reset: boolean) => {
      if (reset) setPostsStatus("loading");
      else setLoadingMore(true);
      try {
        const data = await listUserBubblegrams(targetUsername, page);
        setPosts((prev) => (reset ? data.results : [...prev, ...data.results]));
        setPostsCount(data.count);
        setNextPage(data.next ? page + 1 : null);
        setPostsStatus("ready");
      } catch (err) {
        setPostsError(errorMessage(err));
        if (reset) setPostsStatus("error");
      } finally {
        setLoadingMore(false);
      }
    },
    [targetUsername]
  );

  const loadSide = useCallback(async () => {
    const [pops, fol, comms, inbox] = await Promise.allSettled([
      listUserBubblepops(targetUsername),
      listFollowers(targetUsername, 1),
      isOwn ? listCommunities({ mine: true }) : Promise.resolve(null),
      isOwn ? listInbox(1) : Promise.resolve(null),
    ]);
    setBubblepops(pops.status === "fulfilled" ? pops.value : []);
    setFollowers(fol.status === "fulfilled" ? fol.value.results : []);
    setMyCommunities(comms.status === "fulfilled" && comms.value ? comms.value.results : []);
    setRecentLetters(inbox.status === "fulfilled" && inbox.value ? inbox.value.results.slice(0, 3) : []);
  }, [targetUsername, isOwn]);

  useEffect(() => {
    void loadProfile();
    void loadPosts(1, true);
    void loadSide();
  }, [loadProfile, loadPosts, loadSide]);

  const toggleFollow = async () => {
    if (!profile || followBusy) return;
    setFollowBusy(true);
    setActionError(null);
    try {
      if (profile.is_following) await unfollowUser(profile.username);
      else await followUser(profile.username);
      await Promise.all([loadProfile(), loadSide()]);
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setFollowBusy(false);
    }
  };

  if (profileStatus === "loading" || !profile) {
    return (
      <main className="max-w-7xl mx-auto px-4 py-10">
        {profileStatus === "error" ? (
          <ErrorState message={profileError ?? "Não foi possível carregar o perfil."} onRetry={() => void loadProfile()} />
        ) : (
          <LoadingState label="Carregando perfil..." />
        )}
      </main>
    );
  }

  const formattedJoinDate = new Date(profile.created_at).toLocaleDateString("pt-BR", { month: "short", year: "numeric" });
  const formattedBirthDate = profile.birth_date
    ? new Date(profile.birth_date + "T00:00:00").toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" })
    : "";
  const muralHeight = Math.max(580, Math.ceil(posts.length / 2) * 215 + 40);

  const replacePost = (updated: Bubblegram) => {
    setPosts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
    setSelectedPost(updated);
  };

  return (
    <main className="max-w-7xl mx-auto px-4 py-5">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* LEFT: profile and letters */}
        <div className="lg:col-span-3 space-y-4">
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-sm sm:text-base font-bold text-slate-800">Perfil</span>
            </div>

            <div className="p-4 text-center flex flex-col items-center">
              <Avatar user={profile} className="w-24 h-24 mb-3 text-2xl" />
              <h1 className="text-base font-bold text-slate-900 leading-tight">{profile.name}</h1>
              <p className="text-xs text-pink-600 font-semibold mb-2">@{profile.username}</p>
              {profile.description && (
                <p className="text-xs text-slate-600 leading-relaxed text-center px-1 mb-3 whitespace-pre-wrap break-words">
                  {profile.description}
                </p>
              )}

              {!isOwn && (
                <div className="w-full grid grid-cols-2 gap-2 mb-4">
                  <button
                    onClick={() => void toggleFollow()}
                    disabled={followBusy}
                    className={`py-1.5 px-2 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all disabled:opacity-60 ${
                      profile.is_following ? "btn-outline" : "btn-pink"
                    }`}
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                    {profile.is_following ? "Seguindo" : "Seguir"}
                  </button>
                  <Link to={paths.lettersTo(profile.username)}
                    
                    title="Enviar uma carta"
                    className="btn-purple py-1.5 px-2 text-xs font-semibold flex items-center justify-center gap-1.5"
                  >
                    <Mail className="w-3.5 h-3.5" />
                    Carta
                  </Link>
                </div>
              )}
              {actionError && (
                <p role="alert" className="w-full mb-2 text-[11px] text-red-700">
                  {actionError}
                </p>
              )}

              <div className="w-full pt-3 border-t border-slate-200 text-left space-y-1.5 text-xs text-slate-600">
                {formattedBirthDate && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" />
                      Nascimento:
                    </span>
                    <span className="font-semibold text-slate-700">{formattedBirthDate}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Clock className="w-3 h-3" />
                    Membro desde:
                  </span>
                  <span className="font-semibold text-slate-700">{formattedJoinDate}</span>
                </div>
              </div>

              <div className="w-full mt-3 pt-3 border-t border-slate-200 grid grid-cols-3 text-center">
                <div>
                  <span className="block text-sm font-bold text-slate-800">{postsCount}</span>
                  <span className="text-[10px] text-slate-400">Bolhas</span>
                </div>
                <div>
                  <span className="block text-sm font-bold text-slate-800">{profile.followers_count ?? 0}</span>
                  <span className="text-[10px] text-slate-400">Seguidores</span>
                </div>
                <div>
                  <span className="block text-sm font-bold text-slate-800">{profile.following_count ?? 0}</span>
                  <span className="text-[10px] text-slate-400">Seguindo</span>
                </div>
              </div>
            </div>
          </div>

          {isOwn && (
            <div className="panel-classic">
              <div className="panel-classic-header">
                <span className="text-sm sm:text-base font-bold text-slate-800">Cartas</span>
                <Link to={paths.letters}  className="text-xs text-pink-600 font-semibold hover:underline">
                  Abrir caixa postal
                </Link>
              </div>
              <div className="p-3 space-y-2.5">
                {recentLetters.length === 0 ? (
                  <EmptyState message="Nenhuma carta recebida" />
                ) : (
                  recentLetters.map((letter) => (
                    <div key={letter.id} className="p-2.5 bg-slate-50 border border-slate-200 rounded-sm">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <Avatar user={letter.sender} className="w-5 h-5 text-[9px]" />
                          <span className="text-xs font-bold text-slate-800 truncate">{letter.sender.name}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 flex-shrink-0">{timeAgo(letter.sent_at)}</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-snug line-clamp-2">{letter.text}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* CENTER: bubblepops and mural */}
        <div className="lg:col-span-6 space-y-4">
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-sm sm:text-base font-bold text-slate-800">Bubblepops</span>
              {isOwn && (
                <button
                  onClick={() => setCreatingPop(true)}
                  title="Criar um bubblepop"
                  className="btn-outline py-0.5 px-2.5 text-xs font-semibold flex items-center gap-1"
                >
                  <Plus className="w-3.5 h-3.5 text-pink-600" />
                  Novo
                </button>
              )}
            </div>
            <div className="p-3 flex items-center gap-3 overflow-x-auto min-h-[92px]">
              {bubblepops.length === 0 ? (
                <p className="text-xs text-slate-400">Nenhum bubblepop ativo.</p>
              ) : (
                bubblepops.map((story) => <BubblepopStory key={story.id} story={story} onClick={setSelectedStory} />)
              )}
            </div>
          </div>

          <div className="panel-classic flex flex-col">
            <div className="panel-classic-header">
              <div className="flex items-center gap-2">
                <span className="text-sm sm:text-base font-bold text-slate-800">Mural de bolhas</span>
                <span className="text-xs font-normal text-slate-400">({postsCount})</span>
              </div>
              <div className="flex items-center bg-slate-100 p-0.5 border border-slate-300 rounded-sm">
                <button
                  onClick={() => setViewMode("physics")}
                  className={`px-2 py-0.5 text-xs font-semibold flex items-center gap-1 rounded-sm transition-all ${
                    viewMode === "physics" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  <Layers className="w-3 h-3 text-pink-500" />
                  Mural
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`px-2 py-0.5 text-xs font-semibold flex items-center gap-1 rounded-sm transition-all ${
                    viewMode === "grid" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  <Grid className="w-3 h-3 text-slate-500" />
                  Grade
                </button>
              </div>
            </div>

            <div className="p-3">
              {postsStatus === "loading" ? (
                <LoadingState label="Carregando bolhas..." />
              ) : postsStatus === "error" ? (
                <ErrorState message={postsError ?? "Não foi possível carregar as bolhas."} onRetry={() => void loadPosts(1, true)} />
              ) : posts.length === 0 ? (
                <EmptyState
                  message={isOwn ? "Você ainda não publicou nenhuma bolha" : "Nenhuma bolha publicada"}
                  hint={isOwn ? "Use o botão + no feed para publicar." : undefined}
                />
              ) : viewMode === "physics" ? (
                <div
                  ref={playgroundRef}
                  style={{ height: muralHeight }}
                  className="relative w-full bg-slate-50 border border-slate-200 overflow-hidden"
                >
                  <div className="absolute inset-x-0 bottom-2 text-center pointer-events-none select-none">
                    <span className="text-[10px] text-slate-400 font-medium bg-white/80 px-2 py-0.5 border border-slate-200 rounded-sm">
                      Arraste as bolhas pela tela
                    </span>
                  </div>
                  {posts.map((post, index) => (
                    <BubblegramBall
                      key={post.id}
                      post={{ ...post, ...layoutFor(index) }}
                      dragConstraintsRef={playgroundRef}
                      onClick={setSelectedPost}
                    />
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {posts.map((post) => (
                    <button
                      key={post.id}
                      onClick={() => setSelectedPost(post)}
                      className="text-left bg-white border border-slate-200 p-2 hover:border-pink-300 transition-colors"
                    >
                      <div className="aspect-square bg-slate-100 overflow-hidden relative flex items-center justify-center">
                        {post.media.length > 0 ? (
                          <img src={post.media[0].media} alt="Mídia" className="w-full h-full object-cover" />
                        ) : (
                          <p className="text-xs text-slate-600 font-medium p-3 text-center line-clamp-4">{post.text}</p>
                        )}
                        <span className="absolute bottom-1 right-1 px-1.5 py-0.5 bg-slate-900/80 text-white text-[10px] font-bold rounded-sm flex items-center gap-1">
                          <SoapIcon size={14} />
                          {post.soap_count}
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 font-medium mt-1.5 truncate">{post.text}</p>
                    </button>
                  ))}
                </div>
              )}

              {postsStatus === "ready" && nextPage !== null && (
                <div className="text-center mt-3">
                  <button
                    onClick={() => void loadPosts(nextPage, false)}
                    disabled={loadingMore}
                    className="btn-outline px-4 py-1.5 text-xs font-semibold"
                  >
                    {loadingMore ? "Carregando..." : "Carregar mais bolhas"}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT: wallet (own), followers, communities (own) */}
        <div className="lg:col-span-3 space-y-4">
          {isOwn && (
            <div className="panel-classic">
              <div className="panel-classic-header">
                <span className="text-sm sm:text-base font-bold text-slate-800">Carteira de soap</span>
                <span className="font-bold text-pink-600 text-sm flex items-center gap-1.5">
                  <SoapIcon size={22} />
                  {me.soap_balance ?? 0} soap
                </span>
              </div>
              <div className="p-3 text-xs text-slate-600">
                {economy && (
                  <p className="leading-snug">
                    Ganho passivo: <strong>+{economy.default_passive_earn_rate} soap</strong> a cada{" "}
                    {economy.passive_interval_minutes} min de uso, até {economy.passive_daily_cap} por dia.
                  </p>
                )}
                <Link to={paths.store}
                  
                  className="mt-2.5 w-full btn-outline py-1.5 px-3 text-xs font-semibold flex items-center justify-center gap-1.5 text-slate-700 hover:text-pink-600"
                >
                  <ShoppingBag className="w-3.5 h-3.5 text-pink-500" />
                  Loja de personalização
                </Link>
              </div>
            </div>
          )}

          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-sm sm:text-base font-bold text-slate-800">Seguidores ({profile.followers_count ?? 0})</span>
            </div>
            <div className="p-3">
              {followers.length === 0 ? (
                <p className="text-xs text-slate-400">Ainda sem seguidores.</p>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {followers.slice(0, 6).map(({ id, user }) => (
                    <Link to={paths.profile(user.username)} key={id}  className="flex flex-col items-center group">
                      <Avatar user={user} className="w-14 h-14 group-hover:opacity-90" />
                      <span className="text-[11px] font-medium text-slate-700 mt-1 truncate max-w-[65px] text-center group-hover:text-pink-600">
                        {user.name.split(" ")[0]}
                      </span>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          {isOwn && (
            <div className="panel-classic">
              <div className="panel-classic-header">
                <span className="text-sm sm:text-base font-bold text-slate-800">Comunidades ({myCommunities.length})</span>
                <Link to={paths.communities}  className="text-xs text-pink-600 font-semibold hover:underline">
                  ver todas
                </Link>
              </div>
              <div className="p-3 space-y-2">
                {myCommunities.length === 0 ? (
                  <p className="text-xs text-slate-400">Você ainda não participa de comunidades.</p>
                ) : (
                  myCommunities.map((comm) => (
                    <Link to={paths.community(comm.commname)}
                      key={comm.id}
                      
                      className="w-full flex items-center gap-2.5 p-1.5 hover:bg-slate-50 transition-colors group rounded-sm text-left"
                    >
                      {comm.community_photo ? (
                        <img src={comm.community_photo} alt={comm.name} className="w-9 h-9 object-cover rounded-sm" />
                      ) : (
                        <span className="w-9 h-9 rounded-sm bg-purple-50 text-purple-700 text-xs font-bold flex items-center justify-center">
                          {comm.name.charAt(0).toUpperCase()}
                        </span>
                      )}
                      <div className="flex-1 min-w-0">
                        <h4 className="text-xs font-semibold text-slate-800 truncate group-hover:text-pink-600">{comm.name}</h4>
                        <span className="text-[10px] text-slate-400">{comm.member_count.toLocaleString("pt-BR")} membros</span>
                      </div>
                    </Link>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {creatingPop && (
        <CreateBubblepopModal onClose={() => setCreatingPop(false)} onCreated={(pop) => setBubblepops((prev) => [...prev, pop])} />
      )}

      {(selectedPost || selectedStory) && (
        <PostDetailModal
          post={selectedPost}
          story={selectedStory}
          onClose={() => {
            setSelectedPost(null);
            setSelectedStory(null);
          }}
          onPostUpdate={replacePost}
          onPostDeleted={(id) => {
            setPosts((prev) => prev.filter((p) => p.id !== id));
            setPostsCount((n) => Math.max(0, n - 1));
          }}
          onStoryDeleted={(id) => setBubblepops((prev) => prev.filter((b) => b.id !== id))}
        />
      )}
    </main>
  );
};
