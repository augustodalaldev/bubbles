import React from "react";

interface SoapIconProps {
  className?: string;
  size?: number;
}

export const SoapIcon: React.FC<SoapIconProps> = ({ className = "", size = 16 }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`inline-block flex-shrink-0 ${className}`}
    >
      {/* Clean, minimalist soap bar with floating suds */}
      {/* Main smooth soap bar */}
      <rect
        x="2.5"
        y="8.5"
        width="17"
        height="11"
        rx="4.5"
        fill="#F465AC"
      />
      {/* Specular curved reflection line */}
      <path
        d="M6 11.5C8 10 12 10 15 11"
        stroke="#FFFFFF"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
      {/* Floating mini bubble 1 */}
      <circle
        cx="18"
        cy="5.5"
        r="3"
        fill="#7B63FF"
        stroke="#FFFFFF"
        strokeWidth="0.8"
      />
      {/* Floating mini bubble 2 */}
      <circle
        cx="12.5"
        cy="4.5"
        r="1.8"
        fill="#F465AC"
        fillOpacity="0.85"
      />
    </svg>
  );
};
