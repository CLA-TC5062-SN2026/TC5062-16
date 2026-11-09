/**
 * Servicio de autenticación. Encapsula /auth/register, /auth/login y
 * /auth/me (openapi_equipo.yaml) y el manejo del JWT guardado en el
 * navegador (ver api.js para dónde y por qué).
 */

import { request, setToken, clearToken, getToken } from './api.js'

/**
 * POST /auth/login (público). Si las credenciales son válidas guarda el
 * JWT recibido y lo devuelve junto con su vigencia en segundos.
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ access: string, tipo: string, expiraEn: number }>}
 * @throws {import('./api.js').ApiError} codigo CREDENCIALES_INVALIDAS (401)
 *   si el correo o la contraseña son incorrectos.
 */
async function login(email, password) {
  const datos = await request('/auth/login', {
    method: 'POST',
    body: { email, password },
  })

  setToken(datos.access)

  return {
    access: datos.access,
    tipo: datos.tipo,
    expiraEn: datos.expira_en,
  }
}

/**
 * POST /auth/register (público). Registra la única cuenta administrativa
 * del MVP. Esta entrega no incluye una pantalla de registro ("Se eliminó
 * la página de registro...", instrucciones S07-S08-A1), pero el método se
 * expone aquí porque la capa de servicios cubre todo el contrato, no solo
 * las pantallas construidas hasta ahora.
 *
 * @param {{ usuario: string, email: string, password: string }} datos
 * @throws {import('./api.js').ApiError} codigo ADMINISTRADOR_YA_REGISTRADO (409)
 *   si ya existe la cuenta administrativa.
 */
function registrar({ usuario, email, password }) {
  return request('/auth/register', {
    method: 'POST',
    body: { usuario, email, password },
  })
}

/**
 * GET /auth/me (requiere JWT). Datos del administrador autenticado. Útil
 * para que una ruta protegida confirme que el token guardado sigue siendo
 * válido antes de mostrar contenido administrativo.
 */
function obtenerPerfil() {
  return request('/auth/me')
}

/** Termina la sesión local (no hay endpoint de logout en el backend: el
 * JWT simplemente deja de enviarse). */
function cerrarSesion() {
  clearToken()
}

/** true si hay un token guardado. No garantiza que siga siendo válido en
 * el backend (puede haber expirado); eso solo se sabe al hacer una llamada
 * y recibir 401. */
function haySesionActiva() {
  return Boolean(getToken())
}

export { login, registrar, obtenerPerfil, cerrarSesion, haySesionActiva }
