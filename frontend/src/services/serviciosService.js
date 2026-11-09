/**
 * Servicio para el recurso /servicios (catálogo de servicios y precios).
 * Ver openapi_equipo.yaml, sección "Servicios".
 */

import { request } from './api.js'

/**
 * GET /servicios. Público por defecto (solo servicios activos). Con
 * `incluirInactivos: true` pide también los desactivados; esa variante
 * requiere sesión de administrador (el backend responde 401 sin token).
 */
function listar({ incluirInactivos = false } = {}) {
  return request('/servicios', {
    params: incluirInactivos ? { incluir_inactivos: 'true' } : undefined,
  })
}

/** GET /servicios/{id}. Público si el servicio está activo. */
function obtener(servicioId) {
  return request(`/servicios/${servicioId}`)
}

/** POST /servicios. Requiere sesión de administrador. */
function crear(datos) {
  return request('/servicios', { method: 'POST', body: datos })
}

/**
 * PATCH /servicios/{id}. Requiere sesión de administrador. Para desactivar
 * se envía `{ activo: false }`; no existe DELETE (baja lógica).
 */
function actualizar(servicioId, cambios) {
  return request(`/servicios/${servicioId}`, { method: 'PATCH', body: cambios })
}

export { listar, obtener, crear, actualizar }
