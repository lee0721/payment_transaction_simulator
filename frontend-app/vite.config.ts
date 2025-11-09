import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = env.VITE_API_BASE ?? "http://localhost:8000";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: "0.0.0.0",
      proxy: {
        "/payment": {
          target: apiBase,
          changeOrigin: true,
        },
        "/transaction": {
          target: apiBase,
          changeOrigin: true,
        },
        "/stats": {
          target: apiBase,
          changeOrigin: true,
        },
        "/audit": {
          target: apiBase,
          changeOrigin: true,
        },
        "/admin": {
          target: apiBase,
          changeOrigin: true,
        }
      }
    },
    define: {
      __API_BASE__: JSON.stringify(apiBase),
    }
  };
});
