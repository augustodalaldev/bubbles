import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { paths } from "@/routes";
import { motion } from "framer-motion";
import { Bubblegram, Bubblepop, Comment } from "@/types";
import { X, MessageCircle, Send, Clock, Trash2, CornerDownRight } from "lucide-react";
import { Avatar } from "@/components/Avatar";
import { SoapIcon } from "@/components/SoapIcon";
import { EmptyState, ErrorState, LoadingState } from "@/components/StateViews";
import { useAuthStore } from "@/features/auth/authStore";
import { useSupportBubblegram } from "@/features/feed/useSupport";
import {
  createComment,
  deleteBubblegram,
  deleteBubblepop,
  deleteComment,
  listComments,
  supportComment,
} from "@/services/content";
import { errorMessage, toApiError } from "@/services/errors";
import { hoursLeft, timeAgo } from "@/utils/time";

interface PostDetailModalProps {
  post: Bubblegram | null;
  story: Bubblepop | null;
  onClose: () => void;
  onPostUpdate?: (post: Bubblegram) => void;
  onPostDeleted?: (postId: number) => void;
  onStoryDeleted?: (storyId: number) => void;
}

interface CommentNode {
  comment: Comment;
  children: CommentNode[];
}

function buildTree(comments: Comment[]): CommentNode[] {
  const nodes = new Map<number, CommentNode>(comments.map((c) => [c.id, { comment: c, children: [] }]));
  const roots: CommentNode[] = [];
  for (const node of nodes.values()) {
    const parent = node.comment.parent !== null ? nodes.get(node.comment.parent) : undefined;
    (parent ? parent.children : roots).push(node);
  }
  return roots;
}

