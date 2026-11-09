// Ejecuta verify-dist/verify-bundle.js con un window/sessionStorage/fetch
// simulados (Node no tiene `window`). No se conecta a ningún servidor real.

const store = new Map()
globalThis.window = {
  sessionStorage: {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, v),
    removeItem: (k) => store.delete(k),
  },
  setTimeout: (...args) => setTimeout(...args),
  clearTimeout: (...args) => clearTimeout(...args),
}
globalThis.__VITE_API_URL_ESPERADA__ = 'http://fake-backend.test/api/v1'

await import('./verify-dist/verify-bundle.js')

process.exit(globalThis.__VERIFY_EXIT_CODE__ ?? 1)
