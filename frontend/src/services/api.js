/**
 * Cliente HTTP base de LaundryDesk.
 *
 * Fetch API (decisión del equipo en decision_stack_frontend_FINAL.md) no
 * tiene interceptores nativos como Axios. La función `request()` de este
 * archivo cumple ese rol para TODA la aplicación:
 *
 *   - arma la URL completa a partir de VITE_API_URL;
 *   - agrega el header `Authorization: Bearer <token>` cuando hay una
 *     sesión guardada (ningún módulo de servicios ni componente debe
 *     construir ese header a mano);
 *   - traduce cualquier error (de red o de respuesta del backend) a un
 *     único tipo, `ApiError`, con la forma que define openapi_equipo.yaml:
 *     { codigo, mensaje, errores?: [{ campo, mensaje }] }.
 *
 * Ningún componente de la interfaz debe llamar a `fetch` directamente:
 * siempre a través de este módulo o de los servicios por recurso
 * (authService, serviciosService, horariosService, pedidosService,
 * seguimientosService) que lo usan.
 */

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')

if (!API_URL) {
  console.warn('VITE_API_URL no está definida. Revisa tu archivo .env.')
}

// ---------------------------------------------------------------------------
// Almacenamiento del token
//
// El JWT de LaundryDesk (ver backend/api/auth_utils.py) no tiene refresh
// token: es un único access token que expira a los JWT_EXPIRATION segundos
// (3600 por defecto, 1 hora). Esta entrega tampoco incluye una pantalla de
// logout ("Se eliminó la página de registro y el logout completo para
// reducir tiempo", instrucciones S07-S08-A1).
//
// Se eligió sessionStorage en vez de localStorage: la sesión no necesita
// sobrevivir más allá de la pestaña actual, así que cerrar la pestaña
// cumple el papel de "cerrar sesión", y el token no queda expuesto de forma
// indefinida en el navegador si llegara a haber un XSS. Ver capa_servicios.md
// para el detalle de esta decisión y sus riesgos.
// ---------------------------------------------------------------------------
const TOKEN_STORAGE_KEY = 'laundrydesk_token'

function getToken() {
  try {
    return window.sessionStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    // sessionStorage puede no estar disponible (navegación privada,
    // políticas del navegador, etc.). Sin token, el backend responderá 401
    // y la pantalla protegida redirigirá al login.
    return null
  }
}

function setToken(token) {
  try {
    window.sessionStorage.setItem(TOKEN_STORAGE_KEY, token)
  } catch {
    console.warn('No se pudo guardar el token de sesión en este navegador.')
  }
}

function clearToken() {
  try {
    window.sessionStorage.removeItem(TOKEN_STORAGE_KEY)
  } catch {
    // Nada que limpiar si sessionStorage no está disponible.
  }
}

// ---------------------------------------------------------------------------
// Error centralizado
// ---------------------------------------------------------------------------

/**
 * Único tipo de error de toda la capa de servicios. Replica el contrato de
 * openapi_equipo.yaml y agrega dos datos útiles para la interfaz:
 *   - `status`: código HTTP devuelto por el backend (null si nunca respondió).
 *   - `esErrorDeRed`: true cuando no se pudo contactar al backend en
 *     absoluto (sin internet, CORS, backend caído, timeout).
 */
class ApiError extends Error {
  constructor({
    mensaje,
    codigo = 'ERROR_DESCONOCIDO',
    errores = [],
    status = null,
    esErrorDeRed = false,
  }) {
    super(mensaje)
    this.name = 'ApiError'
    // `message` lo hereda de Error (útil para console.error/stack traces).
    // `mensaje` es el mismo texto, con el nombre que usa el contrato y el
    // que deben leer las pantallas (ver capa_servicios.md).
    this.mensaje = mensaje
    this.codigo = codigo
    this.errores = errores
    this.status = status
    this.esErrorDeRed = esErrorDeRed
  }
}

function mensajeDeRed(error) {
  if (error?.name === 'AbortError') {
    return 'La solicitud tardó demasiado en responder. Intenta de nuevo.'
  }
  return 'No se pudo conectar con el servidor. Revisa tu conexión a internet e intenta de nuevo.'
}

// ---------------------------------------------------------------------------
// Cliente
// ---------------------------------------------------------------------------

/**
 * @param {string} path - Ruta relativa al contrato, p. ej. '/servicios' o
 *   `/pedidos/${id}/estado`. Se concatena tal cual a VITE_API_URL.
 * @param {object} [opciones]
 * @param {string} [opciones.method='GET']
 * @param {object} [opciones.body] - Se serializa como JSON automáticamente.
 * @param {URLSearchParams|Record<string, string|number|undefined>} [opciones.params]
 *   Parámetros de query string. Las claves con valor undefined/null se omiten.
 * @param {number} [opciones.timeoutMs=15000]
 * @returns {Promise<any>} El cuerpo de la respuesta ya parseado (o null si
 *   la respuesta no trae cuerpo).
 * @throws {ApiError}
 */
async function request(path, { method = 'GET', body, params, timeoutMs = 15000 } = {}) {
  const url = new URL(`${API_URL}${path}`)

  if (params instanceof URLSearchParams) {
    params.forEach((value, key) => url.searchParams.append(key, value))
  } else if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, value)
      }
    })
  }

  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)

  let response
  try {
    response = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
  } catch (error) {
    console.error(`[capa de servicios] Falló la conexión con ${url.toString()}:`, error)
    throw new ApiError({
      mensaje: mensajeDeRed(error),
      codigo: 'ERROR_RED',
      esErrorDeRed: true,
    })
  } finally {
    window.clearTimeout(timeoutId)
  }

  const texto = await response.text()
  let datos = null
  if (texto) {
    try {
      datos = JSON.parse(texto)
    } catch (error) {
      console.error(`[capa de servicios] Respuesta no interpretable de ${url.toString()}:`, error)
      throw new ApiError({
        mensaje: 'El servidor respondió con un formato inesperado.',
        codigo: 'RESPUESTA_INVALIDA',
        status: response.status,
      })
    }
  }

  if (!response.ok) {
    if (response.status === 401) {
      // Token ausente, inválido o expirado: se limpia para que la próxima
      // pantalla protegida redirija al login en vez de reintentar con un
      // token que el backend ya rechazó.
      clearToken()
    }

    if (response.status >= 500) {
      console.error(`[capa de servicios] ${response.status} de ${url.toString()}:`, datos)
    }

    throw new ApiError({
      mensaje: datos?.mensaje || 'Ocurrió un problema. Intenta de nuevo en unos minutos.',
      codigo: datos?.codigo || 'ERROR_DESCONOCIDO',
      errores: datos?.errores || [],
      status: response.status,
    })
  }

  return datos
}

export { request, ApiError, API_URL, getToken, setToken, clearToken }
