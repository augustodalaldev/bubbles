import React, { useState, useRef } from "react";
import { Bubblegram, Community, CommunityMemberItem, User } from "@/types";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { SoapIcon } from "@/components/SoapIcon";
import { FeedItemCard } from "@/features/feed/FeedItemCard";
import { PostDetailModal } from "@/features/profile/PostDetailModal";
import { 
  MOCK_COMMUNITIES, 
  MOCK_COMMUNITY_MEMBERS, 
  MOCK_COMMUNITY_POSTS 
} from "@/features/profile/mockData";
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
  Send
} from "lucide-react";

interface CommunityDetailViewProps {
  community: Community;
  currentUser: User;
  onBackToHub: () => void;
  onSelectOtherCommunity?: (community: Community) => void;
  onSelectUser?: (username: string) => void;
}

export const CommunityDetailView: React.FC<CommunityDetailViewProps> = ({
  community: initialCommunity,
  currentUser,
  onBackToHub,
  onSelectOtherCommunity,
  onSelectUser,
}) => {
  const [community, setCommunity] = useState<Community>(initialCommunity);
  const [activeTab, setActiveTab] = useState<"posts" | "guidelines" | "members">("posts");
  
  // Community Posts
  const initialPosts = MOCK_COMMUNITY_POSTS[community.commname] || [];
  const [communityPosts, setCommunityPosts] = useState<Bubblegram[]>(initialPosts);

  // Community Members
  const membersList: CommunityMemberItem[] = MOCK_COMMUNITY_MEMBERS[community.commname] || [
    {
      id: 99,
      user: currentUser,
      role: community.my_membership?.role || "MEMBER",
      current_state: "ACTIVE",
      joined_at: new Date().toISOString(),
    },
  ];

  // Post Detail Modal
  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);

  // New Post State inside community
  const [postTab, setPostTab] = useState<"text" | "photo">("text");
  const [postText, setPostText] = useState("");
  const [photoDataUrl, setPhotoDataUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSizeStr, setFileSizeStr] = useState<string | null>(null);
  const [loadingPost, setLoadingPost] = useState(false);
  const [postError, setPostError] = useState<string | null>(null);
  const [postSuccess, setPostSuccess] = useState(false);

  // Guidelines Editing State
  const [isEditingGuidelines, setIsEditingGuidelines] = useState(false);
  const [guidelinesText, setGuidelinesText] = useState(community.guidelines || "");

  const fileInputRef = useRef<HTMLInputElement>(null);
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

  const isMember = !!community.my_membership;
  const myRole = community.my_membership?.role;
  const canEditGuidelines = myRole === "LEADER" || myRole === "COMM_ADMIN";

  // Toggle Join/Leave Community
  const handleToggleJoin = () => {
    if (isMember) {
      if (myRole === "LEADER") {
        alert("O líder não pode deixar a comunidade sem antes transferir a liderança.");
        return;
      }
      setCommunity((prev) => ({
        ...prev,
        member_count: Math.max(1, prev.member_count - 1),
        my_membership: null,
      }));
    } else {
      setCommunity((prev) => ({
        ...prev,
        member_count: prev.member_count + 1,
        my_membership: {
          role: "MEMBER",
          current_state: "ACTIVE",
          joined_at: new Date().toISOString(),
        },
      }));
    }
  };

  // Handle Photo selection with 10MB limit
  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPostError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > MAX_FILE_SIZE) {
      setPostError(`O arquivo possui ${(file.size / (1024 * 1024)).toFixed(1)} MB e ultrapassa o limite máximo de 10 MB.`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setFileName(file.name);
    setFileSizeStr((file.size / (1024 * 1024)).toFixed(2) + " MB");

    const reader = new FileReader();
    reader.onload = () => {
      setPhotoDataUrl(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  // Submit Community Post
  const handleCreatePost = (e: React.FormEvent) => {
    e.preventDefault();
    setPostError(null);

    if (!isMember) {
      setPostError("Você precisa ser membro desta comunidade para publicar no mural.");
      return;
    }

    if (!postText.trim() && !photoDataUrl) {
      setPostError("Escreva uma mensagem ou anexe uma foto para publicar.");
      return;
    }

    if (postTab === "photo" && !photoDataUrl) {
      setPostError("Selecione uma imagem de até 10 MB na aba Foto.");
      return;
    }

    setLoadingPost(true);

    setTimeout(() => {
      const newPost: Bubblegram = {
        id: Date.now(),
        user: currentUser,
        community: community,
        text: postText.trim(),
        type: postTab === "photo" && photoDataUrl ? "MEDIA" : "TEXT",
        media: photoDataUrl ? [
          { id: Date.now() + 1, media: photoDataUrl, position: 0 }
        ] : [],
        soap_count: 0,
        published_at: new Date().toISOString(),
        is_suggested: false,
        suggestion_reason: null,
        can_delete: true,
      };

      setCommunityPosts((prev) => [newPost, ...prev]);
      setPostText("");
      setPhotoDataUrl(null);
      setFileName(null);
      setFileSizeStr(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setLoadingPost(false);
      setPostSuccess(true);
      setTimeout(() => setPostSuccess(false), 3000);
    }, 350);
  };

  // Save Guidelines
  const handleSaveGuidelines = () => {
    setCommunity((prev) => ({
      ...prev,
      guidelines: guidelinesText,
    }));
    setIsEditingGuidelines(false);
  };

  // Categorize members
  const leaderMember = membersList.find((m) => m.role === "LEADER");
  const adminMembers = membersList.filter((m) => m.role === "COMM_ADMIN");
  const regularMembers = membersList.filter((m) => m.role === "MEMBER");

  // Other suggested communities
  const otherCommunities = MOCK_COMMUNITIES.filter((c) => c.id !== community.id).slice(0, 3);

  return (
    <div className="max-w-7xl mx-auto px-4 py-3 h-[calc(100vh-3.5rem)] overflow-hidden">
      
      {/* 3-Column Classic Grid (Left 3 cols, Center 6 cols, Right 3 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start h-full">
        
        {/* Left Column (3 Cols) - Static / Follows the view */}
        <div className="lg:col-span-3 h-full overflow-y-auto scrollbar-none hidden lg:block space-y-4">
          
          {/* Back Button */}
          <button
            onClick={onBackToHub}
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-pink-600 transition-colors py-1 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Voltar para Comunidades</span>
          </button>

          {/* Community Info Card */}
          <div className="panel-classic">
            <div className="p-4 text-center">
              
              {/* Spherical Community Photo with BubbleOverlay */}
              <div className="relative w-20 h-20 rounded-full overflow-hidden mx-auto mb-2.5 border-2 border-slate-200 shadow-sm">
                <img
                  src={community.community_photo || ""}
                  alt={community.name}
                  className="w-full h-full object-cover"
                />
                <BubbleOverlay opacity={0.4} />
              </div>

              <h1 className="text-sm font-bold text-slate-900 leading-tight">
                {community.name}
              </h1>
              <span className="text-xs text-slate-400 font-mono block mt-0.5 mb-2">
                @{community.commname}
              </span>

              {/* Members Counter */}
              <div className="py-2 border-t border-b border-slate-100 text-xs text-slate-600 mb-3">
                <span className="font-bold text-slate-900">
                  {community.member_count.toLocaleString("pt-BR")}
                </span>
                <span className="text-slate-400 ml-1">membros ativos</span>
              </div>

              {/* Join / Leave Action */}
              <div>
                {myRole === "LEADER" ? (
                  <div className="py-1 px-3 bg-purple-50 border border-purple-200 text-purple-800 text-xs font-bold rounded-sm flex items-center justify-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                    <span>Você é o Líder</span>
                  </div>
                ) : (
                  <button
                    onClick={handleToggleJoin}
                    className={`w-full py-1.5 text-xs font-bold rounded-sm transition-all shadow-xs ${
                      isMember
                        ? "border border-slate-300 text-slate-700 hover:bg-slate-100"
                        : "bg-pink-600 text-white hover:bg-pink-700 active:scale-95"
                    }`}
                  >
                    {isMember ? "Sair da Comunidade" : "Participar da Comunidade"}
                  </button>
                )}
              </div>

            </div>
          </div>

          {/* Description Card */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                Sobre este Espaço
              </span>
            </div>
            <div className="p-3">
              <p className="text-xs text-slate-600 leading-relaxed">
                {community.description || "Nenhuma descrição fornecida."}
              </p>
              <div className="mt-3 pt-2 border-t border-slate-100 text-[10px] text-slate-400">
                Criada em {new Date(community.created_at).toLocaleDateString("pt-BR")}
              </div>
            </div>
          </div>

          {/* Community Wallet (if leader or admin) */}
          {(myRole === "LEADER" || myRole === "COMM_ADMIN") && (
            <div className="panel-classic bg-pink-50/50">
              <div className="p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <SoapIcon size={16} />
                  <span className="text-xs font-bold text-pink-900">
                    Carteira da Comunidade
                  </span>
                </div>
                <div className="text-xs text-slate-700">
                  Saldo: <strong>140 soap</strong>
                </div>
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  Arrecadado com apoios em eventos e posts da comunidade.
                </span>
              </div>
            </div>
          )}

        </div>

        {/* Center Stream (6 Cols) - THE ONLY SCROLLABLE AREA */}
        <div className="lg:col-span-6 min-w-0 h-full overflow-y-auto pr-1.5 scrollbar-thin">
          
          {/* Banner Photo if available */}
          {community.banner_photo && (
            <div className="w-full h-32 rounded-sm overflow-hidden mb-4 border border-slate-200">
              <img
                src={community.banner_photo}
                alt={community.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Community Navigation Tabs */}
          <div className="panel-classic mb-4">
            <div className="p-1 flex items-center gap-1 bg-slate-50">
              <button
                onClick={() => setActiveTab("posts")}
                className={`flex-1 py-1.5 text-xs font-bold rounded-sm transition-all text-center ${
                  activeTab === "posts"
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Mural de Bolhas ({communityPosts.length})
              </button>
              <button
                onClick={() => setActiveTab("guidelines")}
                className={`flex-1 py-1.5 text-xs font-bold rounded-sm transition-all text-center ${
                  activeTab === "guidelines"
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Diretrizes
              </button>
              <button
                onClick={() => setActiveTab("members")}
                className={`flex-1 py-1.5 text-xs font-bold rounded-sm transition-all text-center ${
                  activeTab === "members"
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                Membros ({membersList.length})
              </button>
            </div>
          </div>

          {/* TAB 1: MURAL DE BOLHAS (POSTS) */}
          {activeTab === "posts" && (
            <div className="space-y-4">
              
              {/* Community Post Creator (Available only to members, 0 soap cost) */}
              <div className="panel-classic">
                <div className="panel-classic-header flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-pink-600" />
                    <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                      Publicar na Comunidade
                    </h2>
                  </div>
                  <span className="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded-sm border border-emerald-200 font-semibold">
                    Livre para Membros
                  </span>
                </div>

                {isMember ? (
                  <form onSubmit={handleCreatePost} className="p-3">
                    {postError && (
                      <div className="mb-2.5 p-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-sm flex items-center gap-1.5">
                        <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>{postError}</span>
                      </div>
                    )}

                    {postSuccess && (
                      <div className="mb-2.5 p-2 bg-green-50 border border-green-200 text-green-700 text-xs rounded-sm flex items-center gap-1.5">
                        <Check className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>Sua bolha foi compartilhada com a comunidade!</span>
                      </div>
                    )}

                    {/* Switcher: Texto vs Foto */}
                    <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-sm mb-2">
                      <button
                        type="button"
                        onClick={() => setPostTab("text")}
                        className={`flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold rounded-sm transition-all ${
                          postTab === "text"
                            ? "bg-white text-slate-900 shadow-xs"
                            : "text-slate-600 hover:text-slate-900"
                        }`}
                      >
                        <FileText className="w-3 h-3" />
                        Texto
                      </button>
                      <button
                        type="button"
                        onClick={() => setPostTab("photo")}
                        className={`flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold rounded-sm transition-all ${
                          postTab === "photo"
                            ? "bg-white text-slate-900 shadow-xs"
                            : "text-slate-600 hover:text-slate-900"
                        }`}
                      >
                        <ImageIcon className="w-3 h-3" />
                        Foto (Até 10 MB)
                      </button>
                    </div>

                    {/* Text Input */}
                    <textarea
                      value={postText}
                      onChange={(e) => setPostText(e.target.value)}
                      maxLength={2000}
                      rows={postTab === "photo" ? 2 : 3}
                      placeholder={`Escreva algo relevante para a comunidade ${community.name}...`}
                      className="w-full p-2 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white transition-colors resize-none placeholder-slate-400"
                    />

                    {/* Photo Upload Area */}
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
                          <div
                            onClick={() => fileInputRef.current?.click()}
                            className="border-2 border-dashed border-slate-300 hover:border-pink-500 bg-slate-50 p-2.5 text-center cursor-pointer rounded-sm transition-colors"
                          >
                            <UploadCloud className="w-5 h-5 text-slate-400 mx-auto mb-0.5" />
                            <span className="text-xs font-semibold text-slate-700 block">
                              Carregar foto para a comunidade
                            </span>
                            <span className="text-[10px] text-slate-400 block">
                              Suporte a arquivos de até <strong>10 MB</strong> (PNG, JPEG, WebP, GIF)
                            </span>
                          </div>
                        ) : (
                          <div className="border border-slate-200 rounded-sm p-1.5 bg-slate-50 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <img
                                src={photoDataUrl}
                                alt="Preview"
                                className="w-12 h-12 object-cover rounded-sm border border-slate-200"
                              />
                              <div>
                                <span className="text-xs font-bold text-slate-800 block truncate max-w-[200px]">
                                  {fileName}
                                </span>
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {fileSizeStr} • Limite: 10 MB
                                </span>
                              </div>
                            </div>
                            <button
                              type="button"
                              onClick={() => {
                                setPhotoDataUrl(null);
                                setFileName(null);
                                setFileSizeStr(null);
                              }}
                              className="text-slate-400 hover:text-red-600 p-1"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Bottom Submit Row */}
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[10px] text-slate-400">
                        {postText.length}/2000
                      </span>

                      <button
                        type="submit"
                        disabled={loadingPost}
                        className="flex items-center gap-1.5 px-3 py-1 bg-pink-600 text-white hover:bg-pink-700 text-xs font-bold rounded-sm shadow-xs transition-all active:scale-95"
                      >
                        <Send className="w-3 h-3" />
                        <span>{loadingPost ? "Publicando..." : "Publicar no Mural"}</span>
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="p-4 text-center bg-slate-50/50">
                    <p className="text-xs text-slate-600 font-medium">
                      Você precisa ser membro desta comunidade para publicar no mural.
                    </p>
                    <button
                      onClick={handleToggleJoin}
                      className="mt-2 px-3 py-1 bg-pink-600 text-white text-xs font-bold rounded-sm hover:bg-pink-700 transition-colors shadow-xs"
                    >
                      Participar da Comunidade
                    </button>
                  </div>
                )}
              </div>

              {/* Community Posts Stream */}
              {communityPosts.length > 0 ? (
                communityPosts.map((post) => (
                  <FeedItemCard
                    key={post.id}
                    post={post}
                    currentUser={currentUser}
                    onOpenDetail={(p) => setSelectedPost(p)}
                    onDeletePost={(postId) =>
                      setCommunityPosts((prev) => prev.filter((p) => p.id !== postId))
                    }
                    onSupportPost={(postId) =>
                      setCommunityPosts((prev) =>
                        prev.map((p) =>
                          p.id === postId ? { ...p, soap_count: p.soap_count + 1 } : p
                        )
                      )
                    }
                  />
                ))
              ) : (
                <div className="panel-classic p-8 text-center text-slate-500">
                  <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-xs font-semibold text-slate-700">
                    Ainda não há publicações nesta comunidade.
                  </p>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Seja o primeiro a compartilhar uma bolha com os membros!
                  </p>
                </div>
              )}

            </div>
          )}

          {/* TAB 2: DIRETRIZES */}
          {activeTab === "guidelines" && (
            <div className="panel-classic">
              <div className="panel-classic-header flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-pink-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                    Diretrizes da Comunidade
                  </h2>
                </div>
                {canEditGuidelines && !isEditingGuidelines && (
                  <button
                    onClick={() => setIsEditingGuidelines(true)}
                    className="text-xs font-semibold text-pink-600 hover:text-pink-700"
                  >
                    Editar Diretrizes
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
                      className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white resize-none"
                    />
                    <div className="mt-2 flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setGuidelinesText(community.guidelines || "");
                          setIsEditingGuidelines(false);
                        }}
                        className="px-3 py-1 text-xs text-slate-600 hover:text-slate-900"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleSaveGuidelines}
                        className="px-3 py-1 bg-pink-600 text-white text-xs font-bold rounded-sm hover:bg-pink-700 shadow-xs"
                      >
                        Salvar Diretrizes
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none text-xs text-slate-700 leading-relaxed whitespace-pre-line">
                    {community.guidelines || "Esta comunidade ainda não possui diretrizes registradas."}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: MEMBROS */}
          {activeTab === "members" && (
            <div className="space-y-4">
              
              {/* Leader Section */}
              {leaderMember && (
                <div className="panel-classic">
                  <div className="panel-classic-header">
                    <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                      Líder da Comunidade
                    </span>
                  </div>
                  <div 
                    onClick={() => onSelectUser?.(leaderMember.user.username)}
                    className="p-3 flex items-center gap-3 cursor-pointer"
                  >
                    <img
                      src={leaderMember.user.profile_photo || ""}
                      alt={leaderMember.user.name}
                      className="w-10 h-10 rounded-full object-cover border border-purple-200"
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900">
                          {leaderMember.user.name}
                        </span>
                        <span className="text-[10px] font-bold text-purple-700 bg-purple-50 px-1.5 py-0.2 rounded-sm border border-purple-200">
                          Líder
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400">
                        @{leaderMember.user.username}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Admins Section */}
              {adminMembers.length > 0 && (
                <div className="panel-classic">
                  <div className="panel-classic-header">
                    <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                      Moderadores ({adminMembers.length})
                    </span>
                  </div>
                  <div className="p-3 divide-y divide-slate-100">
                    {adminMembers.map((admin) => (
                      <div key={admin.id} className="py-2 flex items-center gap-3 first:pt-0 last:pb-0">
                        <img
                          src={admin.user.profile_photo || ""}
                          alt={admin.user.name}
                          className="w-9 h-9 rounded-full object-cover border border-pink-200"
                        />
                        <div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-bold text-slate-900">
                              {admin.user.name}
                            </span>
                            <span className="text-[10px] font-bold text-pink-700 bg-pink-50 px-1.5 py-0.2 rounded-sm border border-pink-200">
                              Moderador
                            </span>
                          </div>
                          <span className="text-[11px] text-slate-400">
                            @{admin.user.username}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Members Section */}
              <div className="panel-classic">
                <div className="panel-classic-header">
                  <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                    Membros ({regularMembers.length})
                  </span>
                </div>
                <div className="p-3 divide-y divide-slate-100">
                  {regularMembers.map((member) => (
                    <div key={member.id} className="py-2 flex items-center justify-between gap-3 first:pt-0 last:pb-0">
                      <div className="flex items-center gap-2.5">
                        <img
                          src={member.user.profile_photo || ""}
                          alt={member.user.name}
                          className="w-8 h-8 rounded-full object-cover border border-slate-200"
                        />
                        <div>
                          <span className="text-xs font-bold text-slate-800 block">
                            {member.user.name}
                          </span>
                          <span className="text-[10px] text-slate-400">
                            @{member.user.username}
                          </span>
                        </div>
                      </div>
                      <span className="text-[10px] text-slate-400">
                        Entrou em {new Date(member.joined_at).toLocaleDateString("pt-BR")}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* Footer note inside the scrollable stream at the bottom */}
          <div className="py-6 text-center text-[11px] text-slate-400">
            Bubbles • {community.name}
          </div>

        </div>

        {/* Right Column (3 Cols) - Static / Follows the view */}
        <div className="lg:col-span-3 h-full overflow-y-auto scrollbar-none hidden lg:block space-y-4">
          
          {/* Admin Team Preview */}
          <div className="panel-classic">
            <div className="panel-classic-header flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                Equipe de Moderação
              </span>
              <ShieldCheck className="w-3.5 h-3.5 text-pink-600" />
            </div>
            <div className="p-2.5 space-y-2">
              {leaderMember && (
                <div className="flex items-center gap-2">
                  <img
                    src={leaderMember.user.profile_photo || ""}
                    alt={leaderMember.user.name}
                    className="w-7 h-7 rounded-full object-cover border border-purple-200"
                  />
                  <div className="min-w-0">
                    <span className="text-xs font-bold text-slate-800 block truncate">
                      {leaderMember.user.name}
                    </span>
                    <span className="text-[10px] text-purple-700 font-semibold block">
                      Líder
                    </span>
                  </div>
                </div>
              )}
              {adminMembers.map((admin) => (
                <div key={admin.id} className="flex items-center gap-2">
                  <img
                    src={admin.user.profile_photo || ""}
                    alt={admin.user.name}
                    className="w-7 h-7 rounded-full object-cover border border-pink-200"
                  />
                  <div className="min-w-0">
                    <span className="text-xs font-bold text-slate-800 block truncate">
                      {admin.user.name}
                    </span>
                    <span className="text-[10px] text-pink-700 font-semibold block">
                      Moderador
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Other Suggested Communities */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                Outras Comunidades
              </span>
            </div>
            <div className="p-2 divide-y divide-slate-100">
              {otherCommunities.map((other) => (
                <div
                  key={other.id}
                  onClick={() => onSelectOtherCommunity?.(other)}
                  className="py-2 px-1 flex items-center justify-between gap-2 hover:bg-slate-50 cursor-pointer rounded-sm transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <img
                      src={other.community_photo || ""}
                      alt={other.name}
                      className="w-7 h-7 rounded-full object-cover border border-slate-200 flex-shrink-0"
                    />
                    <div className="min-w-0">
                      <span className="text-xs font-bold text-slate-800 block truncate">
                        {other.name}
                      </span>
                      <span className="text-[10px] text-slate-400 block">
                        {other.member_count.toLocaleString("pt-BR")} membros
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] text-pink-600 font-semibold flex-shrink-0">
                    Ver
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Community Etiquette Tip */}
          <div className="panel-classic bg-slate-50/50">
            <div className="p-3">
              <span className="text-xs font-bold text-slate-800 block mb-1">
                Convivência e Respeito
              </span>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                As publicações em comunidade são de responsabilidade de seus membros. Apoie criadores e mantenha o foco no tema.
              </p>
            </div>
          </div>

        </div>

      </div>

      {/* Post Detail Inspection Modal */}
      {selectedPost && (
        <PostDetailModal
          post={selectedPost}
          story={null}
          currentUser={currentUser}
          onClose={() => setSelectedPost(null)}
        />
      )}

    </div>
  );
};
