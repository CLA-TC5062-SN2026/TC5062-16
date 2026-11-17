/**
 * Servicio para el recurso /horarios.
 */

import { crearRecurso } from './recursoService.js'

const horarios = crearRecurso('/horarios')

const {
  listar,
  obtener,
  crear,
  actualizar,
} = horarios

export {
  listar,
  obtener,
  crear,
  actualizar,
}
