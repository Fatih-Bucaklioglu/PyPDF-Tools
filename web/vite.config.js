import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
  ],
  
  // Build configuration for PyQt6 WebEngine integration
  build: {
    // Output directory - will be copied to src/pypdf_tools/web/build/
    outDir: 'build',
    
    // Generate relative paths for PyQt6 WebEngine
    base: './',
    
    // Assets directory
    assetsDir: 'static',
    
    // Generate manifest for asset management
    manifest: true,
    
    // Rollup options
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      },
      output: {
        // Static asset naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          
          if (/\.(css)$/.test(assetInfo.name)) {
            return `static/css/[name].[hash].${ext}`;
          }
          
          if (/\.(png|jpe?g|gif|svg|ico|webp)$/.test(assetInfo.name)) {
            return `static/images/[name].[hash].${ext}`;
          }
          
          if (/\.(woff2?|ttf|otf|eot)$/.test(assetInfo.name)) {
            return `static/fonts/[name].[hash].${ext}`;
          }
          
          return `static/[name].[hash].${ext}`;
        },
        
        // JavaScript chunk naming
        chunkFileNames: 'static/js/[name].[hash].js',
        entryFileNames: 'static/js/[name].[hash].js',
      }
    },
    
    // Optimization
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    
    // Source maps for debugging
    sourcemap: process.env.NODE_ENV === 'development',
    
    // Target modern browsers (PyQt6 WebEngine uses Chromium)
    target: 'es2018',
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
  },
  
  // Development server
  server: {
    host: 'localhost',
    port: 5173,
    strictPort: false,
    open: false, // Don't auto-open browser in development
    
    // CORS configuration for PyQt6 WebEngine
    cors: {
      origin: true,
      credentials: true,
    },
    
    // Headers for PyQt6 WebEngine compatibility
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization',
    }
  },
  
  // Preview server (for production testing)
  preview: {
    host: 'localhost',
    port: 4173,
    strictPort: false,
    open: false,
    cors: true,
  },
  
  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@components': resolve(__dirname, './src/components'),
      '@utils': resolve(__dirname, './src/utils'),
      '@assets': resolve(__dirname, './src/assets'),
    }
  },
  
  // CSS configuration
  css: {
    devSourcemap: true,
    modules: {
      localsConvention: 'camelCase',
    },
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ]
    }
  },
  
  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '2.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __IS_PYQT__: 'typeof qt !== "undefined"',
  },
  
  // Environment variables
  envPrefix: ['VITE_', 'PYPDF_'],
  
  // Optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'lucide-react',
      'pdfjs-dist'
    ],
    exclude: [
      // Exclude PDF.js worker from optimization (loaded from CDN)
      'pdfjs-dist/build/pdf.worker.js'
    ]
  },
  
  // Worker configuration
  worker: {
    format: 'es'
  },
  
  // Experimental features
  experimental: {
    renderBuiltUrl(filename, { hostType }) {
      // Handle different host types for PyQt6 integration
      if (hostType === 'js') {
        return { js: `"./${filename}"` };
      }
      return { relative: true };
    }
  },
  
  // Plugin-specific configurations
  esbuild: {
    // JSX configuration
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment',
    
    // Remove console logs in production
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  }
})
