import React from "react";
import { Bubblepop } from "@/types";
import { BubbleOverlay } from "@/components/BubbleOverlay";
import { hoursLeft } from "@/utils/time";
import { Plus, Clock } from "lucide-react";

interface FeedBubblepopsTrayProps {
  bubblepops: Bubblepop[];
  onSelectBubblepop: (story: Bubblepop) => void;
  onOpenCreateModal?: () => void;
}

export const FeedBubblepopsTray: React.FC<FeedBubblepopsTrayProps> = ({
  bubblepops,
  onSelectBubblepop,
  onOpenCreateModal,
}) => {
  return (
    <div className="panel-classic mb-4">
      <div className="panel-classic-header flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-pink-600" />
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
            Bubblepops
          </h2>
        </div>
        <span className="text-[10px] text-slate-500 font-normal">
          Mídias efêmeras
        </span>
      </div>

      <div className="p-3">
        <div className="flex items-center gap-3 overflow-x-auto pb-1 scrollbar-thin">
          
          {/* Create Bubblepop Action Button */}
          <button
            onClick={onOpenCreateModal}
            className="flex flex-col items-center flex-shrink-0 group"
          >
            <div className="w-14 h-14 rounded-full border-2 border-dashed border-pink-300 bg-pink-50 flex items-center justify-center text-pink-600 group-hover:bg-pink-100 group-hover:border-pink-500 transition-all">
              <Plus className="w-5 h-5" />
            </div>
            <span className="text-[11px] font-medium text-slate-700 mt-1.5 group-hover:text-pink-600">
              Novo pop
            </span>
          </button>

          {/* Bubblepops list */}
          {bubblepops.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectBubblepop(item)}
              className="flex flex-col items-center flex-shrink-0 cursor-pointer group"
            >
              {/* Spherical container with 3D BubbleOverlay */}
              <div className="relative w-14 h-14 rounded-full overflow-hidden flex-shrink-0 shadow-sm transition-transform duration-200 group-hover:scale-105">
                <img
                  src={item.image}
                  alt={item.description || item.user.name}
                  className="w-full h-full object-cover"
                />
                {/* Official bubble specular highlight overlay */}
                <BubbleOverlay opacity={0.5} />
              </div>

              {/* Author name and remaining time indicator */}
              <span className="text-[11px] font-medium text-slate-800 mt-1 max-w-[64px] truncate text-center group-hover:text-pink-600">
                {item.user.name.split(" ")[0]}
              </span>
              <span className="text-[9px] text-slate-400 font-mono -mt-0.5">
                {hoursLeft(item.expires_at)}
              </span>
            </div>
          ))}

        </div>
      </div>
    </div>
  );
};
