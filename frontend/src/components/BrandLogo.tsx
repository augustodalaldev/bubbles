import React from "react";
import { BrandIcon } from "./BrandIcon";

interface BrandLogoProps {
  className?: string;
  height?: number;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({ className = "", height = 30 }) => {
  return (
    <div className={`flex items-center gap-2 select-none ${className}`}>
      <span
        style={{
          fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif',
          fontWeight: 800,
          fontSize: `${height * 0.85}px`,
          letterSpacing: "-0.04em",
          color: "#F465AC",
          lineHeight: 1,
        }}
      >
        Bubbles
      </span>
      <BrandIcon size={height * 1.1} />
    </div>
  );
};
