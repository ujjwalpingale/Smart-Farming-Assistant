import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy only POST requests to Django. Let React Router handle all GET requests.
      '^/(api|accounts|register|crop|fertilizer|disease|logout|management|chatbot)': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        bypass: function (req, res, proxyOptions) {
          if (req.method === 'GET') {
            return req.url; // Let Vite/React handle the GET request
          }
        }
      }
    },
  },
})
