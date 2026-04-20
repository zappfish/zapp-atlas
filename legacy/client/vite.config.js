import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  const apiPort = env.API_PORT || '8000';
  const apiTarget = `http://localhost:${apiPort}`;

  return {
    base: mode === "phenodemo" ? "./" : "/",
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src')
        }
    },
    server: {
      port: env.DEV_PORT ? Number(env.DEV_PORT) : 5173,
      proxy: {
        '/health': apiTarget,
        '/studies': apiTarget,
        '/experiments': apiTarget,
      },
    },
    build: {
      rollupOptions: {
        input: mode === "phenodemo"
          ? { phenodemo: path.resolve(__dirname, "phenodemo.html") }
          : { main: path.resolve(__dirname, "index.html") },
      }
    },
  };
});
