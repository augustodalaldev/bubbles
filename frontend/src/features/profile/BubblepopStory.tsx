import React from "react";
import { Bubblepop } from "@/types";
import { Clock } from "lucide-react";
import { BubbleOverlay } from "@/components/BubbleOverlay";

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
      className="flex flex-col items-center gap-1.5 flex-shrink-0 cursor-pointer group" 
      onClick={() => onClick(story)}
    >
      {/* Clean circular story avatar with authentic bubble SVG overlay */}
      <div className="relative w-14 h-14 rounded-full overflow-hidden bg-slate-100 shadow-sm transition-transform duration-150 group-hover:scale-105">
        <img
          src={story.image}
          alt={story.description || "Bubblepop"}
          className="w-full h-full object-cover"
        />
        {/* User's authentic bubble reflection SVG overlay with subtle opacity */}
        <BubbleOverlay opacity={0.5} />
      </div>

      {/* Countdown Label */}
      <div className="flex items-center gap-1 text-[10px] font-medium text-slate-500 group-hover:text-pink-600 transition-colors">
        <Clock className="w-2.5 h-2.5 text-slate-400" />
        <span>{hoursLeft}</span>
      </div>
    </div>
  );
};
