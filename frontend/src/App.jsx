import { Outlet, Route, Routes, useNavigate } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import RutaProtegida from './components/RutaProtegida.jsx'
import { useAuth } from './context/AuthContext.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import HomePage from './pages/HomePage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import PedidosPage from './pages/PedidosPage.jsx'

// Estructura común de las pantallas administrativas: el Navbar se conecta
// aquí al contexto una sola vez en vez de repetirlo en cada página protegida.
function LayoutAdministrativo() {
  const { administrador, cerrarSesion } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    cerrarSesion()
    navigate('/login', { replace: true })
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
        isAuthenticated
        userName={administrador.usuario}
        onLogout={handleLogout}
      />

      <main id="contenido-principal" className="container py-5" tabIndex="-1">
        <Outlet />
      </main>
    </>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RutaProtegida>
            <LayoutAdministrativo />
          </RutaProtegida>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/pedidos" element={<PedidosPage />} />
      </Route>
    </Routes>
  )
}

export default App
