import React from "react";
import { Bubblepop } from "@/types";
import { Clock } from "lucide-react";

interface BubblepopStoryProps {
  story: Bubblepop;
  onClick: (story: Bubblepop) => void;
}

export const BubblepopStory: React.FC<BubblepopStoryProps> = ({ story, onClick }) => {
  const calculateHoursLeft = () => {
    try {
      const expires = new Date(story.expires_at).getTime();
      const now = new Date("2026-11-15T19:00:00Z").getTime();
      const diffHours = Math.max(1, Math.round((expires - now) / (1000 * 60 * 60)));
      return `${diffHours}h`;
    } catch {
      return "4h";
    }
  };

  const hoursLeft = calculateHoursLeft();

  return (
    <div 
      className="flex flex-col items-center gap-1 flex-shrink-0 cursor-pointer group" 
      onClick={() => onClick(story)}
    >
      {/* Static Bubble Ring without CPU-heavy pulsing loop */}
      <div className="relative rounded-full p-[2px] bg-gradient-to-tr from-pink-500 via-pink-400 to-purple-400 select-none shadow-sm transition-transform duration-150 group-hover:scale-105">
        <div className="relative w-16 h-16 rounded-full overflow-hidden border-2 border-white bg-slate-100">
          <img
            src={story.image}
            alt={story.description || "Bubblepop"}
            className="w-full h-full object-cover rounded-full"
          />

          {/* Internal Glass Highlight */}
          <div 
            className="absolute rounded-full pointer-events-none"
            style={{
              top: "8%",
              left: "20%",
              width: "45%",
              height: "25%",
              background: "linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.05) 100%)",
              transform: "rotate(-30deg)",
            }}
          />
        </div>
      </div>

      {/* Clean Countdown Label (No emojis) */}
      <div className="flex items-center gap-1 text-[10px] font-semibold text-slate-600 group-hover:text-pink-600 transition-colors">
        <Clock className="w-2.5 h-2.5 text-slate-400" />
        <span>{hoursLeft}</span>
      </div>
    </div>
  );
};
