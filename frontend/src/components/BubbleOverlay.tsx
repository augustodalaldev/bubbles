import React from "react";

interface BubbleOverlayProps {
  className?: string;
  opacity?: number;
}

export const BubbleOverlay: React.FC<BubbleOverlayProps> = ({ className = "", opacity = 1 }) => {
  return (
    <img
      src="/bubble.svg"
      alt=""
      aria-hidden="true"
      style={{ opacity }}
      className={`absolute inset-0 w-full h-full object-cover pointer-events-none select-none z-10 ${className}`}
    />
  );
};
