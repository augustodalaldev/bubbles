import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { Bubblegram, Community, CommunityMemberItem } from "@/types";
import { Avatar } from "@/components/Avatar";
import { UserName } from "@/components/UserName";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { SoapIcon } from "@/components/SoapIcon";
import { formatUntil } from "@/components/ModerationBanner";
import { NotFoundView } from "@/components/NotFoundView";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { FeedItemCard } from "@/features/feed/FeedItemCard";
import { PostDetailModal } from "@/features/profile/PostDetailModal";
import { CommunityCustomizationPanel } from "@/features/customization/CommunityCustomizationPanel";
import { createBubblegram } from "@/services/content";
import {
  getCommunity,
  getCommunityWallet,
  joinCommunity,
  leaveCommunity,
  listCommunityBubblegrams,
  listMembers,
  updateGuidelines,
} from "@/services/communities";
import { errorMessage, toApiError } from "@/services/errors";
import {
  ArrowLeft,
  ShieldCheck,
  FileText,
  Image as ImageIcon,
  UploadCloud,
  BookOpen,
  Check,
  AlertCircle,
  X,
  Send,
} from "lucide-react";

interface CommunityDetailViewProps {
  commname: string;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // mirrors the server limit, only to fail fast

const MemberLine: React.FC<{
  member: CommunityMemberItem;
  badge?: { label: string; className: string };
}> = ({ member, badge }) => (
  <Link to={paths.profile(member.user.username)}
    
    className="w-full py-2 flex items-center justify-between gap-3 text-left first:pt-0 last:pb-0"
  >
    <span className="flex items-center gap-2.5 min-w-0">
      <Avatar user={member.user} className="w-8 h-8 flex-shrink-0" />
      <span className="min-w-0">
        <span className="flex items-center gap-1.5">
          <UserName user={member.user} className="text-xs font-bold text-slate-800 truncate" />
          {badge && (
            <span className={`text-[10px] font-bold px-1.5 rounded-sm border ${badge.className}`}>{badge.label}</span>
          )}
          {member.current_state !== "ACTIVE" && (
            <span className="text-[10px] font-bold px-1.5 rounded-sm border border-slate-300 text-slate-600 bg-slate-100">
              {member.current_state === "SILENCED" ? "Silenciado" : "Banido"}
            </span>
          )}
        </span>
        <span className="text-[10px] text-slate-400">@{member.user.username}</span>
      </span>
    </span>
    <span className="text-[10px] text-slate-400 flex-shrink-0">
      Entrou em {new Date(member.joined_at).toLocaleDateString("pt-BR")}
    </span>
  </Link>
);

const NOT_FOUND = "not_found";

export const CommunityDetailView: React.FC<CommunityDetailViewProps> = ({ commname }) => {
  const economy = useAuthStore((s) => s.economy);
  const isStaff = useAuthStore((s) => s.user?.is_staff);
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const [community, setCommunity] = useState<Community | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"posts" | "guidelines" | "members" | "customization">("posts");
  const [walletBalance, setWalletBalance] = useState<number | null>(null);

  const [posts, setPosts] = useState<Bubblegram[]>([]);
  const [postsCount, setPostsCount] = useState(0);
  const [postsNext, setPostsNext] = useState<number | null>(null);
  const [postsStatus, setPostsStatus] = useState<"loading" | "ready" | "error">("loading");
  const [postsError, setPostsError] = useState<string | null>(null);
  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);

  const [members, setMembers] = useState<CommunityMemberItem[]>([]);
  const [membersCount, setMembersCount] = useState(0);
  const [membersNext, setMembersNext] = useState<number | null>(null);
  const [membersStatus, setMembersStatus] = useState<"loading" | "ready" | "error">("loading");
  const [membersError, setMembersError] = useState<string | null>(null);

  const [membershipBusy, setMembershipBusy] = useState(false);
  const [membershipError, setMembershipError] = useState<string | null>(null);

