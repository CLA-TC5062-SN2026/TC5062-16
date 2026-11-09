// Config temporal SOLO para compilar src/_dev_verify_services.mjs a un bundle
// ejecutable con Node. No se entrega ni se usa para el build real de la app.
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: 'verify-dist',
    emptyOutDir: true,
    minify: false,
    lib: {
      entry: 'src/_dev_verify_services.mjs',
      formats: ['es'],
      fileName: () => 'verify-bundle.js',
    },
  },
})
