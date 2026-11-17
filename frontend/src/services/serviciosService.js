/**
 * Servicio para el recurso /servicios.
 *
 * Las operaciones CRUD comunes se reutilizan desde recursoService.
 * El listado se mantiene aquí porque /servicios tiene el comportamiento
 * particular incluir_inactivos.
 */

import { crearRecurso } from './recursoService.js'

const servicios = crearRecurso('/servicios')

function listar({ incluirInactivos = false } = {}) {
  return servicios.listar(
    incluirInactivos
      ? { incluir_inactivos: 'true' }
      : undefined
  )
}

const {
  obtener,
  crear,
  actualizar,
} = servicios

export {
  listar,
  obtener,
  crear,
  actualizar,
}
