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
      {/* 3D Glossy Soap Bar */}
      <defs>
        <linearGradient id="soap_body" x1="2" y1="4" x2="22" y2="20" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FBCFE8" />
          <stop offset="0.45" stopColor="#F465AC" />
          <stop offset="1" stopColor="#DB2777" />
        </linearGradient>
        <linearGradient id="soap_glint" x1="4" y1="4" x2="16" y2="12" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFFFFF" stopOpacity="0.8" />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
        </linearGradient>
        <radialGradient id="bubble_mini" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(19 5) scale(3)">
          <stop stopColor="#FFFFFF" />
          <stop offset="0.7" stopColor="#7B63FF" />
          <stop offset="1" stopColor="#F465AC" />
        </radialGradient>
      </defs>

      {/* Main soap bar base */}
      <rect
        x="3"
        y="6"
        width="18"
        height="12"
        rx="5"
        fill="url(#soap_body)"
        stroke="#BE185D"
        strokeWidth="1.2"
      />

      {/* Specular light highlight */}
      <path
        d="M6 8C7.5 7 11 7 15 7.5C13 8.5 8 9 6 8Z"
        fill="url(#soap_glint)"
      />

      {/* Subtle soap imprint line */}
      <path
        d="M7 12C9.5 13 14.5 13 17 12"
        stroke="#FFFFFF"
        strokeOpacity="0.65"
        strokeWidth="1.2"
        strokeLinecap="round"
      />

      {/* Floating suds / mini bubble */}
      <circle cx="18.5" cy="4.5" r="2.5" fill="url(#bubble_mini)" stroke="#FFFFFF" strokeWidth="0.8" />
      <circle cx="14" cy="3" r="1.5" fill="#FFFFFF" fillOpacity="0.8" />
    </svg>
  );
};
