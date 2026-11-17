import React from "react";
import { Bubblepop } from "@/types";
import { Clock } from "lucide-react";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { hoursLeft } from "@/utils/time";

interface BubblepopStoryProps {
  story: Bubblepop;
  onClick: (story: Bubblepop) => void;
}

export const BubblepopStory: React.FC<BubblepopStoryProps> = ({ story, onClick }) => {
  const hoursLeftLabel = hoursLeft(story.expires_at);

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
        <span>{hoursLeftLabel}</span>
      </div>
    </div>
  );
};
