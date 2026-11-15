import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bubblegram, Bubblepop, User } from "@/types";
import { X, Sparkles, Heart, MessageCircle, Share2, Send, Clock } from "lucide-react";
import confetti from "canvas-confetti";

interface PostDetailModalProps {
  post: Bubblegram | null;
  story: Bubblepop | null;
  currentUser: User;
  onClose: () => void;
}

export const PostDetailModal: React.FC<PostDetailModalProps> = ({
  post,
  story,
  currentUser,
  onClose,
}) => {
  const [soapCount, setSoapCount] = useState<number>(post?.soap_count ?? 12);
  const [hasSupported, setHasSupported] = useState(false);
  const [commentInput, setCommentInput] = useState("");
  const [comments, setComments] = useState<Array<{ id: number; author: string; avatar: string; text: string; time: string }>>([
    {
      id: 1,
      author: "Carol Diniz",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80",
      text: "Ficou incrível demais! Me lembra muito o papel de parede aquático que vinha no Mac OS X Tiger e no Vista.",
      time: "há 20 min",
    },
    {
      id: 2,
      author: "Lucas Melo",
      avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&q=80",
      text: "Deixei 3 sabões de apoio aqui! Sensacional essa foto 🫧✨",
      time: "há 1 hora",
    },
  ]);

  if (!post && !story) return null;

  const isStory = !!story;
  const author = post?.user || story?.user || currentUser;
  const mediaUrl = isStory 
    ? story?.image 
    : (post?.media && post.media.length > 0 ? post.media[0].media : null);
  const description = isStory ? story?.description : post?.text;

  const handleSoapSupport = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSoapCount((prev) => prev + 1);
    setHasSupported(true);

    // Trigger colorful soap-themed confetti
    try {
      const rect = (e.target as HTMLElement).getBoundingClientRect();
      const x = (rect.left + rect.width / 2) / window.innerWidth;
      const y = (rect.top + rect.height / 2) / window.innerHeight;

      confetti({
        particleCount: 45,
        spread: 60,
        origin: { x, y },
        colors: ["#08C4DB", "#4EE2F2", "#EE5B9B", "#FBA1CA", "#FFFFFF"],
        shapes: ["circle"],
        scalar: 1.2,
      });
    } catch {
      // Fallback silent
    }
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
        time: "agora mesmo",
      },
    ]);
    setCommentInput("");
  };

  return (
    <AnimatePresence>
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-900/60 backdrop-blur-md overflow-y-auto"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-3xl rounded-3xl overflow-hidden glass-card shadow-[0_25px_60px_-15px_rgba(8,196,219,0.35)] border border-white/90 bg-white/80 my-auto flex flex-col md:flex-row max-h-[90vh]"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 z-20 w-8 h-8 rounded-full bg-white/80 hover:bg-white text-slate-700 hover:text-slate-900 flex items-center justify-center shadow-md transition-all hover:scale-105"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Left Side: Media or Large Text */}
          {mediaUrl ? (
            <div className="md:w-1/2 bg-black/10 flex items-center justify-center relative overflow-hidden min-h-[260px] md:min-h-[460px]">
              <img
                src={mediaUrl}
                alt="Post media"
                className="w-full h-full object-cover max-h-[460px]"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/40 via-transparent to-white/20 pointer-events-none" />
              
              {isStory && (
                <div className="absolute bottom-3 left-3 px-3 py-1 rounded-full bg-soap-500/90 backdrop-blur-md text-white text-xs font-semibold flex items-center gap-1.5 shadow-md">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Bolha efêmera • Bubblepop</span>
                </div>
              )}
            </div>
          ) : (
            <div className="md:w-1/2 p-8 flex flex-col justify-center items-center text-center bg-gradient-to-br from-bubble-100/60 via-white to-soap-100/50">
              <span className="text-4xl mb-3">🫧</span>
              <p className="text-base text-slate-800 font-medium leading-relaxed italic">
                "{description}"
              </p>
            </div>
          )}

          {/* Right Side: Details, Scraps & Soap Action */}
          <div className="md:w-1/2 p-5 sm:p-6 flex flex-col justify-between overflow-y-auto">
            {/* Header info */}
            <div>
              <div className="flex items-center gap-3 pb-3 border-b border-bubble-100">
                <img
                  src={author.profile_photo || ""}
                  alt={author.name}
                  className="w-11 h-11 rounded-full object-cover border-2 border-white shadow-sm"
                />
                <div>
                  <h4 className="text-sm font-bold text-slate-900 leading-tight">
                    {author.name}
                  </h4>
                  <span className="text-xs text-bubble-700/80 font-medium">
                    @{author.username}
                  </span>
                </div>
              </div>

              {/* Caption */}
              {mediaUrl && (
                <p className="mt-3 text-sm text-slate-700 leading-relaxed">
                  {description}
                </p>
              )}

              {/* Action Bar (Support with Soap button) */}
              <div className="mt-4 pt-3 border-t border-bubble-100 flex items-center justify-between">
                <button
                  onClick={handleSoapSupport}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full font-bold text-sm text-white transition-all shadow-md active:scale-95 ${
                    hasSupported ? "bg-soap-600 scale-102" : "btn-glossy-cyan hover:shadow-bubble"
                  }`}
                >
                  <span className="text-base">🧼</span>
                  <span>Apoiar com Sabão ({soapCount})</span>
                  <Sparkles className="w-3.5 h-3.5 fill-current" />
                </button>

                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-full hover:bg-bubble-50 text-slate-600 hover:text-soap-600 transition-colors">
                    <Heart className="w-5 h-5" />
                  </button>
                  <button className="p-2 rounded-full hover:bg-bubble-50 text-slate-600 hover:text-bubble-600 transition-colors">
                    <Share2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Comments Section */}
              <div className="mt-5">
                <h5 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
                  <MessageCircle className="w-3.5 h-3.5" />
                  Recados nesta bolha ({comments.length})
                </h5>
                <div className="space-y-2.5 max-h-40 overflow-y-auto pr-1">
                  {comments.map((c) => (
                    <div key={c.id} className="flex items-start gap-2 text-xs bg-white/60 p-2 rounded-xl border border-white/80">
                      <img src={c.avatar} alt={c.author} className="w-6 h-6 rounded-full object-cover mt-0.5" />
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800">{c.author}</span>
                          <span className="text-[10px] text-slate-400">{c.time}</span>
                        </div>
                        <p className="text-slate-600 mt-0.5">{c.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Comment Form */}
            <form onSubmit={handleAddComment} className="mt-4 pt-3 border-t border-bubble-100 flex items-center gap-2">
              <input
                type="text"
                placeholder="Escreva um recado nesta bolha..."
                value={commentInput}
                onChange={(e) => setCommentInput(e.target.value)}
                className="flex-1 px-3.5 py-1.5 text-xs rounded-full bg-white/80 border border-white focus:outline-none focus:ring-2 focus:ring-bubble-400 placeholder-slate-400"
              />
              <button
                type="submit"
                disabled={!commentInput.trim()}
                className="p-2 rounded-full bg-bubble-500 text-white disabled:opacity-40 hover:bg-bubble-600 transition-all shadow-sm"
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
