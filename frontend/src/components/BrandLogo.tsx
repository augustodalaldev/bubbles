import React from "react";

interface BrandLogoProps {
  className?: string;
  height?: number;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({ className = "", height = 30 }) => {
  return (
    <img
      src="/logo.svg"
      alt="Bubbles"
      style={{ height: `${height}px`, width: "auto" }}
      className={`select-none object-contain ${className}`}
    />
  );
};
