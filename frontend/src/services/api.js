/**
 * Cliente HTTP base de LaundryDesk.
 *
 * Centraliza:
 * - URL base desde VITE_API_URL.
 * - JWT en sessionStorage.
 * - Headers de autenticación.
 * - Timeout de solicitudes.
 * - Traducción de errores a ApiError.
 */

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')

if (!API_URL) {
  console.warn('VITE_API_URL no está definida. Revisa tu archivo .env.')
}

// ---------------------------------------------------------------------------
// Almacenamiento del token
// ---------------------------------------------------------------------------

const TOKEN_STORAGE_KEY = 'laundrydesk_token'

function getToken() {
  try {
    return window.sessionStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
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
    // Nada que limpiar.
  }
}

// ---------------------------------------------------------------------------
// Error centralizado
// ---------------------------------------------------------------------------

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
// Responsabilidades auxiliares del cliente HTTP
// ---------------------------------------------------------------------------

function construirUrl(path, params) {
  const url = new URL(`${API_URL}${path}`)

  const entradas =
    params instanceof URLSearchParams
      ? params.entries()
      : Object.entries(params ?? {})

  for (const [clave, valor] of entradas) {
    if (valor !== undefined && valor !== null && valor !== '') {
      url.searchParams.append(clave, valor)
    }
  }

  return url
}

function encabezados() {
  const token = getToken()

  const headers = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return headers
}

function errorDeRed(error, url) {
  console.error(
    `[capa de servicios] Falló la conexión con ${url.toString()}:`,
    error
  )

  return new ApiError({
    mensaje: mensajeDeRed(error),
    codigo: 'ERROR_RED',
    esErrorDeRed: true,
  })
}

function interpretarCuerpo(texto, url, status) {
  if (!texto) {
    return null
  }

  try {
    return JSON.parse(texto)
  } catch (error) {
    console.error(
      `[capa de servicios] Respuesta no interpretable de ${url.toString()}:`,
      error
    )

    throw new ApiError({
      mensaje: 'El servidor respondió con un formato inesperado.',
      codigo: 'RESPUESTA_INVALIDA',
      status,
    })
  }
}

function errorDeRespuesta(response, datos, url) {
  if (response.status === 401) {
    clearToken()
  }

  if (response.status >= 500) {
    console.error(
      `[capa de servicios] ${response.status} de ${url.toString()}:`,
      datos
    )
  }

  return new ApiError({
    mensaje:
      datos?.mensaje ||
      'Ocurrió un problema. Intenta de nuevo en unos minutos.',
    codigo: datos?.codigo || 'ERROR_DESCONOCIDO',
    errores: datos?.errores || [],
    status: response.status,
  })
}

// ---------------------------------------------------------------------------
// Cliente HTTP
// ---------------------------------------------------------------------------

async function request(
  path,
  {
    method = 'GET',
    body,
    params,
    timeoutMs = 15000,
  } = {}
) {
  let url

  try {
    url = construirUrl(path, params)
  } catch (error) {
    console.error(
      '[capa de servicios] VITE_API_URL no contiene una URL válida:',
      error
    )

    throw new ApiError({
      mensaje:
        'La dirección del servidor no está configurada correctamente. Revisa VITE_API_URL.',
      codigo: 'CONFIGURACION_INVALIDA',
    })
  }

  const controller = new AbortController()

  const timeoutId = window.setTimeout(
    () => controller.abort(),
    timeoutMs
  )

  let response
  let texto

  try {
    response = await fetch(url, {
      method,
      headers: encabezados(),
      body:
        body !== undefined
          ? JSON.stringify(body)
          : undefined,
      signal: controller.signal,
    })

    texto = await response.text()
  } catch (error) {
    throw errorDeRed(error, url)
  } finally {
    window.clearTimeout(timeoutId)
  }

  const datos = interpretarCuerpo(
    texto,
    url,
    response.status
  )

  if (!response.ok) {
    throw errorDeRespuesta(response, datos, url)
  }

  return datos
}

export {
  request,
  ApiError,
  API_URL,
  getToken,
  setToken,
  clearToken,
}