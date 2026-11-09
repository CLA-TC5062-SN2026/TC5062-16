/**
 * Servicio para el recurso público /seguimientos/{codigo} (consulta de
 * estado de un pedido sin cuenta ni token). Ver openapi_equipo.yaml,
 * sección "Seguimiento".
 */

import { request } from './api.js'

/**
 * GET /seguimientos/{codigo_seguimiento}. Público. Devuelve solo código,
 * estado y fechas (nunca datos personales ni notas).
 *
 * @param {string} codigoSeguimiento
 * @throws {import('./api.js').ApiError} codigo NO_ENCONTRADO (404) si el
 *   código no corresponde a ningún pedido.
 */
function consultar(codigoSeguimiento) {
  return request(`/seguimientos/${encodeURIComponent(codigoSeguimiento)}`)
}

export { consultar }
