import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/upload': 'http://localhost:8000',
      '/report': 'http://localhost:8000',
      '/demo': 'http://localhost:8000',
      '/analyze-stream': 'http://localhost:8000',
      '/analyze-stream-upload': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/ready': 'http://localhost:8000',
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    globals: true,
  },
})