  const [postTab, setPostTab] = useState<"text" | "photo">("text");
  const [postText, setPostText] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoDataUrl, setPhotoDataUrl] = useState<string | null>(null);
  const [loadingPost, setLoadingPost] = useState(false);
  const [postError, setPostError] = useState<string | null>(null);
  const [postSuccess, setPostSuccess] = useState(false);

  const [isEditingGuidelines, setIsEditingGuidelines] = useState(false);
  const [guidelinesText, setGuidelinesText] = useState("");
  const [guidelinesError, setGuidelinesError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadCommunity = useCallback(async () => {
    try {
      const data = await getCommunity(commname);
      setCommunity(data);
      setGuidelinesText(data.guidelines ?? "");
      setStatus("ready");
      if (data.permissions?.can_view_wallet) {
        getCommunityWallet(commname)
          .then((w) => setWalletBalance(w.soap_balance))
          .catch(() => setWalletBalance(null));
      } else {
        setWalletBalance(null);
      }
    } catch (err) {
      setLoadError(toApiError(err).status === 404 ? NOT_FOUND : errorMessage(err));
      setStatus("error");
    }
  }, [commname]);

  const loadPosts = useCallback(
    async (page: number, reset: boolean) => {
      if (reset) setPostsStatus("loading");
      try {
        const data = await listCommunityBubblegrams(commname, page);
        setPosts((prev) => (reset ? data.results : [...prev, ...data.results]));
        setPostsCount(data.count);
        setPostsNext(data.next ? page + 1 : null);
        setPostsStatus("ready");
      } catch (err) {
        setPostsError(errorMessage(err));
        if (reset) setPostsStatus("error");
      }
    },
    [commname]
  );

  const loadMembers = useCallback(
    async (page: number, reset: boolean) => {
      if (reset) setMembersStatus("loading");
      try {
        const data = await listMembers(commname, page);
        setMembers((prev) => (reset ? data.results : [...prev, ...data.results]));
        setMembersCount(data.count);
        setMembersNext(data.next ? page + 1 : null);
        setMembersStatus("ready");
      } catch (err) {
        setMembersError(errorMessage(err));
        if (reset) setMembersStatus("error");
      }
    },
    [commname]
  );

  useEffect(() => {
    setStatus("loading");
    void loadCommunity();
    void loadPosts(1, true);
    void loadMembers(1, true);
  }, [loadCommunity, loadPosts, loadMembers]);

  if (status === "loading") return <LoadingState label="Carregando comunidade..." />;
  if (loadError === NOT_FOUND) return <NotFoundView message="Esta comunidade não existe ou foi excluída." />;
  if (status === "error" || !community) {
    return (
      <div className="max-w-xl mx-auto px-4 py-10">
        <ErrorState message={loadError ?? "Não foi possível carregar a comunidade."} onRetry={() => void loadCommunity()} />
        <div className="text-center">
          <Link to={paths.communities}  className="text-xs text-pink-600 hover:underline">
            Voltar para comunidades
          </Link>
        </div>
      </div>
    );
  }

  const permissions = community.permissions;
  const myRole = community.my_membership?.role;
  const myState = community.my_membership?.current_state;
  const canPost = myState === "ACTIVE" && !community.is_archived && !community.moderation;
  const postCost = economy?.bubblegram_community_cost;

  // Equipped avatar frame (a design token bought with the community's soap)
  const frame = community.customization_json?.avatar_frame?.metadata as
    | { border_color?: string; glow?: string }
    | undefined;

  const leader = members.find((m) => m.role === "LEADER");
  const admins = members.filter((m) => m.role === "COMM_ADMIN");
  const regular = members.filter((m) => m.role === "MEMBER");

  const handleMembership = async (join: boolean) => {
    setMembershipBusy(true);
    setMembershipError(null);
    try {
      if (join) await joinCommunity(commname);
      else await leaveCommunity(commname);
      await Promise.all([loadCommunity(), loadMembers(1, true)]);
    } catch (err) {
      setMembershipError(errorMessage(err));
    } finally {
      setMembershipBusy(false);
    }
  };

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPostError(null);
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_FILE_SIZE) {
      setPostError(`O arquivo possui ${(file.size / (1024 * 1024)).toFixed(1)} MB e ultrapassa o limite de 10 MB.`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }
    setPhoto(file);
    const reader = new FileReader();
    reader.onload = () => setPhotoDataUrl(reader.result as string);
    reader.readAsDataURL(file);
  };

  const clearPhoto = () => {
    setPhoto(null);
    setPhotoDataUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    setPostError(null);
    if (!postText.trim() && !photo) {
      setPostError("Escreva uma mensagem ou anexe uma foto para publicar.");
      return;
    }
    if (postTab === "photo" && !photo) {
      setPostError("Selecione uma imagem de até 10 MB na aba Foto.");
      return;
    }
    setLoadingPost(true);
    try {
      const created = await createBubblegram({
        text: postText.trim(),
        files: postTab === "photo" && photo ? [photo] : [],
        commname,
      });
      setPosts((prev) => [created, ...prev]);
      setPostsCount((n) => n + 1);
      setPostText("");
      clearPhoto();
      setPostSuccess(true);
      window.setTimeout(() => setPostSuccess(false), 3000);
      await Promise.all([refreshUser(), loadCommunity()]);
    } catch (err) {
      setPostError(errorMessage(err));
    } finally {
      setLoadingPost(false);
    }
  };

  const handleSaveGuidelines = async () => {
    setGuidelinesError(null);
    try {
      const updated = await updateGuidelines(commname, guidelinesText);
      setCommunity((prev) => (prev ? { ...prev, guidelines: updated.guidelines } : prev));
      setIsEditingGuidelines(false);
    } catch (err) {
      setGuidelinesError(errorMessage(err));
    }
  };

  const removePost = (id: number) => {
    setPosts((prev) => prev.filter((p) => p.id !== id));
    setPostsCount((n) => Math.max(0, n - 1));
  };

  const tabs = [
    { id: "posts" as const, label: `Mural de bolhas (${postsCount})` },
    { id: "guidelines" as const, label: "Diretrizes" },
    { id: "members" as const, label: `Membros (${membersCount})` },
    ...(permissions?.can_customize ? [{ id: "customization" as const, label: "Personalização" }] : []),
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-3 lg:h-[calc(100vh-3.5rem)] lg:overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start lg:h-full">
        {/* Left column */}
        <div className="lg:col-span-3 lg:h-full lg:overflow-y-auto scrollbar-none space-y-4">
          <Link to={paths.communities}
            
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-pink-600 transition-colors py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Voltar para comunidades</span>
          </Link>

          <div className="panel-classic">
            <div className="p-4 text-center">
              <div
                className="relative w-20 h-20 rounded-full overflow-hidden mx-auto mb-2.5 border-2 border-slate-200 shadow-sm bg-purple-50 flex items-center justify-center text-purple-700 text-xl font-bold"
                style={
                  frame
                    ? { border: `3px solid ${frame.border_color ?? "#F465AC"}`, boxShadow: frame.glow ?? "none" }
                    : undefined
                }
              >
                {community.community_photo ? (
                  <img src={community.community_photo} alt={community.name} className="w-full h-full object-cover" />
                ) : (
                  community.name.charAt(0).toUpperCase()
                )}
                <BubbleOverlay opacity={0.4} />
              </div>

              <h1 className="text-sm font-bold text-slate-900 leading-tight">{community.name}</h1>
              <span className="text-xs text-slate-400 font-mono block mt-0.5 mb-2">@{community.commname}</span>
              {community.moderation && (
                <div role="status" className="mb-2 text-left text-[11px] bg-amber-50 border border-amber-300 text-amber-900 rounded-sm p-2">
                  <p className="font-bold">
                    {community.moderation.status === "BANNED"
                      ? "Comunidade banida: somente leitura"
                      : `Comunidade suspensa${community.moderation.suspended_until ? ` até ${formatUntil(community.moderation.suspended_until)}` : ""}: somente leitura`}
                  </p>
                  {community.moderation.reason && <p className="break-words">Motivo: {community.moderation.reason}</p>}
                </div>
              )}
              {isStaff && (
                <Link
                  to={paths.moderation({ tab: "communities", q: community.commname })}
                  className="inline-block mb-2 text-[11px] font-semibold text-pink-700 hover:underline"
                >
                  Moderar esta comunidade
                </Link>
              )}
              {community.is_archived && (
                <span className="inline-block mb-2 text-[10px] font-bold text-slate-600 bg-slate-100 px-1.5 rounded-sm border border-slate-300">
                  Arquivada: somente leitura
                </span>
              )}

              <div className="py-2 border-t border-b border-slate-100 text-xs text-slate-600 mb-3">
                <span className="font-bold text-slate-900">{community.member_count.toLocaleString("pt-BR")}</span>
                <span className="text-slate-400 ml-1">membros</span>
              </div>

              {myRole === "LEADER" ? (
                <div className="py-1 px-3 bg-purple-50 border border-purple-200 text-purple-800 text-xs font-bold rounded-sm flex items-center justify-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                  <span>Você é o líder</span>
                </div>
              ) : permissions?.can_leave ? (
                <button
                  onClick={() => void handleMembership(false)}
                  disabled={membershipBusy}
                  className="w-full py-1.5 text-xs font-bold rounded-sm border border-slate-300 text-slate-700 hover:bg-slate-100 disabled:opacity-60"
                >
                  Sair da comunidade
                </button>
              ) : permissions?.can_join ? (
                <button
                  onClick={() => void handleMembership(true)}
                  disabled={membershipBusy}
                  className="w-full py-1.5 text-xs font-bold rounded-sm bg-pink-600 text-white hover:bg-pink-700 disabled:opacity-60"
                >
                  Participar da comunidade
                </button>
              ) : myState === "BANNED" ? (
                <p className="text-xs text-red-700 font-semibold">Você foi banido desta comunidade.</p>
              ) : null}
              {(permissions?.can_edit || permissions?.can_delete) && (
                <Link
                  to={paths.communitySettings(community.commname)}
                  className="mt-2 block w-full py-1.5 text-xs font-bold rounded-sm border border-slate-300 text-slate-700 hover:bg-slate-100 text-center"
                >
                  Configurações da comunidade
                </Link>
              )}
              {membershipError && (
                <p role="alert" className="mt-2 text-[11px] text-red-700">
                  {membershipError}
                </p>
              )}
            </div>
          </div>

          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900">Sobre este espaço</span>
            </div>
            <div className="p-3">
              <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-wrap break-words">
                {community.description || "Nenhuma descrição fornecida."}
              </p>
              <div className="mt-3 pt-2 border-t border-slate-100 text-[10px] text-slate-400">
                Criada em {new Date(community.created_at).toLocaleDateString("pt-BR")}
              </div>
            </div>
          </div>

          {permissions?.can_view_wallet && (
            <div className="panel-classic bg-pink-50/50">
              <div className="p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <SoapIcon size={16} />
                  <span className="text-xs font-bold text-pink-900">Carteira da comunidade</span>
                </div>
                <div className="text-xs text-slate-700">
                  Saldo: <strong>{walletBalance ?? "—"} soap</strong>
                </div>
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  Recebe soap quando conteúdo da comunidade é apoiado.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Center column */}
        <div className="lg:col-span-6 min-w-0 lg:h-full lg:overflow-y-auto pr-1.5 scrollbar-thin">
          {community.banner_photo && (
            <div className="relative w-full h-36 sm:h-44 rounded-sm overflow-hidden mb-4 border border-slate-200 bg-slate-100" data-testid="community-banner">
              <img src={community.banner_photo} alt={`Banner de ${community.name}`} className="w-full h-full object-cover" />
              <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-slate-900/55 to-transparent pointer-events-none" />
              <div className="absolute bottom-2 left-3 right-3 text-white pointer-events-none">
                <span className="block text-sm font-bold leading-tight truncate drop-shadow">{community.name}</span>
                <span className="block text-[11px] font-mono opacity-90 truncate">@{community.commname}</span>
              </div>
            </div>
          )}

          <div className="panel-classic mb-4">
            <div className="p-1 flex items-center gap-1 bg-slate-50" role="tablist">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 py-1.5 text-xs font-bold rounded-sm transition-all text-center ${
                    activeTab === tab.id ? "bg-white text-slate-900 shadow-xs" : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {activeTab === "posts" && (
            <div className="space-y-4">
              <div className="panel-classic">
                <div className="panel-classic-header flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-pink-600" />
                    <h2 className="text-xs font-bold text-slate-900">Publicar na comunidade</h2>
                  </div>
                  <span className="text-[10px] text-pink-900 bg-pink-50 px-1.5 py-0.5 rounded-sm border border-pink-200 font-semibold flex items-center gap-1">
                    <SoapIcon size={12} />
                    Custo: {postCost ?? "..."} soap
                  </span>
                </div>

                {canPost ? (
                  <form onSubmit={handleCreatePost} className="p-3">
                    {postError && (
                      <div role="alert" className="mb-2.5 p-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-sm flex items-center gap-1.5">
                        <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>{postError}</span>
                      </div>
                    )}
                    {postSuccess && (
                      <div className="mb-2.5 p-2 bg-green-50 border border-green-200 text-green-700 text-xs rounded-sm flex items-center gap-1.5">
                        <Check className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>Sua bolha foi compartilhada com a comunidade.</span>
                      </div>
                    )}

                    <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-sm mb-2">
                      {(
                        [
                          ["text", "Texto", FileText],
                          ["photo", "Foto (até 10 MB)", ImageIcon],
                        ] as const
                      ).map(([id, label, Icon]) => (
                        <button
                          key={id}
                          type="button"
                          onClick={() => setPostTab(id)}
                          className={`flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold rounded-sm transition-all ${
                            postTab === id ? "bg-white text-slate-900 shadow-xs" : "text-slate-600 hover:text-slate-900"
                          }`}
                        >
                          <Icon className="w-3 h-3" />
                          {label}
                        </button>
                      ))}
                    </div>

                    <textarea
                      value={postText}
                      onChange={(e) => setPostText(e.target.value)}
                      maxLength={2000}
                      rows={postTab === "photo" ? 2 : 3}
                      aria-label="Texto da publicação"
                      placeholder={`Escreva algo para ${community.name}...`}
                      className="w-full p-2 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none placeholder-slate-400"
                    />

                    {postTab === "photo" && (
                      <div className="mt-2 mb-1">
                        <input
                          type="file"
                          ref={fileInputRef}
                          accept="image/png,image/jpeg,image/webp,image/gif"
                          onChange={handlePhotoChange}
                          className="hidden"
                        />
                        {!photoDataUrl ? (
                          <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className="w-full border-2 border-dashed border-slate-300 hover:border-pink-500 bg-slate-50 p-2.5 text-center rounded-sm transition-colors"
                          >
                            <UploadCloud className="w-5 h-5 text-slate-400 mx-auto mb-0.5" />
                            <span className="text-xs font-semibold text-slate-700 block">Carregar foto</span>
                            <span className="text-[10px] text-slate-400 block">PNG, JPEG, WebP ou GIF, até 10 MB</span>
                          </button>
                        ) : (
                          <div className="border border-slate-200 rounded-sm p-1.5 bg-slate-50 flex items-center justify-between">
                            <div className="flex items-center gap-2 min-w-0">
                              <img src={photoDataUrl} alt="Prévia" className="w-12 h-12 object-cover rounded-sm border border-slate-200" />
                              <span className="text-xs font-bold text-slate-800 truncate max-w-[200px]">{photo?.name}</span>
                            </div>
                            <button type="button" onClick={clearPhoto} aria-label="Remover imagem" className="text-slate-400 hover:text-red-600 p-1">
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[10px] text-slate-400">{postText.length}/2000</span>
                      <button
                        type="submit"
                        disabled={loadingPost}
                        className="flex items-center gap-1.5 px-3 py-1 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs disabled:opacity-60"
                      >
                        <Send className="w-3 h-3" />
                        <span>{loadingPost ? "Publicando..." : "Publicar no mural"}</span>
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="p-4 text-center bg-slate-50/50">
                    <p className="text-xs text-slate-600 font-medium">
                      {community.is_archived
                        ? "Esta comunidade foi arquivada e não aceita novas publicações."
                        : myState === "SILENCED"
                          ? "Você está silenciado nesta comunidade e não pode publicar."
                          : myState === "BANNED"
                            ? "Você foi banido desta comunidade."
                            : "Você precisa ser membro desta comunidade para publicar no mural."}
                    </p>
                    {permissions?.can_join && (
                      <button
                        onClick={() => void handleMembership(true)}
                        disabled={membershipBusy}
                        className="mt-2 px-3 py-1 bg-pink-600 text-white text-xs font-bold rounded-sm hover:bg-pink-700 shadow-xs disabled:opacity-60"
                      >
                        Participar da comunidade
                      </button>
                    )}
                  </div>
                )}
              </div>

              {postsStatus === "loading" ? (
                <LoadingState label="Carregando bolhas..." />
              ) : postsStatus === "error" ? (
                <ErrorState message={postsError ?? "Não foi possível carregar o mural."} onRetry={() => void loadPosts(1, true)} />
              ) : posts.length === 0 ? (
                <div className="panel-classic">
                  <EmptyState message="Esta comunidade ainda não tem publicações" hint="Seja a primeira pessoa a publicar." />
                </div>
              ) : (
                <>
                  {posts.map((post) => (
                    <FeedItemCard
                      key={post.id}
                      post={post}
                      onOpenDetail={(p) => setSelectedPost(p)}
                      onDeleted={removePost}
                    />
                  ))}
                  {postsNext !== null && (
                    <div className="text-center">
                      <button onClick={() => void loadPosts(postsNext, false)} className="btn-outline px-4 py-1.5 text-xs font-semibold">
                        Carregar mais
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {activeTab === "guidelines" && (
            <div className="panel-classic">
              <div className="panel-classic-header flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-pink-600" />
                  <h2 className="text-xs font-bold text-slate-900">Diretrizes da comunidade</h2>
                </div>
                {permissions?.can_edit_guidelines && !isEditingGuidelines && (
                  <button onClick={() => setIsEditingGuidelines(true)} className="text-xs font-semibold text-pink-600 hover:text-pink-700">
                    Editar diretrizes
                  </button>
                )}
              </div>
              <div className="p-4">
                {isEditingGuidelines ? (
                  <div>
                    <textarea
                      value={guidelinesText}
                      onChange={(e) => setGuidelinesText(e.target.value)}
                      maxLength={2000}
                      rows={6}
                      aria-label="Diretrizes"
                      className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white resize-none"
                    />
                    {guidelinesError && (
                      <p role="alert" className="mt-1 text-[11px] text-red-700">
                        {guidelinesError}
                      </p>
                    )}
                    <div className="mt-2 flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setGuidelinesText(community.guidelines ?? "");
                          setGuidelinesError(null);
                          setIsEditingGuidelines(false);
                        }}
                        className="px-3 py-1 text-xs text-slate-600 hover:text-slate-900"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={() => void handleSaveGuidelines()}
                        className="px-3 py-1 bg-pink-600 text-white text-xs font-bold rounded-sm hover:bg-pink-700 shadow-xs"
                      >
                        Salvar diretrizes
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-line break-words">
                    {community.guidelines || "Esta comunidade ainda não possui diretrizes registradas."}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "customization" && permissions?.can_customize && (
            <CommunityCustomizationPanel
              community={community}
              walletBalance={walletBalance}
              onChanged={loadCommunity}
            />
          )}

          {activeTab === "members" && (
            <div className="space-y-4">
              {membersStatus === "loading" ? (
                <LoadingState label="Carregando membros..." />
              ) : membersStatus === "error" ? (
                <ErrorState message={membersError ?? "Não foi possível carregar os membros."} onRetry={() => void loadMembers(1, true)} />
              ) : (
                <>
                  {leader && (
                    <div className="panel-classic">
                      <div className="panel-classic-header">
                        <span className="text-xs font-bold text-slate-900">Líder</span>
                      </div>
                      <div className="p-3">
                        <MemberLine member={leader} badge={{ label: "Líder", className: "text-purple-700 bg-purple-50 border-purple-200" }} />
                      </div>
                    </div>
                  )}
                  {admins.length > 0 && (
                    <div className="panel-classic">
                      <div className="panel-classic-header">
                        <span className="text-xs font-bold text-slate-900">Moderadores ({admins.length})</span>
                      </div>
                      <div className="p-3 divide-y divide-slate-100">
                        {admins.map((m) => (
                          <MemberLine key={m.id} member={m} badge={{ label: "Moderador", className: "text-pink-700 bg-pink-50 border-pink-200" }} />
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="panel-classic">
                    <div className="panel-classic-header">
                      <span className="text-xs font-bold text-slate-900">Membros</span>
                    </div>
                    <div className="p-3 divide-y divide-slate-100">
                      {regular.length === 0 ? (
                        <p className="text-xs text-slate-400">Nenhum outro membro ainda.</p>
                      ) : (
                        regular.map((m) => <MemberLine key={m.id} member={m} />)
                      )}
                    </div>
                  </div>
                  {membersNext !== null && (
                    <div className="text-center">
                      <button onClick={() => void loadMembers(membersNext, false)} className="btn-outline px-4 py-1.5 text-xs font-semibold">
                        Carregar mais membros
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          <div className="py-6 text-center text-[11px] text-slate-400">Bubbles • {community.name}</div>
        </div>

        {/* Right column */}
        <div className="lg:col-span-3 lg:h-full lg:overflow-y-auto scrollbar-none space-y-4">
          <div className="panel-classic">
            <div className="panel-classic-header flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900">Equipe de moderação</span>
              <ShieldCheck className="w-3.5 h-3.5 text-pink-600" />
            </div>
            <div className="p-2.5 space-y-2">
              {[...(leader ? [leader] : []), ...admins].map((m) => (
                <Link to={paths.profile(m.user.username)} key={m.id}  className="w-full flex items-center gap-2 text-left">
                  <Avatar user={m.user} className="w-7 h-7 flex-shrink-0" />
                  <span className="min-w-0">
                    <span className="text-xs font-bold text-slate-800 block truncate">{m.user.name}</span>
                    <span className={`text-[10px] font-semibold block ${m.role === "LEADER" ? "text-purple-700" : "text-pink-700"}`}>
                      {m.role === "LEADER" ? "Líder" : "Moderador"}
                    </span>
                  </span>
                </Link>
              ))}
              {!leader && admins.length === 0 && <p className="text-xs text-slate-400">Carregando equipe...</p>}
            </div>
          </div>

          <div className="panel-classic bg-slate-50/50">
            <div className="p-3">
              <span className="text-xs font-bold text-slate-800 block mb-1">Convivência</span>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                As publicações são de responsabilidade de quem as publica. Apoie criadores e mantenha o foco no tema.
              </p>
            </div>
          </div>
        </div>
      </div>

      {selectedPost && (
        <PostDetailModal
          post={selectedPost}
          story={null}
          onClose={() => setSelectedPost(null)}
          onPostUpdate={(updated) => {
            setPosts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
            setSelectedPost(updated);
          }}
          onPostDeleted={removePost}
        />
      )}
    </div>
  );
};
