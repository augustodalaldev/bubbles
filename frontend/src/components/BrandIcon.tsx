import React from "react";

interface BrandIconProps {
  className?: string;
  size?: number;
}

export const BrandIcon: React.FC<BrandIconProps> = ({ className = "", size = 32 }) => {
  return (
    <svg
      width={size}
      height={(size * 147) / 154}
      viewBox="0 0 154 147"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Green Bubble (Bottom-Left) */}
      <g clipPath="url(#brand_clip0)">
        <g opacity="0.85">
          <mask id="brand_mask0" maskUnits="userSpaceOnUse" x="48" y="85" width="62" height="62">
            <path d="M110 116C110 98.8792 96.1208 85 79 85C61.8792 85 48 98.8792 48 116C48 133.121 61.8792 147 79 147C96.1208 147 110 133.121 110 116Z" fill="white" />
          </mask>
          <g mask="url(#brand_mask0)">
            <path d="M79 147C96.1208 147 110 133.121 110 116C110 98.8792 96.1208 85 79 85C61.8792 85 48 98.8792 48 116C48 133.121 61.8792 147 79 147Z" fill="url(#brand_radial_green)" />
            <path d="M76.1345 112.613C94.8379 112.613 110 106.432 110 98.8067C110 91.1815 94.8379 85 76.1345 85C57.431 85 42.2689 91.1815 42.2689 98.8067C42.2689 106.432 57.431 112.613 76.1345 112.613Z" fill="url(#brand_linear_gloss)" />
            <path d="M98.22 95.236C103.757 100.889 105.079 108.573 101.174 112.398C94.733 117.881 93.203 108.988 89.16 104.277C83.623 98.624 77.217 95.752 81.122 91.927C85.028 88.101 92.683 89.583 98.22 95.236Z" fill="white" fillOpacity="0.8" />
          </g>
        </g>
      </g>

      {/* Pink Bubble (Top-Left, Largest) */}
      <g clipPath="url(#brand_clip1)">
        <g opacity="0.9">
          <mask id="brand_mask1" maskUnits="userSpaceOnUse" x="0" y="0" width="106" height="106">
            <path d="M106 53C106 23.7289 82.2711 0 53 0C23.7289 0 0 23.7289 0 53C0 82.2711 23.7289 106 53 106C82.2711 106 106 82.2711 106 53Z" fill="white" />
          </mask>
          <g mask="url(#brand_mask1)">
            <path d="M53 106C82.2711 106 106 82.2711 106 53C106 23.7289 82.2711 0 53 0C23.7289 0 0 23.7289 0 53C0 82.2711 23.7289 106 53 106Z" fill="url(#brand_radial_pink)" />
            <path d="M48.1008 47.2101C80.0777 47.2101 106 36.6417 106 23.605C106 10.5683 80.0777 0 48.1008 0C16.124 0 -9.79832 10.5683 -9.79832 23.605C-9.79832 36.6417 16.124 47.2101 48.1008 47.2101Z" fill="url(#brand_linear_gloss)" />
            <path d="M85.86 17.5C95.326 27.165 97.587 40.302 90.91 46.843C79.899 56.216 77.283 41.011 70.37 32.958C60.903 23.293 49.951 18.383 56.629 11.843C63.306 5.302 76.394 7.835 85.86 17.5Z" fill="white" fillOpacity="0.85" />
          </g>
        </g>
      </g>

      {/* Purple Bubble (Right) */}
      <g clipPath="url(#brand_clip2)">
        <g opacity="0.9">
          <mask id="brand_mask2" maskUnits="userSpaceOnUse" x="74" y="44" width="80" height="80">
            <path d="M154 84C154 61.9086 136.091 44 114 44C91.9086 44 74 61.9086 74 84C74 106.091 91.9086 124 114 124C136.091 124 154 106.091 154 84Z" fill="white" />
          </mask>
          <g mask="url(#brand_mask2)">
            <path d="M114 124C136.091 124 154 106.091 154 84C154 61.9086 136.091 44 114 44C91.9086 44 74 61.9086 74 84C74 106.091 91.9086 124 114 124Z" fill="url(#brand_radial_purple)" />
            <path d="M110.303 79.6303C134.436 79.6303 154 71.6542 154 61.8151C154 51.9761 134.436 44 110.303 44C86.1691 44 66.605 51.9761 66.605 61.8151C66.605 71.6542 86.1691 79.6303 110.303 79.6303Z" fill="url(#brand_linear_gloss)" />
            <path d="M138.8 57.208C145.944 64.502 147.65 74.417 142.611 79.353C134.301 86.428 132.327 74.952 127.109 68.874C119.965 61.58 111.699 57.874 116.739 52.938C121.778 48.002 131.656 49.913 138.8 57.208Z" fill="white" fillOpacity="0.85" />
          </g>
        </g>
      </g>

      <defs>
        <radialGradient id="brand_radial_green" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(79 116) rotate(90.9629) scale(31.0044)">
          <stop stopColor="white" stopOpacity="0.45" />
          <stop offset="0.9" stopColor="#4BF521" />
        </radialGradient>
        <radialGradient id="brand_radial_pink" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(53 53) rotate(90.9629) scale(53.0075)">
          <stop stopColor="white" stopOpacity="0.45" />
          <stop offset="0.9" stopColor="#F465AC" />
        </radialGradient>
        <radialGradient id="brand_radial_purple" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(114 84) rotate(90.9629) scale(40.0056)">
          <stop stopColor="white" stopOpacity="0.45" />
          <stop offset="0.9" stopColor="#7B63FF" />
        </radialGradient>
        <linearGradient id="brand_linear_gloss" x1="0" y1="0" x2="0" y2="1" gradientUnits="userSpaceOnUse">
          <stop stopColor="white" stopOpacity="0.9" />
          <stop offset="0.8" stopColor="#FFB7DB" stopOpacity="0" />
        </linearGradient>
        <clipPath id="brand_clip0">
          <rect width="62" height="62" fill="white" transform="translate(48 85)" />
        </clipPath>
        <clipPath id="brand_clip1">
          <rect width="106" height="106" fill="white" />
        </clipPath>
        <clipPath id="brand_clip2">
          <rect width="80" height="80" fill="white" transform="translate(74 44)" />
        </clipPath>
      </defs>
    </svg>
  );
};
