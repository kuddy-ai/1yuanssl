import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

const proxyTarget = process.env.VITE_DEV_PROXY_TARGET || 'http://localhost:7000'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isTest = mode === 'test' || process.env.VITEST === 'true'

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 7001,
      host: isTest ? '127.0.0.1' : '0.0.0.0',
      hmr: isTest ? false : undefined,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
        '/.well-known': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
    test: {
      environment: 'jsdom',
      globals: false,
      setupFiles: './src/test/setup.ts',
    },
  }
})
