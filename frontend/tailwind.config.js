/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Segoe UI"',
          '-apple-system',
          'BlinkMacSystemFont',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif',
        ],
      },
      colors: {
        // Official Brand Palette
        pink: {
          50: "#FDF2F8",
          100: "#FCE7F3",
          200: "#FBCFE8",
          300: "#F9A8D4",
          400: "#F472B6",
          500: "#F465AC", // Primary Brand Pink
          600: "#DB2777",
          700: "#BE185D",
          800: "#9D174D",
          900: "#831843",
        },
        purple: {
          50: "#F5F3FF",
          100: "#EDE9FE",
          200: "#DDD6FE",
          300: "#C4B5FD",
          400: "#A78BFA",
          500: "#7B63FF", // Brand Purple
          600: "#6949F5",
          700: "#5B36DE",
          800: "#4C1D95",
          900: "#3B0764",
        },
        lime: {
          50: "#F7FEE7",
          100: "#ECFCCB",
          200: "#D9F99D",
          300: "#BEF264",
          400: "#4BF521", // Brand Lime Green
          500: "#3DD117",
          600: "#2FA40E",
          700: "#237A0A",
          800: "#1A5A07",
          900: "#144306",
        },
      },
      boxShadow: {
        "panel": "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)",
        "panel-hover": "0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05)",
        "bubble": "inset -6px -8px 16px rgba(123, 99, 255, 0.25), inset 4px 6px 14px rgba(255, 255, 255, 0.95), 0 8px 24px -4px rgba(244, 101, 172, 0.3)",
        "bubble-pink": "inset -6px -8px 16px rgba(190, 24, 93, 0.25), inset 4px 6px 14px rgba(255, 255, 255, 0.95), 0 8px 24px -4px rgba(244, 101, 172, 0.35)",
        "glossy-btn": "inset 0 1px 1px 0 rgba(255, 255, 255, 0.75), inset 0 -2px 3px 0 rgba(0, 0, 0, 0.12), 0 2px 6px 0 rgba(244, 101, 172, 0.25)",
      },
      borderRadius: {
        "sm": "2px",
        "DEFAULT": "4px",
        "md": "6px",
      },
    },
  },
  plugins: [],
};
