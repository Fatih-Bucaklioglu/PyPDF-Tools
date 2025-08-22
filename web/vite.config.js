import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Build configuration
  build: {
    outDir: 'build',
    assetsDir: 'static',
    sourcemap: process.env.NODE_ENV === 'development',
    minify: process.env.NODE_ENV === 'production' ? 'terser' : false,
    
    // Rollup options
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk
          vendor: ['react', 'react-dom'],
          // Lucide icons chunk  
          icons: ['lucide-react']
        },
        // Asset naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
            return `static/media/[name]-[hash][extname]`
          }
          if (/\.(css)$/i.test(assetInfo.name)) {
            return `static/css/[name]-[hash][extname]`
          }
          return `static/${ext}/[name]-[hash][extname]`
        },
        chunkFileNames: 'static/js/[name]-[hash].js',
        entryFileNames: 'static/js/[name]-[hash].js'
      }
    },
    
    // Optimization
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  
  // Development server
  server: {
    port: 3000,
    open: false, // PyQt6 will handle opening
    host: 'localhost',
    cors: true,
    hmr: {
      port: 3001,
    }
  },
  
  // Preview server
  preview: {
    port: 4173,
    open: false
  },
  
  // Path resolution
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@assets': path.resolve(__dirname, './src/assets')
    }
  },
  
  // CSS configuration
  css: {
    postcss: './postcss.config.js',
    devSourcemap: true
  },
  
  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __DEV__: process.env.NODE_ENV === 'development',
  },
  
  // Testing configuration (Vitest)
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.js'],
    css: true,
    coverage: {
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/setupTests.js',
        '**/*.test.{js,jsx}',
        '**/__tests__/**'
      ]
    }
  },
  
  // Optimized dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'lucide-react'
    ],
    exclude: []
  },
  
  // Build target
  esbuild: {
    target: 'es2015'
  },
  
  // Base path for deployment
  base: './',
  
  // Public directory
  publicDir: 'public'
})
