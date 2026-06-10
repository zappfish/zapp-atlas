import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// The editing client is served under /edit (FastAPI mounts client/dist there in
// production; the Vite dev server uses the same base). API calls are proxied to
// the FastAPI backend during development.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  const apiPort = env.API_PORT || '8000';
  const apiTarget = `http://localhost:${apiPort}`;

  return {
    base: '/edit/',
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    server: {
      port: env.DEV_PORT ? Number(env.DEV_PORT) : 5173,
      proxy: {
        // The read-write JSON API. Read-only HTML pages are developed against
        // uvicorn directly, so only /api needs proxying here.
        '/api': apiTarget,
      },
    },
  };
});
