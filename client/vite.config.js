import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig(({ mode }) => ({
  base: mode === "phenodemo" ? "./" : "/",
  plugins: [react()],
  resolve: {
      alias: {
          '@': path.resolve(__dirname, 'src')
      }
  },
  build: {
    rollupOptions: {
      input: mode === "phenodemo"
        ? { phenodemo: path.resolve(__dirname, "phenodemo.html") }
        : { main: path.resolve(__dirname, "index.html") },
    }
  },
}));
