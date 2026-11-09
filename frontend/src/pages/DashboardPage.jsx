import { Link } from 'react-router-dom'
import Card from '../components/Card.jsx'
import { useAuth } from '../context/AuthContext.jsx'

function DashboardPage() {
  const { administrador } = useAuth()

  return (
    <div className="row justify-content-center">
      <div className="col-12 col-md-10 col-lg-7">
        <header className="mb-4">
          <h1 className="display-6 fw-semibold">Hola, {administrador.usuario}</h1>
          <p className="lead text-body-secondary mb-0">
            Sesión iniciada como {administrador.email}.
          </p>
        </header>

        <Card title="Accesos rápidos">
          <p>Consulta y administra los pedidos de la lavandería.</p>
          <Link to="/pedidos" className="btn btn-primary">
            Ir a pedidos
          </Link>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage
