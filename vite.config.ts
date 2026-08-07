import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  // Production: Use VITE_API_URL if set (Render backend URL)
  // Development: Use local backend configuration
  const isProduction = mode === 'production';
  const apiUrl = env.VITE_API_URL;
  
  let backendPort = 8000;
  let backendHost = 'localhost';
  let target = `http://${backendHost}:${backendPort}`;
  
  if (isProduction && apiUrl) {
    // Extract host and port from full URL
    try {
      const urlObj = new URL(apiUrl);
      backendHost = urlObj.hostname;
      const portValue = urlObj.port || (urlObj.protocol === 'https:' ? '443' : '80');
      backendPort = Number(portValue);
      target = apiUrl;
      console.log(`\n[vite] PRODUCTION MODE - Backend API → ${target}`);
    } catch (e) {
      console.warn(`[vite] Invalid VITE_API_URL "${apiUrl}", falling back to localhost:8000`);
    }
  } else {
    // Development mode
    const customPort = Number(env.VITE_BACKEND_PORT || process.env.VITE_BACKEND_PORT || 8000);
    const customHost = env.VITE_BACKEND_HOST || process.env.VITE_BACKEND_HOST || 'localhost';
    backendPort = customPort;
    backendHost = customHost;
    target = `http://${backendHost}:${backendPort}`;
    console.log(`\n[vite] DEVELOPMENT MODE - Backend proxy → ${target}`);
    console.log(`[vite]  (override with: set VITE_BACKEND_PORT=8001 && npm run dev)\n`);
  }
  
  console.log(`[vite]  For production deployment on Vercel:`);
  console.log(`[vite]  Set VITE_API_URL=https://your-render-app.onrender.com in Vercel settings\n`);

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    define: {
      // Expose VITE_API_URL to the frontend bundle at build time.
      // In production (Vercel), set this to your Render backend URL.
      // In dev, the proxy below handles /api/* automatically.
      '__BACKEND_URL__': JSON.stringify(env.VITE_API_URL || ''),
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
