import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bubblegram, Bubblepop, User } from "@/types";
import { X, MessageCircle, Send, Clock, Share2, Check } from "lucide-react";
import { SoapIcon } from "@/components/SoapIcon";
import confetti from "canvas-confetti";

interface PostDetailModalProps {
  post: Bubblegram | null;
  story: Bubblepop | null;
  currentUser: User;
  onClose: () => void;
}

interface CommentItem {
  id: number;
  author: string;
  avatar: string;
  text: string;
  time: string;
  soapCount: number;
  hasSupported: boolean;
}

export const PostDetailModal: React.FC<PostDetailModalProps> = ({
  post,
  story,
  currentUser,
  onClose,
}) => {
  const [soapCount, setSoapCount] = useState<number>(post?.soap_count ?? 12);
  const [hasSupportedPost, setHasSupportedPost] = useState(false);
  const [commentInput, setCommentInput] = useState("");
  const [copiedShare, setCopiedShare] = useState(false);

  const [comments, setComments] = useState<CommentItem[]>([
    {
      id: 1,
      author: "Carol Diniz",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
      text: "Excelente nitidez e composição de cores.",
      time: "há 20 min",
      soapCount: 3,
      hasSupported: false,
    },
    {
      id: 2,
      author: "Lucas Melo",
      avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80",
      text: "Enviei 1 soap de apoio. Trabalho muito bem executado.",
      time: "há 1 hora",
      soapCount: 1,
      hasSupported: false,
    },
  ]);

  if (!post && !story) return null;

  const isStory = !!story;
  const author = post?.user || story?.user || currentUser;
  const mediaUrl = isStory 
    ? story?.image 
    : (post?.media && post.media.length > 0 ? post.media[0].media : null);
  const description = isStory ? story?.description : post?.text;

  // Maximum 1 soap support per post
  const handleSoapSupport = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (hasSupportedPost) return;

    setSoapCount((prev) => prev + 1);
    setHasSupportedPost(true);

    try {
      const rect = (e.target as HTMLElement).getBoundingClientRect();
      const x = (rect.left + rect.width / 2) / window.innerWidth;
      const y = (rect.top + rect.height / 2) / window.innerHeight;

      confetti({
        particleCount: 25,
        spread: 45,
        origin: { x, y },
        colors: ["#F465AC", "#7B63FF", "#4BF521", "#FFFFFF"],
        shapes: ["circle"],
        scalar: 1,
      });
    } catch {
      // Fallback
    }
  };

  // Maximum 1 soap support per comment
  const handleSupportComment = (commentId: number) => {
    setComments((prev) =>
      prev.map((c) => {
        if (c.id === commentId && !c.hasSupported) {
          return {
            ...c,
            soapCount: c.soapCount + 1,
            hasSupported: true,
          };
        }
        return c;
      })
    );
  };

  const handleShare = () => {
    navigator.clipboard?.writeText(window.location.href);
    setCopiedShare(true);
    setTimeout(() => setCopiedShare(false), 2000);
  };

  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentInput.trim()) return;

    setComments((prev) => [
      ...prev,
      {
        id: Date.now(),
        author: currentUser.name,
        avatar: currentUser.profile_photo || "",
        text: commentInput.trim(),
        time: "agora",
        soapCount: 0,
        hasSupported: false,
      },
    ]);
    setCommentInput("");
  };

  return (
    <AnimatePresence>
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.96 }}
          transition={{ duration: 0.18 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-3xl bg-white border border-slate-300 shadow-xl rounded-sm my-auto flex flex-col md:flex-row max-h-[90vh] overflow-hidden"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-2.5 right-2.5 z-20 w-7 h-7 bg-white/90 hover:bg-slate-100 text-slate-600 border border-slate-300 rounded-sm flex items-center justify-center transition-colors"
          >
            <X className="w-4 h-4" />
          </button>

          {/* Left Side: Media or Text */}
          {mediaUrl ? (
            <div className="md:w-1/2 bg-slate-900 flex items-center justify-center relative min-h-[280px] md:min-h-[460px]">
              <img
                src={mediaUrl}
                alt="Publicação"
                className="w-full h-full object-cover max-h-[460px]"
              />

              {/* Elongated specular reflection in bottom-right corner */}
              <div 
                className="absolute rounded-full pointer-events-none"
                style={{
                  bottom: "8%",
                  right: "8%",
                  width: "48%",
                  height: "14%",
                  background: "linear-gradient(0deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0) 100%)",
                  transform: "rotate(-18deg)",
                }}
              />

              {isStory && (
                <div className="absolute bottom-3 left-3 px-2.5 py-1 bg-slate-900/80 text-white text-xs font-semibold rounded-sm flex items-center gap-1.5 border border-white/20">
                  <Clock className="w-3 h-3 text-pink-400" />
                  <span>Bubblepop efêmero</span>
                </div>
              )}
            </div>
          ) : (
            <div className="md:w-1/2 p-6 flex flex-col justify-center items-center text-center bg-slate-50 border-r border-slate-200">
              <p className="text-sm text-slate-800 font-medium leading-relaxed italic">
                "{description}"
              </p>
            </div>
          )}

          {/* Right Side: Author, Details & Support */}
          <div className="md:w-1/2 p-4 sm:p-5 flex flex-col justify-between overflow-y-auto bg-white">
            <div>
              {/* Author header */}
              <div className="flex items-center gap-3 pb-3 border-b border-slate-200">
                <img
                  src={author.profile_photo || ""}
                  alt={author.name}
                  className="w-10 h-10 rounded-full object-cover border border-slate-300"
                />
                <div>
                  <h4 className="text-sm font-bold text-slate-900 leading-tight">
                    {author.name}
                  </h4>
                  <span className="text-xs text-slate-500 font-medium">
                    @{author.username}
                  </span>
                </div>
              </div>

              {/* Caption text */}
              {mediaUrl && (
                <p className="mt-3 text-xs text-slate-700 leading-relaxed">
                  {description}
                </p>
              )}

              {/* Engagement Bar: Soap Support (Max 1) + Share Button */}
              <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between gap-2">
                <button
                  onClick={handleSoapSupport}
                  disabled={hasSupportedPost}
                  className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-bold rounded-sm transition-all ${
                    hasSupportedPost 
                      ? "bg-slate-100 text-slate-600 border border-slate-300 cursor-default" 
                      : "btn-pink hover:brightness-105"
                  }`}
                >
                  <SoapIcon size={14} />
                  <span>
                    {hasSupportedPost ? "Apoiado com 1 soap" : "Apoiar com 1 soap"} ({soapCount})
                  </span>
                </button>

                {/* Share Button */}
                <button
                  onClick={handleShare}
                  title="Compartilhar link da publicação"
                  className="btn-outline py-1.5 px-3 text-xs font-semibold flex items-center gap-1.5 text-slate-600 hover:text-slate-900"
                >
                  {copiedShare ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      <span className="text-emerald-700">Copiado!</span>
                    </>
                  ) : (
                    <>
                      <Share2 className="w-3.5 h-3.5" />
                      <span>Compartilhar</span>
                    </>
                  )}
                </button>
              </div>

              {/* Comments Section */}
              <div className="mt-4">
                <div className="text-xs font-bold text-slate-700 mb-2 flex items-center gap-1.5 pb-1 border-b border-slate-100">
                  <MessageCircle className="w-3.5 h-3.5 text-slate-400" />
                  <span>Comentários ({comments.length})</span>
                </div>

                <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                  {comments.map((c) => (
                    <div key={c.id} className="p-2 bg-slate-50 border border-slate-200 rounded-sm text-xs">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="font-bold text-slate-800">{c.author}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-slate-400">{c.time}</span>
                          
                          {/* Soap Support on Comments (Max 1) */}
                          <button
                            onClick={() => handleSupportComment(c.id)}
                            disabled={c.hasSupported}
                            title={c.hasSupported ? "Você já apoiou este comentário" : "Apoiar comentário com 1 soap"}
                            className={`flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-bold rounded-sm border transition-colors ${
                              c.hasSupported
                                ? "bg-pink-100 border-pink-300 text-pink-700 cursor-default"
                                : "bg-white border-slate-200 text-slate-600 hover:border-pink-300 hover:text-pink-600"
                            }`}
                          >
                            <SoapIcon size={11} />
                            <span>{c.soapCount}</span>
                          </button>
                        </div>
                      </div>
                      <p className="text-slate-600 text-[11px] leading-snug">{c.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Comment Input */}
            <form onSubmit={handleAddComment} className="mt-3 pt-2.5 border-t border-slate-200 flex items-center gap-2">
              <input
                type="text"
                placeholder="Escrever um comentário..."
                value={commentInput}
                onChange={(e) => setCommentInput(e.target.value)}
                className="flex-1 px-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-sm focus:outline-none focus:border-pink-500 focus:bg-white placeholder-slate-400"
              />
              <button
                type="submit"
                disabled={!commentInput.trim()}
                className="p-1.5 bg-pink-500 text-white rounded-sm disabled:opacity-40 hover:bg-pink-600 transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
