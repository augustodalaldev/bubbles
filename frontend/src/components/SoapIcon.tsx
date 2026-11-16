import React from "react";

interface SoapIconProps {
  className?: string;
  size?: number;
}

export const SoapIcon: React.FC<SoapIconProps> = ({ className = "", size = 16 }) => {
  return (
    <img
      src="/soap.svg"
      alt="soap"
      style={{
        width: `${size}px`,
        height: `${size}px`,
      }}
      className={`inline-block flex-shrink-0 object-contain select-none pointer-events-none ${className}`}
    />
  );
};
