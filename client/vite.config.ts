import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    proxy: {
      '/observation': 'http://localhost:5001',
      '/normalize': 'http://localhost:5001',
      '/health': 'http://localhost:5001',
    }
  }
});

