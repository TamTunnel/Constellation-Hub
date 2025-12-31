import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import cesium from 'vite-plugin-cesium';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react(), cesium()],
    server: {
        port: 3000,
        proxy: {
            '/api/orbits': {
                target: 'http://localhost:8001',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/orbits/, ''),
            },
            '/api/routing': {
                target: 'http://localhost:8002',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/routing/, ''),
            },
            '/api/scheduler': {
                target: 'http://localhost:8003',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/scheduler/, ''),
            },
            '/api/ai': {
                target: 'http://localhost:8004',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api\/ai/, ''),
            },
        },
    },
    build: {
        chunkSizeWarningLimit: 3000, // CesiumJS is large
    },
    define: {
        CESIUM_BASE_URL: JSON.stringify('/cesium'),
    },
});
