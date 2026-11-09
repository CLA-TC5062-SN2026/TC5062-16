/**
 * Servicio para el recurso /pedidos (registro, consulta, estado, historial
 * y notas). Ver openapi_equipo.yaml, sección "Pedidos". Requiere sesión de
 * administrador en todos sus métodos.
 */

import { request } from './api.js'

/**
 * GET /pedidos.
 *
 * OJO — divergencia entre el contrato y el backend ya implementado: esta
 * función sigue openapi_equipo.yaml (`estado_actual`, repetible;
 * `fecha_desde`/`fecha_hasta`; `pagina`/`tamano_pagina`), pero
 * backend/api/views.py:PedidoListCreateView hoy filtra con otros nombres
 * (`estado`, `codigo_seguimiento`, `telefono_cliente`) y no implementa
 * fecha_desde/fecha_hasta. La paginación (`pagina`, `tamano_pagina`,
 * respuesta {resultados, total, pagina, tamano_pagina}) sí coincide. Ver
 * capa_servicios.md, sección de riesgos, antes de construir la pantalla de
 * lista de pedidos.
 *
 * @param {object} [filtros]
 * @param {string|string[]} [filtros.estadoActual] - Uno o varios de
 *   RECIBIDO, EN_PROCESO, LISTO, ENTREGADO, CANCELADO.
 * @param {string} [filtros.fechaDesde] - 'YYYY-MM-DD'.
 * @param {string} [filtros.fechaHasta] - 'YYYY-MM-DD'.
 * @param {number} [filtros.pagina]
 * @param {number} [filtros.tamanoPagina]
 */
function listar({ estadoActual, fechaDesde, fechaHasta, pagina, tamanoPagina } = {}) {
  const params = new URLSearchParams()

  if (Array.isArray(estadoActual)) {
    estadoActual.forEach((estado) => params.append('estado_actual', estado))
  } else if (estadoActual) {
    params.append('estado_actual', estadoActual)
  }
  if (fechaDesde) params.append('fecha_desde', fechaDesde)
  if (fechaHasta) params.append('fecha_hasta', fechaHasta)
  if (pagina) params.append('pagina', String(pagina))
  if (tamanoPagina) params.append('tamano_pagina', String(tamanoPagina))

  return request('/pedidos', { params })
}

/** GET /pedidos/{id}. Detalle administrativo completo, con notas. */
function obtener(pedidoId) {
  return request(`/pedidos/${pedidoId}`)
}

/** POST /pedidos. Crea el pedido en RECIBIDO. */
function crear(datos) {
  return request('/pedidos', { method: 'POST', body: datos })
}

/**
 * PATCH /pedidos/{id}. Solo peso, precio_final e instrucciones_especiales.
 * Nunca cambia el estado (para eso está cambiarEstado).
 */
function actualizarDatos(pedidoId, cambios) {
  return request(`/pedidos/${pedidoId}`, { method: 'PATCH', body: cambios })
}

/**
 * PUT /pedidos/{id}/estado. Única operación que cambia el estado
 * (incluida la cancelación y la corrección manual).
 *
 * OJO — divergencia: el contrato documenta la respuesta como
 * `ResultadoCambioEstado` ({ pedido, cambio, aviso_correo }), pero
 * backend/api/views.py:PedidoEstadoView hoy devuelve directamente el
 * objeto `CambioEstado`. Confirmar contra el backend real antes de usar
 * esta respuesta en una pantalla (fuera del alcance de esta actividad).
 *
 * @param {string} pedidoId
 * @param {{ estado_nuevo: string, es_correccion?: boolean, confirmacion?: boolean, motivo?: string }} cambio
 */
function cambiarEstado(pedidoId, cambio) {
  return request(`/pedidos/${pedidoId}/estado`, { method: 'PUT', body: cambio })
}

/** GET /pedidos/{id}/cambios-estado. Historial en orden cronológico. */
function listarCambiosEstado(pedidoId) {
  return request(`/pedidos/${pedidoId}/cambios-estado`)
}

/** POST /pedidos/{id}/notas. No cambia el estado del pedido. */
function registrarNota(pedidoId, nota) {
  return request(`/pedidos/${pedidoId}/notas`, { method: 'POST', body: nota })
}

export {
  listar,
  obtener,
  crear,
  actualizarDatos,
  cambiarEstado,
  listarCambiosEstado,
  registrarNota,
}
