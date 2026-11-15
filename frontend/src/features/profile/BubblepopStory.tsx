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

  // Pick a subtle solid border from the brand palette without gradients
  const borderColors = [
    "border-pink-500/40",
    "border-purple-500/40",
    "border-lime-500/45",
  ];
  const ringColor = borderColors[story.id % borderColors.length];

  return (
    <div 
      className="flex flex-col items-center gap-1 flex-shrink-0 cursor-pointer group" 
      onClick={() => onClick(story)}
    >
      {/* Non-gradient bubble frame with low-opacity palette border */}
      <div className={`relative rounded-full p-[2px] border-2 ${ringColor} bg-white select-none transition-transform duration-150 group-hover:scale-105`}>
        <div className="relative w-15 h-15 rounded-full overflow-hidden border border-white bg-slate-100">
          <img
            src={story.image}
            alt={story.description || "Bubblepop"}
            className="w-full h-full object-cover rounded-full"
          />

          {/* Elongated reflection in bottom-right corner */}
          <div 
            className="absolute rounded-full pointer-events-none"
            style={{
              bottom: "6%",
              right: "8%",
              width: "48%",
              height: "14%",
              background: "linear-gradient(0deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0) 100%)",
              transform: "rotate(-18deg)",
            }}
          />
        </div>
      </div>

      {/* Countdown Label */}
      <div className="flex items-center gap-1 text-[10px] font-semibold text-slate-500 group-hover:text-pink-600 transition-colors">
        <Clock className="w-2.5 h-2.5 text-slate-400" />
        <span>{hoursLeft}</span>
      </div>
    </div>
  );
};
