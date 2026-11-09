/**
 * Estado compartido de la sesión del administrador (decision_stack_frontend_FINAL.md,
 * sección 5). Solo guarda QUIÉN está autenticado; el token lo guarda y lo
 * limpia la capa de servicios (api.js), así que aquí no se toca.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import * as authService from '../services/authService.js'

const AuthContext = createContext(null)

function AuthProvider({ children }) {
  const [administrador, setAdministrador] = useState(null)
  // Si no hay token guardado no hay nada que validar: se arranca ya resuelto
  // y la pantalla no parpadea con un indicador de carga innecesario.
  const [cargando, setCargando] = useState(() => authService.haySesionActiva())

  useEffect(() => {
    if (!authService.haySesionActiva()) return

    // En StrictMode el efecto se monta dos veces; la bandera evita que la
    // respuesta de la primera llamada actualice un estado ya descartado.
    let cancelado = false

    authService
      .obtenerPerfil()
      .then((perfil) => {
        if (!cancelado) setAdministrador(perfil)
      })
      .catch((error) => {
        if (cancelado) return
        // 401: api.js ya limpió el token; basta con no tener administrador.
        // Cualquier otro error (red, 500) tampoco permite confirmar la sesión,
        // pero el token se conserva: no fue rechazado, solo no se pudo validar.
        if (error?.status !== 401) {
          console.error('[AuthContext] No se pudo validar la sesión guardada:', error)
        }
        setAdministrador(null)
      })
      .finally(() => {
        if (!cancelado) setCargando(false)
      })

    return () => {
      cancelado = true
    }
  }, [])

  const iniciarSesion = useCallback(async (email, password) => {
    await authService.login(email, password)

    // POST /auth/login solo devuelve el token; los datos del administrador
    // vienen de GET /auth/me.
    try {
      const perfil = await authService.obtenerPerfil()
      setAdministrador(perfil)
      return perfil
    } catch (error) {
      // Sin perfil no hay sesión utilizable: se descarta el token recién
      // guardado para no quedar en un estado a medias.
      authService.cerrarSesion()
      throw error
    }
  }, [])

  const cerrarSesion = useCallback(() => {
    authService.cerrarSesion()
    setAdministrador(null)
  }, [])

  const valor = useMemo(
    () => ({
      administrador,
      estaAutenticado: administrador !== null,
      cargando,
      iniciarSesion,
      cerrarSesion,
    }),
    [administrador, cargando, iniciarSesion, cerrarSesion],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}

function useAuth() {
  const contexto = useContext(AuthContext)
  if (contexto === null) {
    throw new Error('useAuth() debe usarse dentro de <AuthProvider>.')
  }
  return contexto
}

export { AuthProvider, useAuth }
