import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Туннели для проверки Mini App в Telegram (HTTPS-адрес даёт сам туннель).
    allowedHosts: [".trycloudflare.com", ".ngrok-free.app", ".ngrok.app", ".loca.lt"],
    // С одного адреса отдаём и интерфейс, и API: Telegram требует HTTPS, а туннель один.
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
