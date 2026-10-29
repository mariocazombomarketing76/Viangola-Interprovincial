import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

const rawPort = process.env.PORT;
const port = rawPort ? Number(rawPort) : 5173;

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

const basePath = process.env.BASE_PATH ?? "/";

// Em desenvolvimento o frontend é servido pelo Vite e o /api é encaminhado
// para o backend FastAPI (pnpm --filter @workspace/api-server run dev).
const apiTarget = process.env.API_PROXY_TARGET ?? "http://127.0.0.1:8000";

export default defineConfig({
  base: basePath,
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "src"),
    },
  },
  root: path.resolve(import.meta.dirname),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist"),
    emptyOutDir: true,
  },
  server: {
    port,
    host: "0.0.0.0",
    // Host-checking mantém-se estrito por omissão. Hosts de preview são
    // acrescentados via __VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS (o Vite só
    // aplica a variável quando allowedHosts é um array).
    allowedHosts: [],
    proxy: {
      "/api": apiTarget,
    },
    fs: {
      strict: true,
    },
  },
  preview: {
    port,
    host: "0.0.0.0",
    allowedHosts: [],
    proxy: {
      "/api": apiTarget,
    },
  },
});