const CommentRow: React.FC<{
  node: CommentNode;
  depth: number;
  onReply: (comment: Comment) => void;
  onDelete: (comment: Comment) => void;
  onSupport: (comment: Comment) => Promise<void>;
  supportedIds: Set<number>;
  ownId?: number;
}> = ({ node, depth, onReply, onDelete, onSupport, supportedIds, ownId }) => {
  const { comment } = node;
  const supported = supportedIds.has(comment.id);
  return (
    <div className={depth > 0 ? "ml-4 border-l border-slate-200 pl-2" : ""}>
      <div className="p-2 bg-slate-50 border border-slate-200 rounded-sm text-xs">
        <div className="flex items-center justify-between mb-0.5 gap-2">
          <span className="font-bold text-slate-800 truncate">{comment.user.name}</span>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="text-[10px] text-slate-400">{timeAgo(comment.published_at)}</span>
            <button
              onClick={() => void onSupport(comment)}
              disabled={supported || comment.user.id === ownId}
              title={
                comment.user.id === ownId
                  ? "Você não pode apoiar o seu próprio comentário"
                  : supported
                    ? "Você já apoiou este comentário"
                    : "Apoiar comentário com soap"
              }
              className={`flex items-center gap-1 px-2 py-0.5 text-[10px] font-bold rounded-sm border transition-colors ${
                supported
                  ? "bg-pink-100 text-pink-900 border-pink-300"
                  : "bg-white border-slate-200 text-slate-600 hover:border-slate-300 disabled:opacity-60"
              }`}
            >
              <SoapIcon size={14} />
              <span>{comment.soap_count}</span>
            </button>
          </div>
        </div>
        <p className="text-slate-600 text-[11px] leading-snug whitespace-pre-wrap break-words">
          {comment.text}
        </p>
        <div className="mt-1 flex items-center gap-3 text-[10px]">
          <button onClick={() => onReply(comment)} className="text-pink-600 hover:underline">
            Responder
          </button>
          {comment.can_delete && (
            <button
              onClick={() => onDelete(comment)}
              className="text-slate-400 hover:text-red-600 flex items-center gap-0.5"
            >
              <Trash2 className="w-3 h-3" /> Excluir
            </button>
          )}
        </div>
      </div>
      {node.children.length > 0 && (
        <div className="mt-1 space-y-1">
          {node.children.map((child) => (
            <CommentRow
              key={child.comment.id}
              node={child}
              // Deep threads stay flat after the 3rd level so they do not run off the panel.
              depth={Math.min(depth + 1, 2)}
              onReply={onReply}
              onDelete={onDelete}
              onSupport={onSupport}
              supportedIds={supportedIds}
              ownId={ownId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const PostDetailModal: React.FC<PostDetailModalProps> = ({
  post,
  story,
  onClose,
  onPostUpdate,
  onPostDeleted,
  onStoryDeleted,
}) => {
  const currentUser = useAuthStore((s) => s.user)!;
  const refreshUser = useAuthStore((s) => s.refreshUser);

  const support = useSupportBubblegram(post?.id ?? 0, post?.soap_count ?? 0, (count) => {
    if (post) onPostUpdate?.({ ...post, soap_count: count });
  });

  const [comments, setComments] = useState<Comment[]>([]);
  const [nextPage, setNextPage] = useState<number | null>(1);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [supportedIds, setSupportedIds] = useState<Set<number>>(new Set());
  const [input, setInput] = useState("");
  const [replyTo, setReplyTo] = useState<Comment | null>(null);
  const [sending, setSending] = useState(false);

  const postId = post?.id;

  const loadComments = useCallback(
    async (page: number, reset: boolean) => {
      if (postId === undefined) return;
      setLoading(true);
      setLoadError(null);
      try {
        const data = await listComments(postId, page);
        setComments((prev) => (reset ? data.results : [...prev, ...data.results]));
        setNextPage(data.next ? page + 1 : null);
      } catch (err) {
        setLoadError(errorMessage(err));
      } finally {
        setLoading(false);
      }
    },
    [postId]
  );

  useEffect(() => {
    setComments([]);
    setNextPage(1);
    if (postId !== undefined) void loadComments(1, true);
  }, [postId, loadComments]);

  const tree = useMemo(() => buildTree(comments), [comments]);

  if (!post && !story) return null;

  const isStory = !!story;
  const author = post?.user ?? story!.user;
  const mediaUrl = isStory ? story!.image : (post!.media[0]?.media ?? null);
  const description = isStory ? story!.description : post!.text;
  const isOwnPost = post?.user.id === currentUser.id;

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!post || !input.trim() || sending) return;
    setSending(true);
    setActionError(null);
    try {
      const created = await createComment(post.id, input.trim(), replyTo?.id ?? null);
      setComments((prev) => [...prev, created]);
      setInput("");
      setReplyTo(null);
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setSending(false);
    }
  };

  const handleSupportComment = async (comment: Comment) => {
    setActionError(null);
    try {
      const result = await supportComment(comment.id);
      setComments((prev) =>
        prev.map((c) => (c.id === comment.id ? { ...c, soap_count: result.soap_count } : c))
      );
      setSupportedIds((prev) => new Set(prev).add(comment.id));
      await refreshUser();
    } catch (err) {
      if (toApiError(err).code === "already_supported") {
        setSupportedIds((prev) => new Set(prev).add(comment.id));
      }
      setActionError(errorMessage(err));
    }
  };

  const handleDeleteComment = async (comment: Comment) => {
    if (!window.confirm("Excluir este comentário?")) return;
    setActionError(null);
    try {
      await deleteComment(comment.id);
      await loadComments(1, true); // replies may have been removed with it
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  const handleDeleteContent = async () => {
    if (!window.confirm(isStory ? "Excluir este bubblepop?" : "Excluir esta publicação?")) return;
    try {
      if (isStory) {
        await deleteBubblepop(story!.id);
        onStoryDeleted?.(story!.id);
      } else {
        await deleteBubblegram(post!.id);
        onPostDeleted?.(post!.id);
      }
      onClose();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  const canDeleteContent = isStory ? story!.can_delete : post!.can_delete;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.18 }}
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-3xl bg-white border border-slate-300 shadow-xl rounded-sm my-auto flex flex-col md:flex-row max-h-[90vh] overflow-hidden"
      >
        <button
          onClick={onClose}
          aria-label="Fechar"
          className="absolute top-2.5 right-2.5 z-20 w-7 h-7 bg-white/90 hover:bg-slate-100 text-slate-600 border border-slate-300 rounded-sm flex items-center justify-center transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {mediaUrl ? (
          <div className="md:w-1/2 bg-slate-900 flex items-center justify-center relative min-h-[280px] md:min-h-[460px]">
            <img src={mediaUrl} alt="Publicação" className="w-full h-full object-cover max-h-[460px]" />
            {isStory && (
              <div className="absolute bottom-3 left-3 px-2.5 py-1 bg-slate-900/80 text-white text-xs font-semibold rounded-sm flex items-center gap-1.5 border border-white/20">
                <Clock className="w-3 h-3 text-pink-400" />
                <span>Bubblepop · {hoursLeft(story!.expires_at)}</span>
              </div>
            )}
          </div>
        ) : (
          <div className="md:w-1/2 p-6 flex flex-col justify-center items-center text-center bg-slate-50 border-r border-slate-200">
            <p className="text-sm text-slate-800 font-medium leading-relaxed whitespace-pre-wrap break-words">
              {description}
            </p>
          </div>
        )}

        <div className="md:w-1/2 p-4 sm:p-5 flex flex-col justify-between overflow-y-auto bg-white">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 pr-8">
              <Link to={paths.profile(author.username)} className="flex items-center gap-2.5 min-w-0">
                <Avatar user={author} className="w-9 h-9 flex-shrink-0" />
                <div className="min-w-0">
                  <h4 className="text-sm font-bold text-slate-900 leading-tight truncate">{author.name}</h4>
                  <span className="text-xs text-slate-500 font-medium">@{author.username}</span>
                </div>
              </Link>
              <div
                title="Seu saldo atual de soap"
                className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-50 border border-slate-200 rounded-sm text-xs font-semibold text-slate-700"
              >
                <SoapIcon size={18} />
                <span>{currentUser.soap_balance ?? 0}</span>
              </div>
            </div>

            {mediaUrl && description && (
              <p className="mt-3 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap break-words">
                {description}
              </p>
            )}

            {post && (
              <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between gap-2">
                <button
                  onClick={() => void support.support()}
                  disabled={support.supported || support.busy || isOwnPost}
                  title={
                    isOwnPost
                      ? "Você não pode apoiar a sua própria publicação"
                      : support.supported
                        ? "Você já apoiou esta publicação"
                        : "Apoiar com soap"
                  }
                  className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-bold rounded-sm transition-all ${
                    support.supported
                      ? "bg-pink-100 text-pink-900 border border-pink-300"
                      : "bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 disabled:opacity-60"
                  }`}
                >
                  <SoapIcon size={22} />
                  <span>{support.count}</span>
                </button>
                {canDeleteContent && (
                  <button
                    onClick={() => void handleDeleteContent()}
                    className="btn-outline py-1.5 px-2.5 text-xs font-semibold flex items-center gap-1.5 text-slate-600 hover:text-red-700"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Excluir</span>
                  </button>
                )}
              </div>
            )}

            {isStory && canDeleteContent && (
              <div className="mt-4 pt-3 border-t border-slate-200">
                <button
                  onClick={() => void handleDeleteContent()}
                  className="btn-outline py-1.5 px-2.5 text-xs font-semibold flex items-center gap-1.5 text-slate-600 hover:text-red-700"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Excluir bubblepop</span>
                </button>
              </div>
            )}

            {(support.error || actionError) && (
              <p role="alert" className="mt-2 text-[11px] text-red-700">
                {support.error ?? actionError}
              </p>
            )}

            {post && (
              <div className="mt-4">
                <div className="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5 pb-1 border-b border-slate-100">
                  <MessageCircle className="w-3.5 h-3.5 text-slate-400" />
                  <span>Comentários</span>
                </div>

                {loadError && comments.length === 0 ? (
                  <ErrorState message={loadError} onRetry={() => void loadComments(1, true)} />
                ) : loading && comments.length === 0 ? (
                  <LoadingState label="Carregando comentários..." />
                ) : tree.length === 0 ? (
                  <EmptyState message="Ainda não há comentários" hint="Comentar é gratuito." />
                ) : (
                  <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                    {tree.map((node) => (
                      <CommentRow
                        key={node.comment.id}
                        node={node}
                        depth={0}
                        onReply={setReplyTo}
                        onDelete={(c) => void handleDeleteComment(c)}
                        onSupport={handleSupportComment}
                        supportedIds={supportedIds}
                        ownId={currentUser.id}
                      />
                    ))}
                    {nextPage !== null && (
                      <button
                        onClick={() => void loadComments(nextPage, false)}
                        disabled={loading}
                        className="w-full text-[11px] text-pink-600 hover:underline py-1"
                      >
                        {loading ? "Carregando..." : "Carregar mais comentários"}
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {post && (
            <form onSubmit={handleAddComment} className="mt-3 pt-2.5 border-t border-slate-200">
              {replyTo && (
                <div className="mb-1.5 flex items-center justify-between text-[11px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <CornerDownRight className="w-3 h-3" />
                    Respondendo a {replyTo.user.name}
                  </span>
                  <button type="button" onClick={() => setReplyTo(null)} className="hover:text-slate-800">
                    Cancelar
                  </button>
                </div>
              )}
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  aria-label="Escrever um comentário"
                  placeholder="Escrever um comentário..."
                  value={input}
                  maxLength={2000}
                  onChange={(e) => setInput(e.target.value)}
                  className="flex-1 px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white placeholder-slate-400"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || sending}
                  aria-label="Enviar comentário"
                  className="p-1.5 bg-pink-500 text-white rounded-sm disabled:opacity-40 hover:bg-pink-600 transition-colors"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </form>
          )}
        </div>
      </motion.div>
    </div>
  );
};
