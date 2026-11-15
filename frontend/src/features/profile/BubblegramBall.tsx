import React, { useRef } from "react";
import { motion } from "framer-motion";
import { Bubblegram } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { Image as ImageIcon } from "lucide-react";

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
  // Enlarged sizes (default 190px instead of 150px)
  const size = post.size || 190;
  const hasMedia = post.media && post.media.length > 0;
  const firstMedia = hasMedia ? post.media[0].media : null;

  return (
    <motion.div
      drag
      dragConstraints={dragConstraintsRef}
      dragElastic={0.2}
      dragMomentum={true}
      dragTransition={{ bounceStiffness: 280, bounceDamping: 20 }}
      onDragStart={() => {
        isDraggingRef.current = true;
      }}
      onDragEnd={() => {
        setTimeout(() => {
          isDraggingRef.current = false;
        }, 120);
      }}
      onClick={() => {
        if (!isDraggingRef.current) {
          onClick(post);
        }
      }}
      whileHover={{ scale: 1.04, zIndex: 30 }}
      whileDrag={{ scale: 1.08, zIndex: 40, cursor: "grabbing" }}
      initial={{ 
        x: post.initialX ?? 0, 
        y: post.initialY ?? 0, 
        scale: 0.9, 
        opacity: 0 
      }}
      animate={{ 
        scale: 1, 
        opacity: 1,
      }}
      transition={{ duration: 0.3 }}
      style={{
        width: size,
        height: size,
      }}
      className="absolute cursor-grab select-none touch-none group"
    >
      {/* 3D Bubble Sphere Body */}
      <div 
        className="relative w-full h-full rounded-full overflow-hidden p-2 transition-shadow duration-200 group-hover:shadow-[0_12px_32px_rgba(244,101,172,0.35)]"
        style={{
          background: "radial-gradient(circle at 35% 30%, rgba(255,255,255,0.95) 0%, rgba(255,230,242,0.75) 25%, rgba(244,101,172,0.55) 65%, rgba(123,99,255,0.45) 90%, rgba(255,255,255,0.9) 100%)",
          boxShadow: "inset -6px -8px 18px rgba(123,99,255,0.28), inset 4px 6px 14px rgba(255,255,255,0.95), 0 10px 24px -4px rgba(244,101,172,0.3)",
          border: "2px solid rgba(255, 255, 255, 0.9)",
        }}
      >
        {/* Post Content Interior */}
        <div className="w-full h-full rounded-full overflow-hidden relative bg-white flex items-center justify-center">
          {hasMedia && firstMedia ? (
            <img
              src={firstMedia}
              alt="Post preview"
              className="w-full h-full object-cover rounded-full pointer-events-none group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center p-4 text-center bg-gradient-to-br from-pink-50 via-white to-purple-50">
              <p className="text-xs font-semibold text-slate-800 line-clamp-4 leading-relaxed px-2">
                {post.text}
              </p>
            </div>
          )}

          {/* Liquid Glass Overlay inside ball */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-t from-slate-950/45 via-transparent to-white/20 pointer-events-none" />

          {/* Upper Specular Lens Reflection (Glossy Highlight) */}
          <div 
            className="absolute rounded-full pointer-events-none"
            style={{
              top: "8%",
              left: "20%",
              width: "46%",
              height: "26%",
              background: "linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.05) 100%)",
              transform: "rotate(-25deg)",
              filter: "blur(0.5px)",
            }}
          />

          {/* Bottom Soap Support Count Badge */}
          <div className="absolute bottom-2.5 inset-x-0 flex justify-center pointer-events-none">
            <span className="px-2.5 py-1 rounded-full text-[11px] font-bold text-white bg-slate-900/75 backdrop-blur-sm border border-white/40 shadow-sm flex items-center gap-1.5 group-hover:bg-pink-700/90 transition-colors">
              <SoapIcon size={13} />
              <span>{post.soap_count}</span>
              {hasMedia && <ImageIcon className="w-3 h-3 ml-0.5 opacity-80" />}
            </span>
          </div>
        </div>

        {/* Hover Action Label */}
        <div className="absolute inset-0 rounded-full bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-3 text-white pointer-events-none">
          <span className="text-xs font-bold drop-shadow">
            Abrir publicação
          </span>
        </div>
      </div>
    </motion.div>
  );
};
