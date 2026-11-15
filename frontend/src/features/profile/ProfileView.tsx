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
import { 
  Sparkles, 
  UserPlus, 
  Mail, 
  Calendar, 
  MapPin, 
  Palette, 
  Coins, 
  Grid, 
  Compass, 
  Plus, 
  Layers,
  MessageSquare
} from "lucide-react";

export const ProfileView: React.FC = () => {
  const [selectedPost, setSelectedPost] = useState<Bubblegram | null>(null);
  const [selectedStory, setSelectedStory] = useState<Bubblepop | null>(null);
  const [isFollowing, setIsFollowing] = useState(false);
  const [viewMode, setViewMode] = useState<"physics" | "grid">("physics");
  const playgroundRef = useRef<HTMLDivElement>(null);

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-3 sm:px-6 py-6">
      {/* 3-Column Responsive Orkut Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* ========================================================
            LEFT COLUMN: User Profile, Orkut Badges & Personal Info
           ======================================================== */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Main User Card */}
          <div className="glass-card rounded-3xl p-5 text-center flex flex-col items-center">
            {/* Volumetric Avatar with Custom Frame */}
            <div className="relative mb-3.5 group cursor-pointer">
              <div 
                className="w-32 h-32 rounded-full p-1 transition-transform duration-300 group-hover:scale-105"
                style={{
                  background: "linear-gradient(135deg, #4EE2F2 0%, #08C4DB 50%, #EE5B9B 100%)",
                  boxShadow: "0 0 24px rgba(8, 196, 219, 0.45)",
                }}
              >
                <div className="w-full h-full rounded-full overflow-hidden border-2 border-white relative">
                  <img
                    src={MOCK_USER.profile_photo || ""}
                    alt={MOCK_USER.name}
                    className="w-full h-full object-cover"
                  />
                  {/* Glossy avatar reflection */}
                  <div 
                    className="absolute rounded-full pointer-events-none"
                    style={{
                      top: "5%",
                      left: "20%",
                      width: "50%",
                      height: "25%",
                      background: "linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0) 100%)",
                      transform: "rotate(-25deg)",
                    }}
                  />
                </div>
              </div>

              {/* Online Presence Badge */}
              <span className="absolute bottom-2 right-2 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-white border-2 border-white shadow-sm flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />
                Online
              </span>
            </div>

            {/* Names & Bio */}
            <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
              {MOCK_USER.name}
            </h1>
            <p className="text-xs font-semibold text-bubble-600 mb-2">
              @{MOCK_USER.username}
            </p>
            <p className="text-xs text-slate-600 leading-relaxed px-1 text-center">
              {MOCK_USER.description}
            </p>

            {/* Action Buttons */}
            <div className="w-full grid grid-cols-2 gap-2 mt-4">
              <button
                onClick={() => setIsFollowing(!isFollowing)}
                className={`py-2 px-3 rounded-full text-xs font-bold flex items-center justify-center gap-1.5 transition-all text-white ${
                  isFollowing ? "bg-slate-700 shadow-sm" : "btn-glossy-cyan shadow-bubble"
                }`}
              >
                <UserPlus className="w-3.5 h-3.5" />
                {isFollowing ? "Seguindo" : "Seguir"}
              </button>
              <button 
                title="Escrever uma carta / recado no mural"
                className="btn-glossy-pink py-2 px-3 rounded-full text-xs font-bold text-white flex items-center justify-center gap-1.5 shadow-md"
              >
                <Mail className="w-3.5 h-3.5" />
                Enviar Carta
              </button>
            </div>

            {/* Classic Orkut Badge Indicators (Nostalgic meters) */}
            <div className="w-full mt-5 pt-4 border-t border-white/80 space-y-2 text-left">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                Classificação da Comunidade
              </span>
              
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 font-medium">Confiável:</span>
                <span className="text-amber-500 font-bold flex items-center tracking-widest text-sm" title="3/3 Estrelas">
                  ⭐️⭐️⭐️
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 font-medium">Legal:</span>
                <span className="text-sky-500 font-bold flex items-center tracking-widest text-sm" title="Super Fresco / Cool">
                  🧊🧊🧊
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-600 font-medium">Radiante:</span>
                <span className="text-soap-500 font-bold flex items-center tracking-widest text-sm" title="Cheio de Bolhas e Brilho">
                  🫧🫧🫧
                </span>
              </div>
            </div>

            {/* Fast Stats */}
            <div className="w-full mt-4 pt-3 border-t border-white/80 grid grid-cols-3 text-center">
              <div>
                <span className="block text-base font-extrabold text-slate-800">
                  {MOCK_BUBBLEGRAMS.length}
                </span>
                <span className="text-[10px] font-semibold text-slate-500 uppercase">
                  Bolhas
                </span>
              </div>
              <div>
                <span className="block text-base font-extrabold text-slate-800">
                  {MOCK_USER.followers_count}
                </span>
                <span className="text-[10px] font-semibold text-slate-500 uppercase">
                  Seguidores
                </span>
              </div>
              <div>
                <span className="block text-base font-extrabold text-slate-800">
                  {MOCK_USER.following_count}
                </span>
                <span className="text-[10px] font-semibold text-slate-500 uppercase">
                  Seguindo
                </span>
              </div>
            </div>
          </div>

          {/* User Details & Identity Card */}
          <div className="glass-card rounded-3xl p-5 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-bubble-500" />
              Informações do Perfil
            </h3>
            
            <div className="space-y-2.5 text-xs text-slate-700">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-bubble-600/70" />
                <span>Aniversário: <strong>20 de Maio (26 anos)</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-soap-500" />
                <span>Cidade: <strong>Florianópolis, SC</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <Palette className="w-4 h-4 text-sky-500" />
                <span>Tema: <strong>Água Frutiger (Ciano)</strong></span>
              </div>
            </div>
          </div>

          {/* Soap Wallet Card */}
          <div className="glass-card rounded-3xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-soap-700 flex items-center gap-1.5">
                <Coins className="w-4 h-4 text-soap-500" />
                Carteira de Sabão
              </h3>
              <span className="text-xs font-black text-soap-600 bg-white/70 px-2 py-0.5 rounded-full border border-soap-200">
                {MOCK_USER.soap_balance} 🧼
              </span>
            </div>
            <p className="text-xs text-slate-600 leading-snug">
              Você gera <strong>+5 sabões</strong> passivamente a cada 24 horas por estar ativo na rede.
            </p>
            <button className="mt-3.5 w-full btn-glossy-glass text-slate-800 py-1.5 px-3 rounded-full text-xs font-bold flex items-center justify-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-soap-500" />
              Visitar Loja de Customizações
            </button>
          </div>
        </div>

        {/* ========================================================
            CENTER COLUMN: Stories Tray & Interactive Bubble Playground
           ======================================================== */}
        <div className="lg:col-span-6 space-y-4">
          
          {/* Bubblepops Tray (Ephemeral Stories) */}
          <div className="glass-card rounded-3xl p-4 sm:p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-lg">🫧</span>
                <div>
                  <h2 className="text-sm font-bold text-slate-900 leading-none">
                    Bubblepops Ativos
                  </h2>
                  <span className="text-[10px] text-slate-500 font-medium">
                    Bolhas de mídia efêmeras que estouram com o tempo
                  </span>
                </div>
              </div>

              <button 
                title="Criar nova bolha temporária"
                className="px-2.5 py-1 rounded-full btn-glossy-glass text-[11px] font-bold text-bubble-700 flex items-center gap-1"
              >
                <Plus className="w-3 h-3 text-bubble-600" />
                Soprar Bolha
              </button>
            </div>

            {/* Stories Horizontal Carousel */}
            <div className="flex items-center gap-4 overflow-x-auto pb-2 pt-1 scrollbar-none">
              {MOCK_BUBBLEPOPS.map((story) => (
                <BubblepopStory
                  key={story.id}
                  story={story}
                  onClick={(s) => setSelectedStory(s)}
                />
              ))}
            </div>
          </div>

          {/* Bubblegrams Interactive Arena */}
          <div className="glass-card rounded-3xl p-4 sm:p-5 flex flex-col">
            {/* Header & View Switcher */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/80">
              <div>
                <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                  <span>🔮</span>
                  <span>Mural de Bolhas de Sabão</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-bubble-100 text-bubble-700 font-semibold border border-bubble-200">
                    {MOCK_BUBBLEGRAMS.length} posts
                  </span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Arraste e empurre as bolhas flutuantes ou clique para expandir
                </p>
              </div>

              {/* View Switcher Toggle */}
              <div className="flex items-center bg-white/70 p-1 rounded-full border border-white/90 shadow-inner">
                <button
                  onClick={() => setViewMode("physics")}
                  className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all ${
                    viewMode === "physics"
                      ? "btn-glossy-cyan text-white shadow-xs"
                      : "text-slate-600 hover:text-bubble-700"
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  Bolhas Físicas
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all ${
                    viewMode === "grid"
                      ? "btn-glossy-cyan text-white shadow-xs"
                      : "text-slate-600 hover:text-bubble-700"
                  }`}
                >
                  <Grid className="w-3.5 h-3.5" />
                  Grade
                </button>
              </div>
            </div>

            {/* Physics Arena View */}
            {viewMode === "physics" ? (
              <div 
                ref={playgroundRef}
                className="relative w-full h-[520px] rounded-2xl mt-4 overflow-hidden bg-gradient-to-b from-sky-100/50 via-white/40 to-bubble-100/40 border border-white/70 shadow-inner"
              >
                {/* Aquatic Playground Water Caustic Watermark */}
                <div 
                  className="absolute inset-0 opacity-25 pointer-events-none"
                  style={{
                    backgroundImage: "radial-gradient(circle at 50% 50%, rgba(8,196,219,0.3) 0%, transparent 60%)"
                  }}
                />

                {/* Gentle hint watermark */}
                <div className="absolute inset-x-0 bottom-4 text-center pointer-events-none select-none">
                  <span className="text-[11px] font-bold text-bubble-700/60 bg-white/60 px-3 py-1 rounded-full backdrop-blur-xs border border-white/80">
                    💡 Dica: Pegue qualquer bolha com o mouse e arremesse!
                  </span>
                </div>

                {/* Draggable Bubblegrams floating freely */}
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
              /* Alternative Grid View */
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5 mt-4">
                {MOCK_BUBBLEGRAMS.map((post) => (
                  <div
                    key={post.id}
                    onClick={() => setSelectedPost(post)}
                    className="group cursor-pointer rounded-2xl overflow-hidden glass-card-subtle border border-white/90 p-2 hover:shadow-bubble transition-all hover:-translate-y-1"
                  >
                    <div className="aspect-square rounded-xl overflow-hidden relative bg-bubble-50 flex items-center justify-center">
                      {post.media && post.media.length > 0 ? (
                        <img
                          src={post.media[0].media}
                          alt="Thumbnail"
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <p className="text-[11px] text-slate-600 font-medium p-3 text-center line-clamp-4">
                          "{post.text}"
                        </p>
                      )}
                      <span className="absolute bottom-1.5 right-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold text-white bg-slate-900/60 backdrop-blur-xs flex items-center gap-1">
                        🧼 {post.soap_count}
                      </span>
                    </div>
                    <p className="text-xs text-slate-700 font-medium mt-2 line-clamp-1 px-1">
                      {post.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ========================================================
            RIGHT COLUMN: Orkut Friends 3x3 Grid, Communities & Scraps
           ======================================================== */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Friends Grid Card (Classic Orkut 3x3 Block) */}
          <div className="glass-card rounded-3xl p-5">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/80">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Amigos <span className="text-bubble-600">({MOCK_USER.followers_count})</span>
              </h3>
              <a href="#ver-amigos" className="text-xs font-bold text-bubble-600 hover:text-bubble-800">
                ver todos ({MOCK_USER.followers_count})
              </a>
            </div>

            {/* 3x3 Avatar Grid */}
            <div className="grid grid-cols-3 gap-2.5">
              {MOCK_FRIENDS.map((friend) => (
                <div key={friend.id} className="flex flex-col items-center group cursor-pointer">
                  <div className="w-14 h-14 rounded-2xl overflow-hidden border-2 border-white shadow-xs group-hover:scale-105 group-hover:border-bubble-300 transition-all">
                    <img
                      src={friend.avatar}
                      alt={friend.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <span className="text-[11px] font-semibold text-slate-700 mt-1 truncate max-w-[62px] text-center group-hover:text-bubble-600">
                    {friend.name.split(" ")[0]}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Communities Card */}
          <div className="glass-card rounded-3xl p-5">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/80">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Comunidades <span className="text-soap-600">({MOCK_COMMUNITIES.length})</span>
              </h3>
              <a href="#ver-comunidades" className="text-xs font-bold text-soap-600 hover:text-soap-800">
                ver todas
              </a>
            </div>

            <div className="space-y-2.5">
              {MOCK_COMMUNITIES.map((comm) => (
                <div 
                  key={comm.id}
                  className="flex items-center gap-3 p-2 rounded-2xl hover:bg-white/60 transition-colors cursor-pointer group"
                >
                  <img
                    src={comm.community_photo || ""}
                    alt={comm.name}
                    className="w-11 h-11 rounded-xl object-cover border border-white shadow-xs group-hover:scale-105 transition-transform"
                  />
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-slate-800 truncate group-hover:text-bubble-600">
                      {comm.name}
                    </h4>
                    <span className="text-[10px] text-slate-500 font-medium">
                      {comm.member_count.toLocaleString("pt-BR")} membros
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Scraps & Letters Card (Livro de Recados do Orkut) */}
          <div className="glass-card rounded-3xl p-5">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/80">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-bubble-500" />
                Cartas & Recados
              </h3>
              <span className="text-xs font-bold text-bubble-600">
                2 recados
              </span>
            </div>

            <div className="space-y-3">
              {MOCK_LETTERS.map((letter) => (
                <div key={letter.id} className="p-3 rounded-2xl bg-white/60 border border-white/90 shadow-2xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-800">
                      {letter.sender.name}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {letter.sent_at}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed italic">
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
