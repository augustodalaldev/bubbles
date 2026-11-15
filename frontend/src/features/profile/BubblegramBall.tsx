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
  const hasMedia = post.type === "MEDIA" && post.media && post.media.length > 0;
  const firstMedia = hasMedia ? post.media[0].media : null;

  // Photo posts: Large round sphere (~190-210px)
  // Text posts: Smaller rounded rectangle (~170x110px)
  const isRoundPhoto = hasMedia;
  const width = isRoundPhoto ? (post.size || 195) : 170;
  const height = isRoundPhoto ? (post.size || 195) : 110;

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
      whileDrag={{ scale: 1.06, zIndex: 40, cursor: "grabbing" }}
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
        /* Round Borderless Sphere for Media Posts */
        <div className="relative w-full h-full rounded-full overflow-hidden bg-slate-100 shadow-md transition-shadow group-hover:shadow-lg">
          <img
            src={firstMedia!}
            alt="Publicação"
            className="w-full h-full object-cover rounded-full pointer-events-none group-hover:scale-105 transition-transform duration-300"
          />

          {/* Subtle bottom shadow to enhance soap badge readability */}
          <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-black/60 to-transparent pointer-events-none" />

          {/* Bottom Soap Badge */}
          <div className="absolute bottom-2.5 inset-x-0 flex justify-center pointer-events-none">
            <span className="px-2.5 py-1 rounded-full text-[11px] font-bold text-white bg-slate-900/80 backdrop-blur-sm shadow-sm flex items-center gap-1.5 group-hover:bg-pink-700/90 transition-colors">
              <SoapIcon size={13} />
              <span>{post.soap_count}</span>
              <ImageIcon className="w-3 h-3 ml-0.5 opacity-80" />
            </span>
          </div>
        </div>
      ) : (
        /* Smaller Rounded Rectangle for Text Posts (Borderless) */
        <div className="relative w-full h-full rounded-xl overflow-hidden p-3 bg-white shadow-sm flex flex-col justify-between transition-shadow group-hover:shadow-md">
          {/* Text Content */}
          <p className="text-[11px] font-semibold text-slate-800 line-clamp-3 leading-relaxed pointer-events-none">
            "{post.text}"
          </p>

          {/* Bottom Bar: Soap badge and type label */}
          <div className="flex items-center justify-between pt-1 border-t border-slate-100 pointer-events-none">
            <span className="text-[10px] font-bold text-slate-700 flex items-center gap-1">
              <SoapIcon size={12} />
              <span>{post.soap_count}</span>
            </span>
            <span className="text-[9px] text-slate-400">
              texto
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
};
