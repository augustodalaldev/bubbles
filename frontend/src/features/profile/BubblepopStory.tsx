import React from "react";
import { motion } from "framer-motion";
import { Bubblepop } from "@/types";
import { Clock } from "lucide-react";

interface BubblepopStoryProps {
  story: Bubblepop;
  onClick: (story: Bubblepop) => void;
}

export const BubblepopStory: React.FC<BubblepopStoryProps> = ({ story, onClick }) => {
  // Calculate hours remaining mock
  const calculateHoursLeft = () => {
    try {
      const expires = new Date(story.expires_at).getTime();
      const now = new Date("2026-11-14T20:00:00Z").getTime();
      const diffHours = Math.max(1, Math.round((expires - now) / (1000 * 60 * 60)));
      return `${diffHours}h`;
    } catch {
      return "4h";
    }
  };

  const hoursLeft = calculateHoursLeft();
  const isExpiringSoon = hoursLeft === "1h" || hoursLeft === "2h" || hoursLeft === "3h";

  return (
    <div className="flex flex-col items-center gap-1.5 flex-shrink-0 group cursor-pointer" onClick={() => onClick(story)}>
      {/* Outer Pulsing Bubble Ring */}
      <motion.div
        className="relative rounded-full p-[3px] select-none"
        animate={{
          scale: [1, 1.04, 1],
        }}
        transition={{
          repeat: Infinity,
          duration: isExpiringSoon ? 1.5 : 2.5,
          ease: "easeInOut",
        }}
      >
        {/* Iridescent water ripple border */}
        <div 
          className={`absolute inset-0 rounded-full ${
            isExpiringSoon 
              ? "bg-gradient-to-tr from-soap-500 via-amber-400 to-bubble-400 animate-spin-slow"
              : "bg-gradient-to-tr from-bubble-400 via-sky-300 to-soap-400"
          } p-[2.5px] shadow-[0_0_15px_rgba(8,196,219,0.45)]`}
        />

        {/* Bubblepop Ball */}
        <div className="relative w-16 h-16 sm:w-18 sm:h-18 rounded-full overflow-hidden border-2 border-white/90 shadow-md">
          <img
            src={story.image}
            alt={story.description || "Bubblepop"}
            className="w-full h-full object-cover rounded-full group-hover:scale-110 transition-transform duration-300"
          />

          {/* Internal Glass Highlight */}
          <div 
            className="absolute rounded-full pointer-events-none"
            style={{
              top: "10%",
              left: "20%",
              width: "45%",
              height: "25%",
              background: "linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.1) 100%)",
              transform: "rotate(-30deg)",
              filter: "blur(0.5px)",
            }}
          />

          {/* Subtle pop warning badge when expiring */}
          {isExpiringSoon && (
            <motion.div 
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ repeat: Infinity, duration: 1 }}
              className="absolute top-1 right-1 w-3 h-3 rounded-full bg-soap-500 border border-white flex items-center justify-center text-[8px] text-white"
            >
              💥
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Countdown Label (Indicates that this bubble will pop soon) */}
      <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/70 backdrop-blur-sm border border-white/80 shadow-xs text-[10px] font-semibold text-slate-700 group-hover:text-soap-600 transition-colors">
        <Clock className="w-2.5 h-2.5 text-soap-500" />
        <span>estoura em {hoursLeft}</span>
      </div>
    </div>
  );
};
