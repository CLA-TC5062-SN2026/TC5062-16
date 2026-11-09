import { useRef, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import InputField from '../components/InputField.jsx'
import Navbar from '../components/Navbar.jsx'
import { useAuth } from '../context/AuthContext.jsx'

const CAMPOS = ['email', 'password']

function rutaDestino(from) {
  if (!from?.pathname || from.pathname === '/login') return '/dashboard'
  return `${from.pathname}${from.search || ''}${from.hash || ''}`
}

function LoginPage() {
  const { estaAutenticado, cargando, iniciarSesion } = useAuth()
  const location = useLocation()
  const emailRef = useRef(null)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [erroresCampo, setErroresCampo] = useState({})
  const [alerta, setAlerta] = useState(null)
  const [enviando, setEnviando] = useState(false)

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

  // Cubre tanto al usuario que ya tenía sesión como al que acaba de
  // autenticarse: iniciarSesion() actualiza el contexto y este render redirige.
  if (estaAutenticado) {
    return <Navigate to={rutaDestino(location.state?.from)} replace />
  }

  const limpiarErrorCampo = (campo) => {
    setErroresCampo((actuales) => ({ ...actuales, [campo]: '' }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setAlerta(null)

    const erroresLocales = {}
    if (!email.trim()) erroresLocales.email = 'Ingresa tu correo electrónico.'
    if (!password) erroresLocales.password = 'Ingresa tu contraseña.'
    setErroresCampo(erroresLocales)
    if (Object.keys(erroresLocales).length > 0) return

    setEnviando(true)
    try {
      await iniciarSesion(email.trim(), password)
    } catch (error) {
      setEnviando(false)

      if (error?.esErrorDeRed) {
        setAlerta({ tipo: 'warning', titulo: 'No pudimos conectar con el servidor', mensaje: error.mensaje, extras: [] })
        return
      }

      const porCampo = {}
      const extras = []
      for (const { campo, mensaje } of error?.errores || []) {
        if (CAMPOS.includes(campo)) {
          porCampo[campo] = mensaje
        } else {
          extras.push(mensaje)
        }
      }
      setErroresCampo(porCampo)
      setAlerta({
        tipo: 'danger',
        titulo: null,
        mensaje: error?.mensaje || 'Ocurrió un problema. Intenta de nuevo.',
        extras,
      })
    }
  }

  return (
    <>
      <a
        href="#contenido-principal"
        className="visually-hidden-focusable position-absolute top-0 start-0 m-2 btn btn-light"
      >
        Saltar al contenido principal
      </a>

      <Navbar isAuthenticated={false} onLogin={() => emailRef.current?.focus()} />

      <main id="contenido-principal" className="container py-5" tabIndex="-1">
        <div className="row justify-content-center">
          <div className="col-12 col-sm-10 col-md-7 col-lg-5">
            <h1 className="h3 fw-semibold mb-4 text-center">Acceso administrativo</h1>

            <Card>
              {alerta && (
                <div className={`alert alert-${alerta.tipo}`} role="alert">
                  {alerta.titulo && <p className="fw-semibold mb-1">{alerta.titulo}</p>}
                  <p className="mb-0">{alerta.mensaje}</p>
                  {alerta.tipo === 'warning' && (
                    <p className="mb-0 small mt-1">
                      No es un problema con tus datos; inténtalo de nuevo en unos momentos.
                    </p>
                  )}
                  {alerta.extras.length > 0 && (
                    <ul className="mb-0 mt-2">
                      {alerta.extras.map((mensaje) => (
                        <li key={mensaje}>{mensaje}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <form onSubmit={handleSubmit} noValidate>
                <InputField
                  ref={emailRef}
                  id="login-email"
                  name="email"
                  type="email"
                  label="Correo electrónico"
                  autoComplete="username"
                  value={email}
                  onChange={(event) => {
                    setEmail(event.target.value)
                    limpiarErrorCampo('email')
                  }}
                  error={erroresCampo.email}
                  disabled={enviando}
                  required
                />

                <InputField
                  id="login-password"
                  name="password"
                  type="password"
                  label="Contraseña"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => {
                    setPassword(event.target.value)
                    limpiarErrorCampo('password')
                  }}
                  error={erroresCampo.password}
                  disabled={enviando}
                  required
                />

                <Button
                  type="submit"
                  className="w-100"
                  isLoading={enviando}
                  loadingText="Iniciando sesión..."
                >
                  Iniciar sesión
                </Button>
              </form>
            </Card>
          </div>
        </div>
      </main>
    </>
  )
}

export default LoginPage
