import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // Permet d'écouter sur le réseau Docker
    allowedHosts: ['web', 'localhost'] // Autorise Nginx ("web") et ton PC ("localhost")
  }
})