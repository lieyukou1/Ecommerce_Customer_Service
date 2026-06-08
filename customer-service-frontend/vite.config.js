import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_TARGET || env.VITE_BACKEND_TARGET || 'http://127.0.0.1:18082'
  const commerceTarget = env.VITE_COMMERCE_TARGET || env.VITE_BACKEND_TARGET || 'http://192.168.200.145:18081'

  return {
    plugins: [vue()],
    server: {
      host: '127.0.0.1',
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
        '/commerce': {
          target: commerceTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/commerce/, ''),
        },
        '/health': {
          target: commerceTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
