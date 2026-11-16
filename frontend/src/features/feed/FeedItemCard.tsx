import React, { useState } from "react";
import { Bubblegram, User } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { MessageSquare, Share2, Flame, Users, Check, Trash2 } from "lucide-react";
import confetti from "canvas-confetti";

interface FeedItemCardProps {
  post: Bubblegram;
  currentUser: User;
  onOpenDetail: (post: Bubblegram) => void;
  onDeletePost?: (postId: number) => void;
  onSupportPost?: (postId: number) => void;
}

export const FeedItemCard: React.FC<FeedItemCardProps> = ({
  post,
  currentUser,
  onOpenDetail,
  onDeletePost,
  onSupportPost,
}) => {
  const [soapCount, setSoapCount] = useState<number>(post.soap_count);
  const [hasSupported, setHasSupported] = useState<boolean>(false);
  const [copiedShare, setCopiedShare] = useState<boolean>(false);

  // Trigger bubble/foam rising animation
  const triggerBubbleShower = (e: React.MouseEvent) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const originX = (rect.left + rect.width / 2) / window.innerWidth;
    const originY = (rect.top + rect.height / 2) / window.innerHeight;

    confetti({
      particleCount: 16,
      angle: 90,
      spread: 50,
      startVelocity: 14,
      decay: 0.92,
      gravity: -0.3, // Rising effect like bubbles/foam
      ticks: 120,
      colors: ["#F465AC", "#E87DA0", "#FFFFFF", "#7B63FF"],
      origin: { x: originX, y: originY },
    });
  };

  const handleSupportClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (hasSupported) return;

    triggerBubbleShower(e);
    setSoapCount((prev) => prev + 1);
    setHasSupported(true);
    if (onSupportPost) {
      onSupportPost(post.id);
    }
  };

  const handleShareClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard?.writeText(window.location.origin + `/post/${post.id}`);
    setCopiedShare(true);
    setTimeout(() => setCopiedShare(false), 2000);
  };

  // Format relative time
  const formatTime = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      const now = new Date("2026-11-15T20:00:00Z");
      const diffMs = now.getTime() - date.getTime();
      const diffMin = Math.floor(diffMs / (1000 * 60));
      if (diffMin < 60) return `há ${Math.max(1, diffMin)} min`;
      const diffHours = Math.floor(diffMin / 60);
      if (diffHours < 24) return `há ${diffHours} h`;
      const diffDays = Math.floor(diffHours / 24);
      return `há ${diffDays} dia${diffDays > 1 ? "s" : ""}`;
    } catch {
      return "recente";
    }
  };

  const canDelete = post.can_delete || post.user.id === currentUser.id;

  return (
    <article className="panel-classic mb-4 transition-shadow hover:shadow-xs">
      
      {/* Suggested Post Banner (Interleaved Social Recommendations) */}
      {post.is_suggested && (
        <div className="bg-slate-100/90 px-3 py-1.5 border-b border-slate-200 flex items-center justify-between text-[11px] text-slate-600">
          <div className="flex items-center gap-1.5 font-semibold text-pink-700">
            {post.suggestion_reason === "popular" ? (
              <>
                <Flame className="w-3.5 h-3.5 text-pink-600" />
                <span>Sugerido: Mais popular nas últimas 24h</span>
              </>
            ) : (
              <>
                <Users className="w-3.5 h-3.5 text-purple-600" />
                <span className="text-purple-700">Sugerido: Da sua rede de conexões</span>
              </>
            )}
          </div>
          <span className="text-[10px] text-slate-400">Descoberta</span>
        </div>
      )}

      {/* Header: Author info, Community tag, Time */}
      <div className="p-3 pb-2 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5 min-w-0">
          
          {/* User Avatar (Clean, no bubble filter as per design guidelines) */}
          <img
            src={post.user.profile_photo || ""}
            alt={post.user.name}
            className="w-9 h-9 rounded-full object-cover border border-slate-200 flex-shrink-0"
          />

          {/* Author Details & Community Context */}
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-xs font-bold text-slate-900 truncate">
                {post.user.name}
              </span>
              <span className="text-[11px] text-slate-400">
                @{post.user.username}
              </span>

              {/* Community Tag */}
              {post.community && (
                <>
                  <span className="text-slate-300 text-xs">•</span>
                  <span className="text-[11px] font-semibold text-pink-700 bg-pink-50 px-1.5 py-0.2 rounded-sm border border-pink-200">
                    {post.community.name}
                  </span>
                </>
              )}
            </div>

            <span className="text-[10px] text-slate-400 leading-tight">
              {formatTime(post.published_at)}
            </span>
          </div>
        </div>

        {/* Delete option if authorized */}
        {canDelete && onDeletePost && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDeletePost(post.id);
            }}
            title="Excluir publicação"
            className="text-slate-400 hover:text-red-600 p-1 rounded-sm transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Text Body */}
      {post.text && (
        <div 
          onClick={() => onOpenDetail(post)}
          className="px-3 pt-1 pb-2.5 text-xs text-slate-800 leading-relaxed cursor-pointer"
        >
          {post.text}
        </div>
      )}

      {/* Media Content (Photos borderless, high resolution) */}
      {post.media && post.media.length > 0 && (
        <div 
          onClick={() => onOpenDetail(post)}
          className="relative w-full bg-slate-900 overflow-hidden cursor-pointer"
        >
          <img
            src={post.media[0].media}
            alt="Mídia da bolha"
            className="w-full max-h-[480px] object-cover hover:opacity-95 transition-opacity"
          />
        </div>
      )}

      {/* Action Footer: Soap Support, Comments, Share */}
      <div className="p-2.5 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between">
        
        {/* Left Actions: Soap & Comments */}
        <div className="flex items-center gap-2">
          
          {/* Soap Engagement Button */}
          <button
            onClick={handleSupportClick}
            disabled={hasSupported}
            title={hasSupported ? "Você já apoiou esta bolha com 1 soap" : "Apoiar criador com 1 soap"}
            className={`flex items-center gap-1.5 px-2.5 py-1 text-xs border rounded-sm transition-all shadow-xs ${
              hasSupported
                ? "bg-pink-100 border-pink-300 text-pink-900 font-semibold cursor-default"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50 active:scale-95 cursor-pointer"
            }`}
          >
            <SoapIcon size={16} />
            <span className="font-bold">{soapCount}</span>
            <span className="text-[10px] text-slate-500 font-normal">
              {hasSupported ? "Apoiado" : "soap"}
            </span>
          </button>

          {/* Comments Button */}
          <button
            onClick={() => onOpenDetail(post)}
            title="Ver comentários"
            className="flex items-center gap-1 px-2.5 py-1 text-xs bg-white border border-slate-200 text-slate-700 rounded-sm hover:bg-slate-50 transition-colors shadow-xs"
          >
            <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
            <span>Comentários</span>
          </button>
        </div>

        {/* Right Actions: Share */}
        <button
          onClick={handleShareClick}
          title="Compartilhar link do post"
          className="flex items-center gap-1 px-2 py-1 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-sm transition-colors"
        >
          {copiedShare ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-[11px] text-emerald-700 font-medium">Copiado</span>
            </>
          ) : (
            <>
              <Share2 className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px]">Compartilhar</span>
            </>
          )}
        </button>

      </div>
    </article>
  );
};
