/**
 * Servicio para el recurso /horarios (horario de atención por día de la
 * semana). Ver openapi_equipo.yaml, sección "Horarios".
 */

import { request } from './api.js'

/** GET /horarios. Público. Un registro por día configurado. */
function listar() {
  return request('/horarios')
}

/** GET /horarios/{id}. Público. */
function obtener(horarioId) {
  return request(`/horarios/${horarioId}`)
}

/** POST /horarios. Requiere sesión de administrador. */
function crear(datos) {
  return request('/horarios', { method: 'POST', body: datos })
}

/** PATCH /horarios/{id}. Requiere sesión de administrador. */
function actualizar(horarioId, cambios) {
  return request(`/horarios/${horarioId}`, { method: 'PATCH', body: cambios })
}

export { listar, obtener, crear, actualizar }
