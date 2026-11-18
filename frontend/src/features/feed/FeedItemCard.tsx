import React, { useState } from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { Bubblegram } from "@/types";
import { Avatar } from "@/components/Avatar";
import { UserName } from "@/components/UserName";
import { SoapIcon } from "@/components/SoapIcon";
import { useAuthStore } from "@/features/auth/authStore";
import { deleteBubblegram } from "@/services/content";
import { errorMessage } from "@/services/errors";
import { timeAgo } from "@/utils/time";
import { MessageSquare, Flame, Users, Trash2 } from "lucide-react";
import { useSupportBubblegram } from "./useSupport";

interface FeedItemCardProps {
  post: Bubblegram;
  onOpenDetail: (post: Bubblegram) => void;
  onDeleted?: (postId: number) => void;
}

export const FeedItemCard: React.FC<FeedItemCardProps> = ({
  post,
  onOpenDetail,
  onDeleted,
}) => {
  const currentUserId = useAuthStore((s) => s.user?.id);
  const { count, supported, busy, error: supportError, support } = useSupportBubblegram(
    post.id,
    post.soap_count
  );
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const isOwn = post.user.id === currentUserId;

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm("Excluir esta publicação? O soap já recebido não é devolvido.")) return;
    try {
      await deleteBubblegram(post.id);
      onDeleted?.(post.id);
    } catch (err) {
      setDeleteError(errorMessage(err));
    }
  };

  const supportTitle = isOwn
    ? "Você não pode apoiar a sua própria publicação"
    : supported
      ? "Você já apoiou esta publicação"
      : "Apoiar o autor com soap";

  return (
    <article className="panel-classic mb-4 transition-shadow hover:shadow-xs">
      {post.is_suggested && (
        <div className="bg-slate-100/90 px-3 py-1.5 border-b border-slate-200 flex items-center text-[11px]">
          {post.suggestion_reason === "popular" ? (
            <span className="flex items-center gap-1.5 font-semibold text-pink-700">
              <Flame className="w-3.5 h-3.5 text-pink-600" />
              Sugerido: mais popular nas últimas 24h
            </span>
          ) : (
            <span className="flex items-center gap-1.5 font-semibold text-purple-700">
              <Users className="w-3.5 h-3.5 text-purple-600" />
              Sugerido: da sua rede de conexões
            </span>
          )}
        </div>
      )}

      <div className="p-3 pb-2 flex items-center justify-between gap-3">
        <Link to={paths.profile(post.user.username)}
          
          className="flex items-center gap-2.5 min-w-0 text-left"
        >
          <Avatar user={post.user} className="w-9 h-9 flex-shrink-0" />
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <UserName user={post.user} className="text-xs font-bold text-slate-900 truncate" />
              <span className="text-[11px] text-slate-400">@{post.user.username}</span>
              {post.community && (
                <>
                  <span className="text-slate-300 text-xs">•</span>
                  <span className="text-[11px] font-semibold text-pink-700 bg-pink-50 px-1.5 rounded-sm border border-pink-200">
                    {post.community.name}
                  </span>
                </>
              )}
            </div>
            <span className="text-[10px] text-slate-400 leading-tight">
              {timeAgo(post.published_at)}
            </span>
          </div>
        </Link>

        {post.can_delete && (
          <button
            onClick={handleDelete}
            title="Excluir publicação"
            aria-label="Excluir publicação"
            className="text-slate-400 hover:text-red-600 p-1 rounded-sm transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {post.text && (
        <div
          onClick={() => onOpenDetail(post)}
          className="px-3 pt-1 pb-2.5 text-xs text-slate-800 leading-relaxed cursor-pointer whitespace-pre-wrap break-words"
        >
          {post.text}
        </div>
      )}

      {post.media.length > 0 && (
        <div
          onClick={() => onOpenDetail(post)}
          className="relative w-full bg-slate-900 overflow-hidden cursor-pointer"
        >
          <img
            src={post.media[0].media}
            alt="Mídia da publicação"
            className="w-full max-h-[480px] object-cover hover:opacity-95 transition-opacity"
          />
        </div>
      )}

      <div className="p-2.5 bg-slate-50/70 border-t border-slate-100">
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              void support();
            }}
            disabled={supported || busy || isOwn}
            title={supportTitle}
            className={`flex items-center gap-1.5 px-2.5 py-1 text-xs border rounded-sm transition-all shadow-xs ${
              supported
                ? "bg-pink-100 border-pink-300 text-pink-900 font-semibold"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50 disabled:opacity-60"
            }`}
          >
            <SoapIcon size={16} />
            <span className="font-bold">{count}</span>
            <span className="text-[10px] text-slate-500 font-normal">
              {supported ? "Apoiado" : "soap"}
            </span>
          </button>

          <button
            onClick={() => onOpenDetail(post)}
            title="Ver comentários"
            className="flex items-center gap-1 px-2.5 py-1 text-xs bg-white border border-slate-200 text-slate-700 rounded-sm hover:bg-slate-50 transition-colors shadow-xs"
          >
            <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
            <span>Comentários</span>
          </button>
        </div>
        {(supportError || deleteError) && (
          <p role="alert" className="mt-1.5 text-[11px] text-red-700">
            {supportError ?? deleteError}
          </p>
        )}
      </div>
    </article>
  );
};
