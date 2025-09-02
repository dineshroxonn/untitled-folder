import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/agent-status': 'http://localhost:8000',
      '/connection-info': 'http://localhost:8000',
      '/connect-obd': 'http://localhost:8000',
      '/disconnect-obd': 'http://localhost:8000',
      '/diagnose': 'http://localhost:8000',
    },
  },
})
