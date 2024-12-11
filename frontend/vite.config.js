import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Redirect API calls starting with "/api" to the backend
      "/api": {
        target: "http://localhost:8000", // Your FastAPI server's URL
        changeOrigin: true,             // Update the origin of the host header
        rewrite: (path) => path.replace(/^\/api/, ""), // Remove "/api" prefix
      },
    },
  },
})
