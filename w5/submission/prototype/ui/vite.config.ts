import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api -> FastAPI backend (uvicorn server:app --port 8000),
// so the frontend has no CORS concerns and ships no hardcoded backend URL.
// app is served under /2905/ (keep in sync with server.py BASE_PATH)
export default defineConfig({
  base: "/2905/",
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/2905/api": "http://localhost:8000",
    },
  },
});
