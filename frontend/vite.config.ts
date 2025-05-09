// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA, VitePWAOptions } from 'vite-plugin-pwa'

const manifestForPlugin: Partial<VitePWAOptions> = {
  registerType: 'autoUpdate',
  includeAssets: ['favicon.ico', 'icons/app-icon-192.png', 'icons/app-icon-512.png'], // Paths relative to public folder
  manifest: {
    name: 'TÜFE CPI Tahmin',
    short_name: 'TÜFE Tahmin',
    description: 'Aylık TÜFE CPI verileri için tahmin uygulaması.',
    theme_color: '#ffffff',
    background_color: '#ffffff',
    display: 'standalone',
    scope: '/',
    start_url: '/',
    icons: [
      {
        src: 'icons/app-icon-192.png', // Path relative to public folder
        sizes: '192x192',
        type: 'image/png'
      },
      {
        src: 'icons/app-icon-512.png', // Path relative to public folder
        sizes: '512x512',
        type: 'image/png'
      },
      // Optional: Add a maskable icon if you have one
      // { 
      //   src: 'icons/app-icon-512-maskable.png', 
      //   sizes: '512x512',
      //   type: 'image/png',
      //   purpose: 'maskable'
      // }
    ]
  }
};

export default defineConfig({
  plugins: [
    react(),
    VitePWA(manifestForPlugin)
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5001', // Your backend port
        changeOrigin: true,
        secure: false,
      }
    }
  }
})