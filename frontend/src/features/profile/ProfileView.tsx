import React, { useState, useRef } from "react";
import { 
  MOCK_USER, 
  MOCK_BUBBLEGRAMS, 
  MOCK_BUBBLEPOPS, 
  MOCK_FRIENDS, 
  MOCK_COMMUNITIES, 
  MOCK_LETTERS 
} from "./mockData";
import { BubblegramBall } from "./BubblegramBall";
import { BubblepopStory } from "./BubblepopStory";
import { PostDetailModal } from "./PostDetailModal";
import { Bubblegram, Bubblepop } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { 
  UserPlus, 
  Mail, 
  Calendar, 
  Layers, 
  Grid, 
  Plus, 
  Clock, 
  ShoppingBag
} from "lucide-react";

export const ProfileView: React.FC = () => {
  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);
  const [selectedStory, setSelectedStory] = useState<Bubblepop | null>(null);
  const [isFollowing, setIsFollowing] = useState(false);
  const [viewMode, setViewMode] = useState<"physics" | "grid">("physics");
  const playgroundRef = useRef<HTMLDivElement>(null);

  const formattedJoinDate = new Date(MOCK_USER.created_at).toLocaleDateString("pt-BR", {
    month: "short",
    year: "numeric",
  });

  const formattedBirthDate = MOCK_USER.birth_date
    ? new Date(MOCK_USER.birth_date).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      })
    : "";

  return (
    <main className="max-w-7xl mx-auto px-4 py-5">
      {/* 3-Column Classic Straight Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* ========================================================
            LEFT COLUMN: User Profile & Identity (No rounded panels)
           ======================================================== */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Main User Profile Card */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span>Perfil</span>
              <span className="flex items-center gap-1.5 text-[11px] font-normal text-slate-500">
                <span className="w-2 h-2 rounded-full bg-lime-400" />
                Ativo
              </span>
            </div>

            <div className="p-4 text-center flex flex-col items-center">
              {/* Spherical Bubble Avatar with Cosmetics */}
              <div className="relative mb-3 group cursor-pointer">
                <div 
                  className="w-28 h-28 rounded-full p-1 transition-transform duration-200 group-hover:scale-102"
                  style={{
                    background: "linear-gradient(135deg, #F465AC 0%, #7B63FF 100%)",
                    boxShadow: "0 0 16px rgba(244, 101, 172, 0.4)",
                  }}
                >
                  <div className="w-full h-full rounded-full overflow-hidden border-2 border-white relative bg-slate-100">
                    <img
                      src={MOCK_USER.profile_photo || ""}
                      alt={MOCK_USER.name}
                      className="w-full h-full object-cover"
                    />
                    <div className="bubble-reflection" />
                  </div>
                </div>
              </div>

              {/* User Names */}
              <h1 className="text-base font-bold text-slate-900 leading-tight">
                {MOCK_USER.name}
              </h1>
              <p className="text-xs text-pink-600 font-semibold mb-2">
                @{MOCK_USER.username}
              </p>

              {/* Bio */}
              <p className="text-xs text-slate-600 leading-relaxed text-center px-1 mb-3">
                {MOCK_USER.description}
              </p>

              {/* Direct Actions */}
              <div className="w-full grid grid-cols-2 gap-2 mb-4">
                <button
                  onClick={() => setIsFollowing(!isFollowing)}
                  className={`py-1.5 px-3 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                    isFollowing ? "btn-outline" : "btn-pink"
                  }`}
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  {isFollowing ? "Seguindo" : "Seguir"}
                </button>
                <button 
                  title="Enviar correspondência privada"
                  className="btn-purple py-1.5 px-3 text-xs font-semibold flex items-center justify-center gap-1.5"
                >
                  <Mail className="w-3.5 h-3.5" />
                  Carta
                </button>
              </div>

              {/* Profile Details (Only 100% backend fields) */}
              <div className="w-full pt-3 border-t border-slate-200 text-left space-y-1.5 text-xs text-slate-600">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Calendar className="w-3 h-3 text-slate-400" />
                    Nascimento:
                  </span>
                  <span className="font-semibold text-slate-700">{formattedBirthDate}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 flex items-center gap-1.5">
                    <Clock className="w-3 h-3 text-slate-400" />
                    Membro desde:
                  </span>
                  <span className="font-semibold text-slate-700">{formattedJoinDate}</span>
                </div>
              </div>

              {/* Quantitative Counters */}
              <div className="w-full mt-3 pt-3 border-t border-slate-200 grid grid-cols-3 text-center">
                <div>
                  <span className="block text-sm font-bold text-slate-800">
                    {MOCK_BUBBLEGRAMS.length}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Bolhas
                  </span>
                </div>
                <div>
                  <span className="block text-sm font-bold text-slate-800">
                    {MOCK_USER.followers_count}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Seguidores
                  </span>
                </div>
                <div>
                  <span className="block text-sm font-bold text-slate-800">
                    {MOCK_USER.following_count}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Seguindo
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Soap Wallet Panel */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="flex items-center gap-1.5">
                <SoapIcon size={14} />
                Carteira de soap
              </span>
              <span className="font-bold text-pink-600">
                {MOCK_USER.soap_balance} soap
              </span>
            </div>
            <div className="p-3 text-xs text-slate-600">
              <p className="leading-snug">
                Geração passiva: <strong>+5 soap</strong> por dia.
              </p>
              <button className="mt-2.5 w-full btn-outline py-1 px-2.5 text-xs flex items-center justify-center gap-1.5 text-slate-700">
                <ShoppingBag className="w-3.5 h-3.5 text-pink-500" />
                Loja de personalização
              </button>
            </div>
          </div>

        </div>

        {/* ========================================================
            CENTER COLUMN: Bubblepops Tray & Mural of Bubbles
           ======================================================== */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* Bubblepops Tray (Ephemeral Stories) */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span>Bubblepops</span>
              <button 
                title="Criar nova bolha temporária"
                className="btn-outline py-0.5 px-2 text-[11px] font-semibold flex items-center gap-1"
              >
                <Plus className="w-3 h-3 text-pink-600" />
                Novo
              </button>
            </div>

            {/* Stories Horizontal Tray with tighter spacing */}
            <div className="p-3 flex items-center gap-2.5 overflow-x-auto">
              {MOCK_BUBBLEPOPS.map((story) => (
                <BubblepopStory
                  key={story.id}
                  story={story}
                  onClick={(s) => setSelectedStory(s)}
                />
              ))}
            </div>
          </div>

          {/* Bubblegrams Mural (Interactive Arena) */}
          <div className="panel-classic flex flex-col">
            <div className="panel-classic-header">
              <div className="flex items-center gap-2">
                <span>Mural de bolhas</span>
                <span className="text-[11px] font-normal text-slate-400">
                  ({MOCK_BUBBLEGRAMS.length} postagens)
                </span>
              </div>

              {/* View Switcher Toggle */}
              <div className="flex items-center bg-slate-100 p-0.5 border border-slate-300 rounded-sm">
                <button
                  onClick={() => setViewMode("physics")}
                  className={`px-2 py-0.5 text-xs font-semibold flex items-center gap-1 rounded-sm transition-all ${
                    viewMode === "physics"
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  <Layers className="w-3 h-3 text-pink-500" />
                  Mural
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`px-2 py-0.5 text-xs font-semibold flex items-center gap-1 rounded-sm transition-all ${
                    viewMode === "grid"
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-500 hover:text-slate-900"
                  }`}
                >
                  <Grid className="w-3 h-3 text-slate-500" />
                  Grade
                </button>
              </div>
            </div>

            {/* Arena or Grid View */}
            <div className="p-3">
              {viewMode === "physics" ? (
                <div 
                  ref={playgroundRef}
                  className="relative w-full h-[560px] bg-slate-50 border border-slate-200 overflow-hidden"
                >
                  {/* Watermark instructions */}
                  <div className="absolute inset-x-0 bottom-2 text-center pointer-events-none select-none">
                    <span className="text-[10px] text-slate-400 font-medium bg-white/80 px-2 py-0.5 border border-slate-200 rounded-sm">
                      Arraste as bolhas pela tela ou clique para expandir
                    </span>
                  </div>

                  {/* Enlarged Draggable Bubblegrams */}
                  {MOCK_BUBBLEGRAMS.map((post) => (
                    <BubblegramBall
                      key={post.id}
                      post={post}
                      dragConstraintsRef={playgroundRef}
                      onClick={(p) => setSelectedPost(p)}
                    />
                  ))}
                </div>
              ) : (
                /* Classic Straight Grid View */
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {MOCK_BUBBLEGRAMS.map((post) => (
                    <div
                      key={post.id}
                      onClick={() => setSelectedPost(post)}
                      className="cursor-pointer bg-white border border-slate-200 p-2 hover:border-pink-300 transition-colors"
                    >
                      <div className="aspect-square bg-slate-100 overflow-hidden relative flex items-center justify-center">
                        {post.media && post.media.length > 0 ? (
                          <img
                            src={post.media[0].media}
                            alt="Mídia"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <p className="text-xs text-slate-600 font-medium p-3 text-center line-clamp-4">
                            "{post.text}"
                          </p>
                        )}
                        <span className="absolute bottom-1 right-1 px-1.5 py-0.5 bg-slate-900/80 text-white text-[10px] font-bold rounded-sm flex items-center gap-1">
                          <SoapIcon size={11} />
                          {post.soap_count}
                        </span>
                      </div>
                      <p className="text-xs text-slate-700 font-medium mt-1.5 truncate">
                        {post.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ========================================================
            RIGHT COLUMN: Friends, Communities & Direct Letters
           ======================================================== */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Friends Grid Card (Classic 3x3) */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span>Amigos ({MOCK_USER.followers_count})</span>
              <a href="#amigos" className="text-xs text-pink-600 font-semibold hover:underline">
                ver todos
              </a>
            </div>

            <div className="p-3">
              <div className="grid grid-cols-3 gap-2">
                {MOCK_FRIENDS.map((friend) => (
                  <div key={friend.id} className="flex flex-col items-center cursor-pointer group">
                    <div className="w-14 h-14 overflow-hidden border border-slate-200 group-hover:border-pink-400 transition-colors">
                      <img
                        src={friend.avatar}
                        alt={friend.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <span className="text-[11px] font-medium text-slate-700 mt-1 truncate max-w-[60px] text-center group-hover:text-pink-600">
                      {friend.name.split(" ")[0]}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Communities Card */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span>Comunidades ({MOCK_COMMUNITIES.length})</span>
              <a href="#comunidades" className="text-xs text-pink-600 font-semibold hover:underline">
                ver todas
              </a>
            </div>

            <div className="p-3 space-y-2">
              {MOCK_COMMUNITIES.map((comm) => (
                <div 
                  key={comm.id}
                  className="flex items-center gap-2.5 p-1.5 hover:bg-slate-50 transition-colors cursor-pointer group border border-transparent hover:border-slate-200"
                >
                  <img
                    src={comm.community_photo || ""}
                    alt={comm.name}
                    className="w-9 h-9 object-cover border border-slate-200"
                  />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-semibold text-slate-800 truncate group-hover:text-pink-600">
                      {comm.name}
                    </h4>
                    <span className="text-[10px] text-slate-400">
                      {comm.member_count.toLocaleString("pt-BR")} membros
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Direct Letters Section (Private Correspondence) */}
          <div className="panel-classic">
            <div className="panel-classic-header">
              <span className="flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-purple-600" />
                Cartas
              </span>
              <button className="text-xs text-pink-600 font-semibold hover:underline">
                Nova carta
              </button>
            </div>

            <div className="p-3 space-y-2.5">
              {MOCK_LETTERS.map((letter) => (
                <div key={letter.id} className="p-2.5 bg-slate-50 border border-slate-200">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1.5">
                      <img
                        src={letter.sender.avatar}
                        alt={letter.sender.name}
                        className="w-4 h-4 rounded-full object-cover"
                      />
                      <span className="text-xs font-bold text-slate-800">
                        {letter.sender.name}
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-400">
                      {letter.sent_at}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-snug">
                    "{letter.text}"
                  </p>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* Post or Story Detail Modal */}
      {(selectedPost || selectedStory) && (
        <PostDetailModal
          post={selectedPost}
          story={selectedStory}
          currentUser={MOCK_USER}
          onClose={() => {
            setSelectedPost(null);
            setSelectedStory(null);
          }}
        />
      )}
    </main>
  );
};
