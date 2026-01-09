import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量（从 .env 文件或系统环境变量）
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          // 使用环境变量或默认localhost:8000
          // 如果前端在Docker中运行，可以在 .env 中设置 VITE_API_TARGET=http://backend:8000
          // 如果前端在本地运行，使用 http://localhost:8000（后端端口已映射到主机）
          // 注意：Vite 环境变量必须以 VITE_ 开头才能在客户端代码中使用
          // 但在 vite.config.js 中可以使用任何环境变量
          target: env.VITE_API_TARGET || process.env.VITE_API_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            antd: ['antd'],
            echarts: ['echarts', 'echarts-for-react']
          }
        }
      }
    }
  }
})
