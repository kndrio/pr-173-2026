import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'ordersApp',
      filename: 'remoteEntry.js',
      exposes: {
        './OrdersApp': './src/OrdersApp.tsx',
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
    minify: false,
  },
  server: {
    port: 3001,
    // Proxy for standalone dev mode
    proxy: {
      '/api/auth': {
        target: 'http://localhost:8001',
        rewrite: (path) => path.replace(/^\/api\/auth/, '/api/v1/auth'),
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
