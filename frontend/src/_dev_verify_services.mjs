// Script temporal de verificación de capa_servicios.md paso 2 (Parte 1).
// No forma parte de la entrega: se compila una vez con Vite para resolver
// import.meta.env.VITE_API_URL igual que en producción, y se ejecuta con
// fetch/window simulados (ver run-verify.mjs). No contacta ningún backend
// real.

import { request, ApiError, getToken, setToken, clearToken, API_URL } from './services/api.js'
import { login } from './services/authService.js'

const resultados = []

function check(nombre, condicion, detalle = '') {
  resultados.push({ nombre, ok: Boolean(condicion), detalle })
}

async function main() {
  // --- 1) La URL base se lee de VITE_API_URL, no está hardcodeada ---
  check(
    '1. API_URL viene de VITE_API_URL',
    API_URL === globalThis.__VITE_API_URL_ESPERADA__,
    `API_URL='${API_URL}'`,
  )

  // --- 2) Almacenamiento del token ---
  clearToken()
  check('2a. getToken() es null sin sesión', getToken() === null)

  setToken('token-de-prueba.abc.def')
  const guardado = globalThis.window.sessionStorage.getItem('laundrydesk_token')
  check(
    '2b. setToken() guarda en sessionStorage',
    guardado === 'token-de-prueba.abc.def',
    `sessionStorage['laundrydesk_token']='${guardado}'`,
  )

  // Verifica que request() efectivamente envía el header Authorization.
  let headerEnviado = null
  globalThis.fetch = async (_url, opts) => {
    headerEnviado = opts.headers.Authorization
    return new Response(JSON.stringify({ ok: true }), { status: 200 })
  }
  await request('/horarios')
  check(
    '2c. request() agrega Authorization: Bearer <token>',
    headerEnviado === 'Bearer token-de-prueba.abc.def',
    `Authorization='${headerEnviado}'`,
  )

  // --- 3) Errores de red con mensaje útil (no solo técnico en consola) ---
  globalThis.fetch = async () => {
    throw new TypeError('fetch failed') // lo que lanza fetch real sin conexión/por CORS
  }
  let errorDeRed = null
  try {
    await login('admin@laundrydesk.test', 'cualquier-cosa')
  } catch (error) {
    errorDeRed = error
  }
  check(
    '3a. Un fallo de red lanza ApiError (no la excepción cruda)',
    errorDeRed instanceof ApiError,
  )
  check(
    '3b. ApiError.codigo === ERROR_RED y esErrorDeRed === true',
    errorDeRed?.codigo === 'ERROR_RED' && errorDeRed?.esErrorDeRed === true,
  )
  check(
    '3c. El mensaje es apto para mostrar al usuario (texto en español, no "TypeError: fetch failed")',
    typeof errorDeRed?.mensaje === 'string' &&
      errorDeRed.mensaje.length > 0 &&
      !errorDeRed.mensaje.includes('TypeError'),
    `mensaje='${errorDeRed?.mensaje}'`,
  )

  // --- Bonus: 401 del backend limpia el token guardado ---
  setToken('token-que-sera-rechazado')
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({ codigo: 'NO_AUTENTICADO', mensaje: 'Inicia sesión para continuar.' }),
      { status: 401 },
    )
  let error401 = null
  try {
    await request('/auth/me')
  } catch (error) {
    error401 = error
  }
  check(
    'Bonus. Un 401 del backend se traduce a ApiError con el código del contrato',
    error401 instanceof ApiError && error401.codigo === 'NO_AUTENTICADO' && error401.status === 401,
  )
  check(
    'Bonus. Un 401 limpia el token guardado automáticamente',
    getToken() === null,
  )

  // --- Bonus: login exitoso guarda el token real que manda el backend ---
  clearToken()
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({ access: 'jwt-real-del-backend', tipo: 'Bearer', expira_en: 3600 }),
      { status: 200 },
    )
  const sesion = await login('admin@laundrydesk.test', 'correcta')
  check(
    'Bonus. Un login 200 guarda el access token y devuelve expiraEn',
    getToken() === 'jwt-real-del-backend' && sesion.expiraEn === 3600,
  )

  // --- Reporte ---
  console.log('\n=== Verificación capa de servicios (Parte 1, paso 2) ===\n')
  let fallos = 0
  for (const r of resultados) {
    console.log(`${r.ok ? '✅' : '❌'} ${r.nombre}${r.detalle ? ` — ${r.detalle}` : ''}`)
    if (!r.ok) fallos += 1
  }
  console.log(`\n${resultados.length - fallos}/${resultados.length} checks en verde.`)
  if (fallos > 0) {
    globalThis.__VERIFY_EXIT_CODE__ = 1
  } else {
    globalThis.__VERIFY_EXIT_CODE__ = 0
  }
}

await main()
