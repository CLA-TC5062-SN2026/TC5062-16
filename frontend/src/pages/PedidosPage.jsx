import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import * as pedidosService from '../services/pedidosService.js'

// El texto acompaña siempre al color: el estado no se comunica solo con color
// (accesibilidad.md). text-bg-* elige un color de texto con contraste suficiente.
const ESTADOS = {
  RECIBIDO: { etiqueta: 'Recibido', clase: 'text-bg-secondary' },
  EN_PROCESO: { etiqueta: 'En proceso', clase: 'text-bg-info' },
  LISTO: { etiqueta: 'Listo', clase: 'text-bg-success' },
  ENTREGADO: { etiqueta: 'Entregado', clase: 'text-bg-primary' },
  CANCELADO: { etiqueta: 'Cancelado', clase: 'text-bg-danger' },
}

const formatoFecha = new Intl.DateTimeFormat('es-MX', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

function formatearFecha(iso) {
  const fecha = new Date(iso)
  return Number.isNaN(fecha.getTime()) ? iso : formatoFecha.format(fecha)
}

function EstadoBadge({ estado }) {
  const { etiqueta, clase } = ESTADOS[estado] || { etiqueta: estado, clase: 'text-bg-light' }
  return <span className={`badge ${clase}`}>{etiqueta}</span>
}

function PedidosPage() {
  const { cerrarSesion } = useAuth()
  const navigate = useNavigate()

  // Un solo objeto de estado garantiza que cargando / error / vacío / datos
  // sean mutuamente excluyentes.
  const [vista, setVista] = useState({ tipo: 'cargando' })

  // Identifica la solicitud vigente para descartar respuestas viejas (doble
  // montaje de StrictMode, recargas rápidas o la página ya desmontada).
  const solicitudActual = useRef(0)

  const cargar = async () => {
    const id = ++solicitudActual.current
    setVista({ tipo: 'cargando' })

    try {
      const datos = await pedidosService.listar()
      if (id !== solicitudActual.current) return

      const resultados = datos?.resultados || []
      setVista(
        resultados.length === 0
          ? { tipo: 'vacio' }
          : { tipo: 'datos', resultados, total: datos.total ?? resultados.length },
      )
    } catch (error) {
      if (id !== solicitudActual.current) return

      // Token expirado: api.js ya lo borró, falta que el contexto se entere.
      if (error?.status === 401) {
        cerrarSesion()
        navigate('/login', { replace: true, state: { from: { pathname: '/pedidos' } } })
        return
      }

      setVista({ tipo: 'error', error })
    }
  }

  useEffect(() => {
    cargar()
    return () => {
      solicitudActual.current += 1
    }
    // Solo al montar; las recargas posteriores las dispara el usuario.
  }, [])

  const cargando = vista.tipo === 'cargando'

  return (
    <>
      <div className="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2 mb-4">
        <h1 className="h3 fw-semibold mb-0">Pedidos</h1>

        {vista.tipo !== 'error' && (
          <Button
            variant="secondary"
            onClick={cargar}
            isLoading={cargando}
            loadingText="Cargando..."
          >
            Recargar
          </Button>
        )}
      </div>

      <Card>
        {vista.tipo === 'cargando' && (
          <div
            className="d-flex flex-column align-items-center justify-content-center text-center py-5"
            role="status"
          >
            <span
              className="spinner-border text-primary mb-3"
              style={{ width: '3rem', height: '3rem' }}
              aria-hidden="true"
            />
            <p className="fs-5 mb-0">Cargando pedidos...</p>
          </div>
        )}

        {vista.tipo === 'error' && (
          <div
            className={`alert ${vista.error?.esErrorDeRed ? 'alert-warning' : 'alert-danger'} mb-0`}
            role="alert"
          >
            {vista.error?.esErrorDeRed && (
              <p className="fw-semibold mb-1">No pudimos conectar con el servidor</p>
            )}
            <p className="mb-3">
              {vista.error?.mensaje || 'Ocurrió un problema al cargar los pedidos.'}
            </p>
            <Button onClick={cargar}>Reintentar</Button>
          </div>
        )}

        {vista.tipo === 'vacio' && (
          <div className="text-center py-5">
            <p className="fs-5 mb-1">Todavía no hay pedidos registrados.</p>
            <p className="text-body-secondary mb-0">
              Cuando se registre un pedido aparecerá en esta lista.
            </p>
          </div>
        )}

        {vista.tipo === 'datos' && (
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <caption className="caption-top">
                Mostrando {vista.resultados.length} de {vista.total} pedidos, del más reciente al
                más antiguo.
              </caption>
              <thead>
                <tr>
                  <th scope="col">Código de seguimiento</th>
                  <th scope="col">Cliente</th>
                  <th scope="col">Estado</th>
                  <th scope="col">Fecha de recepción</th>
                </tr>
              </thead>
              <tbody>
                {vista.resultados.map((pedido) => (
                  <tr key={pedido.id}>
                    <td className="font-monospace">{pedido.codigo_seguimiento}</td>
                    <td>{pedido.nombre_cliente}</td>
                    <td>
                      <EstadoBadge estado={pedido.estado_actual} />
                    </td>
                    <td>
                      <time dateTime={pedido.fecha_recepcion}>
                        {formatearFecha(pedido.fecha_recepcion)}
                      </time>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  )
}

export default PedidosPage
