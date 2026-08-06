import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendPort = Number(env.VITE_BACKEND_PORT || process.env.VITE_BACKEND_PORT || 8000);
  const backendHost = env.VITE_BACKEND_HOST || process.env.VITE_BACKEND_HOST || 'localhost';
  const target = `http://${backendHost}:${backendPort}`;

  console.log(`\n[vite] Backend proxy target → ${target}`);
  console.log(`[vite]  (override with: set VITE_BACKEND_PORT=8001 && npm run dev)\n`);

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      strictPort: false,
      host: true,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          secure: false,
          ws: false,
          configure: (proxy) => {
            proxy.on('error', (err, _req, _res) => {
              console.error(
                `\n[proxy] ⚠ Backend proxy error — is the FastAPI server running on ${target} ?\n`
                + `[proxy]    Details: ${err.message}\n`
                + `[proxy]    Start with:  python server.py\n`,
              );
            });
            proxy.on('proxyReq', (_proxyReq, req, _res) => {
              console.log(`[proxy] → ${req.method} ${req.url}  →  ${backendHost}:${backendPort}`);
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log(`[proxy] ← ${req.method} ${req.url}   status=${proxyRes.statusCode}`);
            });
          },
          timeout: 5 * 60 * 1000, // 5 minutes — LangGraph pipeline can be slow
          proxyTimeout: 5 * 60 * 1000,
        },
        '/uploads': {
          target,
          changeOrigin: true,
          secure: false,
        },
        '/reports': {
          target,
          changeOrigin: true,
          secure: false,
        },
      },
    },
    preview: {
      port: 4173,
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      chunkSizeWarningLimit: 1200,
    },
  };
});
