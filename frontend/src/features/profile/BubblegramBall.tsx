import React, { useRef } from "react";
import { motion } from "framer-motion";
import { Bubblegram } from "@/types";
import { SoapIcon } from "@/components/SoapIcon";
import { BubbleOverlay } from "@/components/BubbleOverlay";
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
  const hasMedia = post.type === "MEDIA" && post.media && post.media.length > 0;
  const firstMedia = hasMedia ? post.media[0].media : null;

  // Photo posts: Large round sphere (~195px)
  // Text posts: Classic UI rectangular card (~175x115px)
  const isRoundPhoto = hasMedia;
  const width = isRoundPhoto ? (post.size || 195) : 175;
  const height = isRoundPhoto ? (post.size || 195) : 115;

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
      whileHover={{ scale: 1.03, zIndex: 30 }}
      whileDrag={{ scale: 1.05, zIndex: 40, cursor: "grabbing" }}
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
        width,
        height,
      }}
      className="absolute cursor-grab select-none touch-none group"
    >
      {isRoundPhoto ? (
        /* Round Bubble Sphere with User's bubble.svg Overlay */
        <div className="relative w-full h-full rounded-full overflow-hidden bg-slate-100 shadow-md transition-shadow group-hover:shadow-lg">
          <img
            src={firstMedia!}
            alt="Publicação"
            className="w-full h-full object-cover rounded-full pointer-events-none group-hover:scale-105 transition-transform duration-300"
          />

          {/* User's bubble.svg overlay applied over round photo */}
          <BubbleOverlay opacity={0.7} />

          {/* Subtle bottom shadow to enhance soap badge readability */}
          <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-black/60 to-transparent pointer-events-none z-10" />

          {/* Bottom Soap Badge */}
          <div className="absolute bottom-2.5 inset-x-0 flex justify-center pointer-events-none z-20">
            <span className="px-2.5 py-1 rounded-full text-[11px] font-bold text-white bg-slate-900/80 backdrop-blur-sm shadow-sm flex items-center gap-1.5 group-hover:bg-pink-700/90 transition-colors">
              <SoapIcon size={18} />
              <span>{post.soap_count}</span>
              <ImageIcon className="w-3 h-3 ml-0.5 opacity-80" />
            </span>
          </div>
        </div>
      ) : (
        /* Straight UI-aesthetic rectangular text card (rounded-sm, matching UI panels) */
        <div className="relative w-full h-full rounded-sm bg-white border border-slate-200 shadow-sm flex flex-col justify-between transition-all group-hover:border-slate-300 group-hover:shadow-md overflow-hidden">
          {/* Subtle top header bar matching UI panel aesthetic */}
          <div className="bg-slate-50 border-b border-slate-200 px-2 py-1 flex items-center justify-between text-[10px] text-slate-500 font-semibold pointer-events-none">
            <span>Texto</span>
            <span className="flex items-center gap-1 text-slate-700">
              <SoapIcon size={15} />
              <span>{post.soap_count}</span>
            </span>
          </div>

          {/* Text Content */}
          <div className="p-2.5 flex-1 flex items-center pointer-events-none">
            <p className="text-[11px] font-medium text-slate-800 line-clamp-3 leading-relaxed">
              "{post.text}"
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
};
