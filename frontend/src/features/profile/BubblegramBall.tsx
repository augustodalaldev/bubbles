import React, { useRef } from "react";
import { motion } from "framer-motion";
import { Bubblegram } from "@/types";
import { Sparkles, MessageCircle, Image as ImageIcon } from "lucide-react";

interface BubblegramBallProps {
  post: Bubblegram & { size?: number; initialX?: number; initialY?: number };
  dragConstraintsRef?: React.RefObject<Element>;
  onClick: (post: Bubblegram) => void;
}

export const BubblegramBall: React.FC<BubblegramBallProps> = ({
  post,
  dragConstraintsRef,
  onClick,
}) => {
  const isDraggingRef = useRef(false);
  const size = post.size || 150;
  const hasMedia = post.media && post.media.length > 0;
  const firstMedia = hasMedia ? post.media[0].media : null;

  return (
    <motion.div
      drag
      dragConstraints={dragConstraintsRef}
      dragElastic={0.25}
      dragMomentum={true}
      dragTransition={{ bounceStiffness: 250, bounceDamping: 18 }}
      onDragStart={() => {
        isDraggingRef.current = true;
      }}
      onDragEnd={() => {
        // Small delay to prevent opening modal immediately after dragging
        setTimeout(() => {
          isDraggingRef.current = false;
        }, 150);
      }}
      onClick={() => {
        if (!isDraggingRef.current) {
          onClick(post);
        }
      }}
      whileHover={{ scale: 1.06, zIndex: 30 }}
      whileDrag={{ scale: 1.12, zIndex: 40, cursor: "grabbing" }}
      initial={{ 
        x: post.initialX ?? 0, 
        y: post.initialY ?? 0, 
        scale: 0.8, 
        opacity: 0 
      }}
      animate={{ 
        scale: 1, 
        opacity: 1,
        y: [(post.initialY ?? 0) - 6, (post.initialY ?? 0) + 6, (post.initialY ?? 0) - 6],
      }}
      transition={{
        scale: { duration: 0.4 },
        opacity: { duration: 0.4 },
        y: {
          repeat: Infinity,
          duration: 4 + (post.id % 3),
          ease: "easeInOut",
        },
      }}
      style={{
        width: size,
        height: size,
      }}
      className="absolute cursor-grab select-none group touch-none"
    >
      {/* 3D Sphere Outer Container */}
      <div 
        className="relative w-full h-full rounded-full overflow-hidden p-1.5 transition-shadow duration-300 group-hover:shadow-[0_16px_36px_rgba(8,196,219,0.45)]"
        style={{
          background: "radial-gradient(circle at 35% 30%, rgba(255,255,255,0.95) 0%, rgba(184,242,248,0.7) 25%, rgba(8,196,219,0.55) 60%, rgba(238,91,155,0.45) 90%, rgba(255,255,255,0.9) 100%)",
          boxShadow: "inset -6px -8px 18px rgba(4,86,97,0.35), inset 4px 6px 12px rgba(255,255,255,0.95), 0 10px 28px -4px rgba(8,196,219,0.35)",
          border: "2px solid rgba(255, 255, 255, 0.85)",
        }}
      >
        {/* Post Content Sphere Preview */}
        <div className="w-full h-full rounded-full overflow-hidden relative bg-white/40 backdrop-blur-sm flex items-center justify-center">
          {hasMedia && firstMedia ? (
            <img
              src={firstMedia}
              alt="Bubblegram preview"
              className="w-full h-full object-cover rounded-full pointer-events-none group-hover:scale-110 transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center p-3 text-center bg-gradient-to-br from-bubble-100/70 via-white/80 to-soap-100/70">
              <span className="text-xl mb-1">💬</span>
              <p className="text-[11px] font-medium text-slate-700 line-clamp-3 leading-snug px-1">
                "{post.text}"
              </p>
            </div>
          )}

          {/* Liquid Glass Overlay inside ball */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-t from-bubble-900/40 via-transparent to-white/30 pointer-events-none" />

          {/* Upper Specular Lens Reflection (Glossy 2000s Highlight) */}
          <div 
            className="absolute rounded-full pointer-events-none"
            style={{
              top: "8%",
              left: "20%",
              width: "48%",
              height: "26%",
              background: "linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.1) 100%)",
              transform: "rotate(-25deg)",
              filter: "blur(0.5px)",
            }}
          />

          {/* Lower Ambient Reflection */}
          <div 
            className="absolute rounded-full pointer-events-none"
            style={{
              bottom: "7%",
              right: "22%",
              width: "36%",
              height: "14%",
              background: "linear-gradient(0deg, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0) 100%)",
              transform: "rotate(-15deg)",
            }}
          />

          {/* Bottom Floating Soap Badge */}
          <div className="absolute bottom-2 inset-x-0 flex justify-center pointer-events-none">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold text-white bg-slate-900/60 backdrop-blur-md border border-white/40 shadow-sm flex items-center gap-1 group-hover:bg-soap-600/90 transition-colors">
              <span>🧼</span>
              <span>{post.soap_count}</span>
              {hasMedia && <ImageIcon className="w-2.5 h-2.5 ml-0.5 opacity-80" />}
            </span>
          </div>
        </div>

        {/* Hover Action Hint Overlay */}
        <div className="absolute inset-0 rounded-full bg-bubble-950/40 backdrop-blur-[2px] opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-2 text-white pointer-events-none">
          <span className="text-xs font-bold tracking-wide drop-shadow-md flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
            Explorar Bolha
          </span>
          <span className="text-[9px] text-bubble-100 drop-shadow flex items-center gap-1 mt-0.5">
            <MessageCircle className="w-2.5 h-2.5" />
            Clique para ler
          </span>
        </div>
      </div>
    </motion.div>
  );
};
