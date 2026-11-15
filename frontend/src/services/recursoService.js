/**
 * Fábrica para operaciones CRUD comunes de recursos REST.
 *
 * Centraliza las operaciones repetidas de:
 * - listar
 * - obtener por id
 * - crear
 * - actualizar parcialmente
 *
 * Los servicios concretos conservan aquí únicamente el comportamiento
 * específico de cada recurso.
 */

import { request } from './api.js'

function crearRecurso(ruta) {
  const rutaConId = (id) =>
    `${ruta}/${encodeURIComponent(id)}`

  return {
    listar: (params) =>
      request(ruta, { params }),

    obtener: (id) =>
      request(rutaConId(id)),

    crear: (datos) =>
      request(ruta, {
        method: 'POST',
        body: datos,
      }),

    actualizar: (id, cambios) =>
      request(rutaConId(id), {
        method: 'PATCH',
        body: cambios,
      }),
  }
}

export { crearRecurso }
