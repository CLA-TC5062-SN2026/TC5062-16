import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

function RutaProtegida({ children }) {
  const { estaAutenticado, cargando } = useAuth()
  const location = useLocation()

  if (cargando) {
    return (
      <div
        className="d-flex justify-content-center align-items-center py-5"
        role="status"
      >
        <span className="spinner-border text-primary me-2" aria-hidden="true" />
        <span>Verificando sesión...</span>
      </div>
    )
  }

  if (!estaAutenticado) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children
}

export default RutaProtegida
