import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',   // necesario para Docker
    port: 5173,
    proxy: {
      // Redirige /api/... al backend (usa el nombre del servicio en Docker)
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      }
    }
  }
})
