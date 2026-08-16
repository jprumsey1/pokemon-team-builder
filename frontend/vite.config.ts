import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Proxying rather than CORS: the browser only ever talks to this origin, so the
  // session cookie behaves in dev exactly as it does behind FastAPI in production.
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
