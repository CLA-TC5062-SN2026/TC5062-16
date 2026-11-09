import { useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import InputField from '../components/InputField.jsx'
import Navbar from '../components/Navbar.jsx'

function HomePage() {
  const [codigo, setCodigo] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const handleSubmit = (event) => {
    event.preventDefault()
    setMessage('')

    if (codigo.trim().length < 5) {
      setError('Ingresa un código de seguimiento válido.')
      return
    }

    setError('')
    setIsLoading(true)

    window.setTimeout(() => {
      setIsLoading(false)
      setMessage(
        `Consulta de demostración realizada para ${codigo.trim()}.`
      )
    }, 700)
  }

  const handleClear = () => {
    setCodigo('')
    setError('')
    setMessage('')
  }

  return (
    <>
      <a
        href="#contenido-principal"
        className="visually-hidden-focusable position-absolute top-0 start-0 m-2 btn btn-light"
      >
        Saltar al contenido principal
      </a>

      <Navbar
        isAuthenticated={isAuthenticated}
        userName="Diego"
        userRole="Administrador"
        onLogin={() => setIsAuthenticated(true)}
        onLogout={() => setIsAuthenticated(false)}
      />

      <main
        id="contenido-principal"
        className="container py-5"
        tabIndex="-1"
      >
        <div className="row justify-content-center">
          <div className="col-12 col-md-10 col-lg-7">
            <header className="mb-4">
              <h1 className="display-6 fw-semibold">
                LaundryDesk
              </h1>

              <p className="lead text-body-secondary">
                Consulta el estado de tu pedido de lavandería.
              </p>
            </header>

            <Card
              title="Seguimiento de pedido"
              footer={
                <small className="text-body-secondary">
                  Pantalla demostrativa de los componentes de LaundryDesk.
                </small>
              }
            >
              <form onSubmit={handleSubmit} noValidate>
                <InputField
                  id="codigo-seguimiento"
                  name="codigoSeguimiento"
                  type="text"
                  label="Código de seguimiento"
                  value={codigo}
                  onChange={(event) => setCodigo(event.target.value)}
                  placeholder="Ej. LD-2026-001"
                  helperText="Introduce el código asociado a tu pedido."
                  error={error}
                  required
                />

                <div className="d-flex flex-column flex-sm-row gap-2">
                  <Button
                    type="submit"
                    variant="primary"
                    isLoading={isLoading}
                    loadingText="Consultando..."
                  >
                    Consultar pedido
                  </Button>

                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleClear}
                    disabled={isLoading}
                  >
                    Limpiar
                  </Button>
                </div>

                {message && (
                  <div
                    className="alert alert-success mt-3 mb-0"
                    role="status"
                  >
                    {message}
                  </div>
                )}
              </form>
            </Card>

            <div className="mt-4">
              <Card title="Componentes implementados">
                <p className="mb-2">
                  Esta pantalla utiliza los cuatro componentes esenciales:
                </p>

                <ul className="mb-0">
                  <li>Button</li>
                  <li>InputField</li>
                  <li>Card</li>
                  <li>Navbar</li>
                </ul>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

export default HomePage