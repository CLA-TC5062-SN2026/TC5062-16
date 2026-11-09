import { useState } from 'react'

function Navbar({
  isAuthenticated = false,
  userName = 'Administrador',
  userRole = 'Administrador',
  onLogin = () => {},
  onLogout = () => {},
}) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <nav
      className="navbar navbar-expand-md navbar-dark bg-dark"
      aria-label="Navegación principal"
    >
      <div className="container">
        <a className="navbar-brand fw-semibold" href="/">
          LaundryDesk
        </a>

        <button
          type="button"
          className="navbar-toggler"
          aria-controls="navbarLaundryDesk"
          aria-expanded={menuOpen}
          aria-label="Mostrar u ocultar menú de navegación"
          onClick={() => setMenuOpen((current) => !current)}
        >
          <span className="navbar-toggler-icon" />
        </button>

        <div
          id="navbarLaundryDesk"
          className={`collapse navbar-collapse ${menuOpen ? 'show' : ''}`}
        >
          <div className="ms-auto d-flex flex-column flex-md-row align-items-md-center gap-2 mt-3 mt-md-0">
            {isAuthenticated ? (
              <>
                <span className="text-white small">
                  {userName} · {userRole}
                </span>

                <button
                  type="button"
                  className="btn btn-outline-light btn-sm"
                  onClick={onLogout}
                >
                  Cerrar sesión
                </button>
              </>
            ) : (
              <button
                type="button"
                className="btn btn-outline-light btn-sm"
                onClick={onLogin}
              >
                Iniciar sesión
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar