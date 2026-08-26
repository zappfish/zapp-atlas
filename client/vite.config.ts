import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// The editing client renders *inside* the server-rendered shell: FastAPI
// serves the HTML document (html/templates/edit.html, which extends
// base.html) and this build only supplies the JS/CSS that document loads.
// There is no index.html here — the page comes from the server in both dev
// and production, so the React app inherits the site header, nav, and styles.
//
//   dev   FastAPI serves /edit/ and points <script> at the Vite dev server,
//         so HMR still works.
//   prod  `npm run build` emits assets plus .vite/manifest.json; the server
//         reads the manifest to find the hashed filenames.
//
// The API is no longer proxied: the page is served from the FastAPI origin,
// so a request to /api from the browser already lands on the backend.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  const devPort = env.DEV_PORT ? Number(env.DEV_PORT) : 5173;

  return {
    base: '/edit/',
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    server: {
      port: devPort,
      // The document is served from the FastAPI origin, so the asset URLs the
      // dev server generates must be absolute back to itself.
      origin: `http://localhost:${devPort}`,
    },
    build: {
      // The server needs the hashed filenames to build its <script>/<link>
      // tags, and without a manifest it cannot know them.
      manifest: true,
      rollupOptions: {
        // main.tsx is the entry directly, in place of an index.html.
        input: path.resolve(__dirname, 'src/main.tsx'),
      },
    },
  };
});
