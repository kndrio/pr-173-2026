import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell',
      remotes: {
        // In Docker, orders-mfe is accessible at localhost:3001
        ordersApp: 'http://localhost:3001/assets/remoteEntry.js',
      },
      shared: {
        react: { singleton: true, requiredVersion: '^18.3.0' },
        'react-dom': { singleton: true, requiredVersion: '^18.3.0' },
        'react-router-dom': { singleton: true, requiredVersion: '^6.26.0' },
      },
    }),
  ],
  build: {
    // Required for Module Federation: top-level await support
    target: 'esnext',
  },
  server: {
    port: 3000,
    proxy: {
      '/api/auth': {
        target: 'http://localhost:8001',
        rewrite: (path) => path.replace(/^\/api\/auth/, '/api/v1/auth'),
        changeOrigin: true,
      },
      '/api/users': {
        target: 'http://localhost:8001',
        rewrite: (path) => path.replace(/^\/api\/users/, '/api/v1/users'),
        changeOrigin: true,
      },
      '/api/orders': {
        target: 'http://localhost:8002',
        rewrite: (path) => path.replace(/^\/api\/orders/, ''),
        changeOrigin: true,
      },
    },
  },
})
