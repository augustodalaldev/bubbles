import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Backend the dev server proxies /api and /media to. Override to point at another backend, e.g. the
// demo one: VITE_API_TARGET=http://127.0.0.1:8001 npm run dev
const apiTarget = process.env.VITE_API_TARGET ?? "http://127.0.0.1:8000";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: apiTarget,
        changeOrigin: true,
      },
      "/media": {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
});
