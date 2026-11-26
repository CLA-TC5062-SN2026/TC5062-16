# Code Review



## Alcance y archivo seleccionado

Revisé el frontend completo de LaundryDesk: 29 archivos del paquete `b58eb862-frontend.zip`, con lectura estática. No ejecuté el build ni las pruebas, porque el paquete no incluye `node\_modules`.

Archivo con la lógica más compleja: `src/frontend/src/services/api.js`, función `request()` (líneas 128 a 205). Concentra la construcción de la URL, el token, el timeout, el manejo de errores y la limpieza de sesión.

El paquete cubre la pantalla pública, la capa de servicios y el flujo de autenticación. El backend y el servicio de pedidos no forman parte de esta revisión.

## Evaluación SWEBOK por atributo de calidad

El atributo de calidad más débil es la verificación: solo un script manual cubre los servicios. El marco proviene de SWEBOK 2.6 (calidad) y de las KA relacionadas de calidad y gestión de configuración.

|Atributo (SWEBOK 2.6)|Calificación|Motivo principal|Hallazgos|
|-|-|-|-|
|Seguridad|Aceptable con riesgos|Token en `sessionStorage` (documentado). Sin invalidación en servidor. IDs sin codificar en las rutas.|H1, H2, H5|
|Confiabilidad|Parcial|Buen mapeo de errores, pero hay fugas fuera de `ApiError`. Lista vacía que oculta fallos de contrato.|H3, H4, H6, H11|
|Disponibilidad y rendimiento|Parcial|Timeout de 15 s. La página solo carga la primera página, sin controles para avanzar.|H3|
|Facilidad de uso|Buena|Mensajes en español, `aria-\*`, enlace de salto, estados de carga y error.|No aplica|
|Facilidad de modificación|Media-baja|Código repetido, SRP incumplido en dos archivos, nombres mezclados.|H7 a H10, H12|
|Verificación (SWEBOK 3.2)|Insuficiente|Solo cubre `api.js` y los servicios. Sin pruebas de contexto, rutas ni páginas.|H13|
|Gestión de configuración|Insuficiente|No hay `package-lock.json` ni `.gitignore`.|H13|

Lo bien hecho: la documentación de divergencias con el backend (comentarios "OJO") cumple con reportar y controlar (SWEBOK 3.5 y 3.6).

## Seguridad

Hay tres hallazgos de seguridad: H1 (sesión sin invalidación), H2 (token legible por scripts) y H5 (IDs sin codificar). Ninguno es explotable de forma inmediata desde el frontend, pero H1 y H2 se suman si hay un XSS.

### H1 · Cerrar sesión no invalida el JWT

* **Archivo y líneas:** `services/authService.js`, líneas 61 a 65 (`cerrarSesion`), y `context/AuthContext.jsx`, líneas 66 a 69.
* **Problema:** `cerrarSesion()` solo borra el token de `sessionStorage`. El backend no tiene endpoint de logout, así que un JWT copiado sigue válido hasta expirar, a los 3600 s.
* **Por qué es un problema:** el administrador cree que cerró sesión, pero un token robado sigue dando acceso a `/pedidos` durante una hora.
* **Corrección propuesta:** revocar el token en el backend y llamar a esa revocación desde el frontend. Backend (pseudocódigo: ajustar al objeto de token que use `auth\_utils.py`):

```python
import time
from django.core.cache import cache
from rest\_framework.permissions import IsAuthenticated
from rest\_framework.response import Response
from rest\_framework.views import APIView

class LogoutView(APIView):
    permission\_classes = \[IsAuthenticated]

    def post(self, request):
        # jti: identificador único del token; se guarda hasta su expiración.
        jti = request.auth\['jti']
        restante = request.auth\['exp'] - int(time.time())
        cache.set(f'jwt\_revocado:{jti}', True, timeout=max(restante, 1))
        return Response(status=204)
```

El middleware de autenticación debe rechazar cualquier token con `cache.get(f'jwt\_revocado:{jti}')` activo.

Frontend, `services/authService.js`:

```js
import { request, clearToken } from './api.js'

async function cerrarSesion() {
  try {
    await request('/auth/logout', { method: 'POST' })
  } catch {
    // Si el backend no responde, el token local se borra igual.
  } finally {
    clearToken()
  }
}
```

Con este cambio, `cerrarSesion` pasa a ser asíncrono. `LayoutAdministrativo` debe esperarla antes de navegar a `/login`.

### H2 · Token legible por cualquier script de la página

* **Archivo y líneas:** `services/api.js`, líneas 37 a 41 (comentario de decisión) y 43 a 47 (`getToken`).
* **Problema:** el token queda en `sessionStorage`, donde cualquier script de la página puede leerlo. El comentario dice que el riesgo queda acotado a la pestaña, pero eso no impide el robo.
* **Por qué es un problema:** una inyección de script (XSS) permite leer el token y enviarlo a un tercero, aunque la pestaña no se cierre.
* **Corrección propuesta:** limitar qué scripts pueden ejecutarse con una política de contenido (CSP) y corregir el comentario. En `index.html`, dentro de `<head>`:

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' https://TU-BACKEND.onrender.com">
```

El comentario de `api.js` debe decir: "sessionStorage reduce la persistencia del token, pero no lo protege de un XSS; la CSP es la mitigación principal".

### H5 · IDs sin codificar en las rutas

* **Archivo y líneas:** `services/pedidosService.js`, líneas 48, 61, 78, 83 y 88; `services/serviciosService.js`, líneas 21 y 34; `services/horariosService.js`, líneas 15 y 25. `services/seguimientosService.js`, línea 18, sí usa `encodeURIComponent`.
* **Problema:** el ID se concatena tal cual en la ruta.
* **Por qué es un problema:** un valor con `/`, `?` o `..` cambia la ruta o la query que llega al backend. El backend probablemente lo rechaza, pero el frontend no debe depender de eso. Además, la inconsistencia hace que cada servicio siga un patrón distinto.
* **Corrección propuesta:** un helper único que codifique el ID, usado en todas las funciones.

```js
// services/pedidosService.js
import { request } from './api.js'

// Codifica el ID: un valor con "/" o "?" no altera la ruta.
const rutaPedido = (pedidoId, sufijo = '') =>
  `/pedidos/${encodeURIComponent(pedidoId)}${sufijo}`

function obtener(pedidoId) {
  return request(rutaPedido(pedidoId))
}

function actualizarDatos(pedidoId, cambios) {
  return request(rutaPedido(pedidoId), { method: 'PATCH', body: cambios })
}

function cambiarEstado(pedidoId, cambio) {
  return request(rutaPedido(pedidoId, '/estado'), { method: 'PUT', body: cambio })
}

function listarCambiosEstado(pedidoId) {
  return request(rutaPedido(pedidoId, '/cambios-estado'))
}

function registrarNota(pedidoId, nota) {
  return request(rutaPedido(pedidoId, '/notas'), { method: 'POST', body: nota })
}
```

Las funciones `listar` y `crear` no cambian. Los servicios de servicios y horarios aplican el mismo patrón (ver DRY).

## Código duplicado (DRY)

Hay tres repeticiones claras. Cada una obliga a cambiar varios archivos ante un mismo ajuste.

### H7 · Operaciones CRUD idénticas en dos servicios

* **Archivo y líneas:** `services/serviciosService.js`, líneas 19 a 35, y `services/horariosService.js`, líneas 13 a 26.
* **Problema:** `obtener`, `crear` y `actualizar` son idénticas en ambos archivos, salvo por la ruta. `listar` también, excepto por el parámetro de servicios.
* **Por qué es un problema:** un cambio de contrato (por ejemplo, codificar el ID o agregar un encabezado) hay que replicarlo a mano en cada recurso. Ya ocurrió con H5.
* **Corrección propuesta:** una función fábrica para los recursos estándar.

```js
// services/recursoService.js
import { request } from './api.js'

// Operaciones CRUD de un recurso del contrato. El ID siempre se codifica.
export function crearRecurso(ruta) {
  const rutaConId = (id) => `${ruta}/${encodeURIComponent(id)}`

  return {
    listar: () => request(ruta),
    obtener: (id) => request(rutaConId(id)),
    crear: (datos) => request(ruta, { method: 'POST', body: datos }),
    actualizar: (id, cambios) => request(rutaConId(id), { method: 'PATCH', body: cambios }),
  }
}
```

```js
// services/horariosService.js
import { crearRecurso } from './recursoService.js'

const horarios = crearRecurso('/horarios')

export const listar = horarios.listar
export const obtener = horarios.obtener
export const crear = horarios.crear
export const actualizar = horarios.actualizar
```

```js
// services/serviciosService.js
import { request } from './api.js'
import { crearRecurso } from './recursoService.js'

const servicios = crearRecurso('/servicios')

export const obtener = servicios.obtener
export const crear = servicios.crear
export const actualizar = servicios.actualizar

// Solo la lista tiene una variante: incluir los servicios inactivos.
export function listar({ incluirInactivos = false } = {}) {
  return request('/servicios', {
    params: incluirInactivos ? { incluir\_inactivos: 'true' } : undefined,
  })
}
```

### H7b · Markup repetido: enlace de salto, `<main>` y spinner

* **Archivo y líneas:** el enlace de salto aparece en `App.jsx` (líneas 23 a 28), `LoginPage.jsx` (líneas 91 a 96) y `HomePage.jsx` (líneas 42 a 47). El `<main id="contenido-principal">` aparece en `App.jsx` (línea 36), `LoginPage.jsx` (línea 100) y `HomePage.jsx` (líneas 57 a 61). El spinner de "Verificando sesión..." aparece en `RutaProtegida.jsx` (líneas 8 a 18) y `LoginPage.jsx` (líneas 27 a 37).
* **Problema:** el mismo bloque se copia tres o dos veces.
* **Por qué es un problema:** si el enlace de salto y el `id` de `<main>` no coinciden en una pantalla, la navegación por teclado falla sin aviso. Son fallos de accesibilidad difíciles de detectar.
* **Corrección propuesta:** componentes compartidos.

```jsx
// components/EstructuraPagina.jsx
export function EnlaceSalto() {
  return (
    <a href='#contenido-principal' className='visually-hidden-focusable position-absolute top-0 start-0 m-2 btn btn-light'>
      Saltar al contenido principal
    </a>
  )
}

export function ContenidoPrincipal({ children }) {
  return (
    <main id='contenido-principal' className='container py-5' tabIndex='-1'>
      {children}
    </main>
  )
}
```

```jsx
// components/CargaIndicador.jsx
export default function CargaIndicador({ mensaje = 'Cargando...' }) {
  return (
    <div className='d-flex justify-content-center align-items-center py-5' role='status'>
      <span className='spinner-border text-primary me-2' aria-hidden='true' />
      <span>{mensaje}</span>
    </div>
  )
}
```

En `RutaProtegida.jsx` y en `LoginPage.jsx`, el bloque `if (cargando)` queda como `if (cargando) return <CargaIndicador mensaje={'Verificando sesión...'} />`.

## Funciones con múltiples responsabilidades (SRP)

Hay dos funciones con varias responsabilidades. Una es la pieza más crítica del frontend.

### H8 · `request()` hace siete tareas en una sola función

* **Archivo y líneas:** `services/api.js`, líneas 128 a 205.
* **Problema:** la misma función construye la URL (líneas 129 a 139), añade el token (141 a 145), aplica el timeout (147 a 148), traduce errores de red (158 a 164), interpreta el cuerpo (169 a 182), traduce errores del backend (184 a 202) y limpia la sesión en un 401 (185 a 190).
* **Por qué es un problema:** cualquier cambio en una tarea afecta a las demás. El efecto secundario de limpiar el token queda oculto dentro de una función que parece solo de lectura. Probar cada caso exige montar toda la función.
* **Corrección propuesta:** separar cada tarea en una función con un solo propósito. `request()` solo coordina. El cambio también corrige H4, porque la interpretación del cuerpo queda dentro del `try`.

```js
// services/api.js (estructura propuesta)
function construirUrl(path, params) {
  const url = new URL(`${API\_URL}${path}`)
  const entradas = params instanceof URLSearchParams ? params.entries() : Object.entries(params ?? {})
  for (const \[clave, valor] of entradas) {
    if (valor !== undefined \&\& valor !== null \&\& valor !== '') url.searchParams.append(clave, valor)
  }
  return url
}

function encabezados() {
  const token = getToken()
  const base = { 'Content-Type': 'application/json' }
  return token ? { ...base, Authorization: `Bearer ${token}` } : base
}

function errorDeRespuesta(response, datos) {
  if (response.status === 401) clearToken() // el backend rechazó el token
  return new ApiError({
    mensaje: datos?.mensaje || 'Ocurrió un problema. Intenta de nuevo en unos minutos.',
    codigo: datos?.codigo || 'ERROR\_DESCONOCIDO',
    errores: datos?.errores || \[],
    status: response.status,
  })
}

async function request(path, { method = 'GET', body, params, timeoutMs = 15000 } = {}) {
  const url = construirUrl(path, params)
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)

  let response
  let texto
  try {
    response = await fetch(url, {
      method,
      headers: encabezados(),
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
    texto = await response.text()
  } catch (error) {
    throw errorDeRed(error, url) // H4: ahora cubre también la lectura del cuerpo
  } finally {
    window.clearTimeout(timeoutId)
  }

  const datos = interpretarCuerpo(texto, url, response.status)
  if (!response.ok) throw errorDeRespuesta(response, datos)
  return datos
}
```

`errorDeRed` e `interpretarCuerpo` se extraen del `request` actual sin cambios de lógica, salvo lo indicado en H4. Estas funciones deben quedar en el mismo archivo.

### H8b · `LoginPage` mezcla validación, envío y mapeo de errores

* **Archivo y líneas:** `pages/LoginPage.jsx`, líneas 49 a 87 (`handleSubmit`).
* **Problema:** la misma función valida los campos (53 a 57), llama a la sesión (61), separa los errores por campo y los extras (70 a 78) y arma la alerta (80 a 85).
* **Por qué es un problema:** las reglas de validación no se pueden probar sin renderizar la página, y cualquier cambio en el formato de error obliga a tocar el formulario.
* **Corrección propuesta:** dos funciones puras fuera del componente.

```jsx
// pages/LoginPage.jsx (fuera del componente)
function validarFormulario({ email, password }) {
  const errores = {}
  if (!email.trim()) errores.email = 'Ingresa tu correo electrónico.'
  if (!password) errores.password = 'Ingresa tu contraseña.'
  return errores
}

function separarErroresDeServidor(errores = \[]) {
  const porCampo = {}
  const extras = \[]
  for (const { campo, mensaje } of errores) {
    if (CAMPOS.includes(campo)) porCampo\[campo] = mensaje
    else extras.push(mensaje)
  }
  return { porCampo, extras }
}

// Dentro del componente, handleSubmit queda así:
const handleSubmit = async (event) => {
  event.preventDefault()
  setAlerta(null)

  const erroresLocales = validarFormulario({ email, password })
  setErroresCampo(erroresLocales)
  if (Object.keys(erroresLocales).length > 0) return

  setEnviando(true)
  try {
    await iniciarSesion(email.trim(), password)
  } catch (error) {
    setEnviando(false)
    // Aquí va el bloque actual de mapeo y alerta, usando separarErroresDeServidor(error?.errores).
  }
}
```

## Manejo de excepciones

Hay cuatro hallazgos de manejo de errores. H11 es el más grave porque la pantalla pública entrega una respuesta falsa.

### H11 · Consulta simulada en la pantalla pública

* **Archivo y líneas:** `pages/HomePage.jsx`, líneas 14 a 32 (`handleSubmit`) y línea 51 (usuario fijo).
* **Problema:** la consulta usa un `setTimeout` de 700 ms y muestra "Consulta de demostración realizada". No llama a `seguimientosService`, que ya existe. Además, `Navbar` usa estado local (`isAuthenticated`, líneas 12, 50 y 53) en lugar de `AuthContext`.
* **Por qué es un problema:** un cliente recibe una confirmación inventada. Un error real del backend, como un código inexistente, nunca se muestra. Y hay dos fuentes de verdad para la sesión.
* **Corrección propuesta:** usar el servicio real y manejar sus errores.

```jsx
import \* as seguimientosService from '../services/seguimientosService.js'

const handleSubmit = async (event) => {
  event.preventDefault()
  setMessage('')

  const codigoLimpio = codigo.trim()
  if (codigoLimpio.length < 5) {
    setError('Ingresa un código de seguimiento válido.')
    return
  }

  setError('')
  setIsLoading(true)
  try {
    const pedido = await seguimientosService.consultar(codigoLimpio)
    // Confirmar en openapi\_equipo.yaml el nombre del campo de estado.
    setMessage(`Estado de tu pedido: ${pedido.estado\_actual}.`)
  } catch (error) {
    setError(
      error.codigo === 'NO\_ENCONTRADO'
        ? 'No encontramos un pedido con ese código.'
        : error.mensaje,
    )
  } finally {
    setIsLoading(false)
  }
}
```

El `Navbar` de esta página debe leer `useAuth()` y eliminar sus `useState` de sesión.

### H3 · Respuesta con formato inesperado se muestra como lista vacía

* **Archivo y líneas:** `pages/PedidosPage.jsx`, línea 53 (`datos?.resultados || \[]`) y líneas 54 a 58.
* **Problema:** si la respuesta no trae `resultados` como lista, el código lo trata como lista vacía y muestra "Todavía no hay pedidos registrados".
* **Por qué es un problema:** el desfase con el backend ya está documentado en `pedidosService.js`. Si ocurre, el administrador cree que no hay pedidos y nadie ve el error. Además, la página solo carga la primera página y no ofrece controles para avanzar, aunque el servicio acepta `pagina`.
* **Corrección propuesta:** validar la forma de la respuesta y tratar un formato inválido como error.

```jsx
import { ApiError } from '../services/api.js'

function esRespuestaDePedidos(datos) {
  return Array.isArray(datos?.resultados) \&\& typeof datos?.total === 'number'
}

// Dentro de cargar(), tras la comprobación de solicitud vigente:
const datos = await pedidosService.listar()
if (id !== solicitudActual.current) return

if (!esRespuestaDePedidos(datos)) {
  throw new ApiError({
    mensaje: 'La lista de pedidos llegó con un formato inesperado.',
    codigo: 'RESPUESTA\_INESPERADA',
  })
}

const { resultados, total } = datos
setVista(resultados.length === 0 ? { tipo: 'vacio' } : { tipo: 'datos', resultados, total })
```

Para la paginación, el estado debe guardar `pagina` y los botones "Anterior" y "Siguiente" deben llamar a `cargar` con esa página.

### H4 · Errores que se escapan del tipo `ApiError`

* **Archivo y líneas:** `services/api.js`, línea 129 (`new URL(...)`) y línea 169 (`response.text()`), ambas fuera del `try` que mapea errores.
* **Problema:** si falta `VITE\_API\_URL`, `new URL` lanza un `TypeError` sin `mensaje`. Si la lectura del cuerpo falla a mitad de la transferencia, el `TypeError` también escapa. El check 3a del script de verificación no cubre estos dos casos.
* **Por qué es un problema:** el encabezado del archivo promete un único tipo de error. Las pantallas leen `error.mensaje` y `error.esErrorDeRed`, que no existen en un `TypeError`. El login muestra el mensaje genérico sin explicar la causa, y el desarrollador solo ve un error en consola.
* **Corrección propuesta:** traducir ambos casos a `ApiError`. Estas funciones reemplazan el bloque de errores del `request` actual (las usa H8):

```js
// services/api.js
function errorDeRed(error, url) {
  console.error(`\[capa de servicios] Falló la conexión con ${url}:`, error)
  return new ApiError({ mensaje: mensajeDeRed(error), codigo: 'ERROR\_RED', esErrorDeRed: true })
}

function interpretarCuerpo(texto, url, status) {
  if (!texto) return null
  try {
    return JSON.parse(texto)
  } catch (error) {
    console.error(`\[capa de servicios] Respuesta no interpretable de ${url}:`, error)
    throw new ApiError({
      mensaje: 'El servidor respondió con un formato inesperado.',
      codigo: 'RESPUESTA\_INVALIDA',
      status,
    })
  }
}
```

En `request`, `construirUrl` también debe envolverse:

```js
let url
try {
  url = construirUrl(path, params)
} catch {
  throw new ApiError({
    mensaje: 'La dirección del servidor no está configurada. Revisa VITE\_API\_URL.',
    codigo: 'CONFIGURACION\_INVALIDA',
  })
}
```

### H6 · El comentario de `AuthContext` no coincide con el comportamiento

* **Archivo y líneas:** `context/AuthContext.jsx`, líneas 33 a 38.
* **Problema:** el comentario dice que ante un error de red "el token se conserva", pero `setAdministrador(null)` (línea 38) manda al usuario a `/login`. El token sigue guardado, pero la pantalla no lo usa.
* **Por qué es un problema:** el comentario documenta una intención que el código no cumple. Quien mantenga el código puede asumir que la sesión se recupera al recargar, y no es así.
* **Corrección propuesta:** dejar explícito el comportamiento actual y corregir el comentario. Si el equipo prefiere mantener la sesión visible, debe agregarse un estado "no verificada" con botón de reintento en `RutaProtegida`.

```jsx
.catch((error) => {
  if (cancelado) return
  // Cualquier fallo impide confirmar la sesión y la ruta protegida manda a /login.
  // Si no fue un 401, el token NO se borra: se reintenta al recargar la página.
  if (error?.status !== 401) {
    console.error('\[AuthContext] No se pudo validar la sesión guardada:', error)
  }
  setAdministrador(null)
})
```

## Nombres poco descriptivos o mezclados

El proyecto mezcla español e inglés sin regla. Los nombres de dominio están en español y las funciones de sesión y de red en inglés. Algunos nombres de estado tampoco dicen qué representan.

### H9 · Nombres mezclados y poco descriptivos

* **Archivo y líneas:**

  * `services/authService.js`, líneas 19 (`login`), 45 (`registrar`), 57 (`obtenerPerfil`) y 63 (`cerrarSesion`).
  * `pages/HomePage.jsx`, líneas 8 a 12: `isLoading`, `message`, `isAuthenticated`, mientras el resto de la app usa español.
  * `pages/LoginPage.jsx`, líneas 70 a 78: `extras` no dice qué contiene (son mensajes generales del servidor).
* **Problema:** conviven `login` con `cerrarSesion`, y `isLoading` con `enviando` y `cargando`, para el mismo concepto. Un lector no sabe si `extras` son errores, avisos o advertencias.
* **Por qué es un problema:** los nombres son la primera documentación del código. Si el mismo concepto tiene varios nombres, es fácil duplicar funciones sin notarlo, y cambiar uno exige buscar todas las variantes.
* **Corrección propuesta:** una regla escrita en `README.md`. Los conceptos de dominio van en español (`pedido`, `sesión`, `mensajesGenerales`). Los términos genéricos de React y de la librería Fetch, como `request` o `ApiError`, pueden quedarse en inglés porque son convención del ecosistema. Ejemplos aplicados:

```js
// services/authService.js
async function iniciarSesion(email, password) {
  const datos = await request('/auth/login', { method: 'POST', body: { email, password } })
  setToken(datos.access)
  return { access: datos.access, tipo: datos.tipo, expiraEn: datos.expira\_en }
}

function registrarAdministrador({ usuario, email, password }) {
  return request('/auth/register', { method: 'POST', body: { usuario, email, password } })
}

export { iniciarSesion, registrarAdministrador, obtenerPerfil, cerrarSesion, haySesionActiva }
```

```jsx
// pages/LoginPage.jsx
const { porCampo, mensajesGenerales } = separarErroresDeServidor(error?.errores)
```

```jsx
// pages/HomePage.jsx
const \[estaConsultando, setEstaConsultando] = useState(false)
const \[mensajeConsulta, setMensajeConsulta] = useState('')
```

Al renombrar `login` hay que actualizar la llamada en `context/AuthContext.jsx` (línea 50) y `registrar` no tiene consumidores, por eso se elimina en H10.

## Configuración, pruebas y código muerto

Este bloque agrupa los hallazgos que no son de código de aplicación: entregables, configuración del repositorio y verificación. Son los que más pesan en SWEBOK 3.2 (verificación) y en la gestión de configuración.

### H10 · Código muerto y herramientas de verificación dentro de la entrega

* **Archivo y líneas:** `services/authService.js`, líneas 45 a 50 (`registrar`, sin consumidores). `src/\_dev\_verify\_services.mjs`, `run-verify.mjs` y `vite.verify.config.js`, que el propio archivo marca como "no forma parte de la entrega". `components/README.md` y `context/README.md` describen trabajo futuro ya hecho.
* **Problema:** el paquete incluye scripts temporales y una función sin uso.
* **Por qué es un problema:** el código muerto se lee como parte del sistema y confunde a quien lo mantenga. Los scripts temporales dentro de `src/` pueden terminar en el build si alguien los importa.
* **Corrección propuesta:** eliminar `registrar` del archivo de servicios y migrar la verificación a pruebas formales en `tests/`, fuera de `src/`. Ejemplo con Vitest:

```js
// tests/pedidosService.test.js
import { describe, it, expect, vi, afterEach } from 'vitest'
import \* as pedidosService from '../src/services/pedidosService.js'

describe('pedidosService', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('codifica el ID de pedido en la ruta (H5)', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)

    await pedidosService.obtener('1/../usuarios')

    expect(fetchMock.mock.calls\[0]\[0].toString()).toContain('/pedidos/1%2F..%2Fusuarios')
  })
})
```

Los componentes README deben reescribirse como documentación real o eliminarse.

### H12 · Otros hallazgos de calidad

* **`pages/PedidosPage.jsx`, líneas 45 a 79:** `cargar` se define dentro del componente y el `useEffect` la usa con `\[]` como dependencias. React advierte de esto con la regla `react-hooks/exhaustive-deps`, pero el proyecto no tiene ESLint. Corrección:

```jsx
const cargar = useCallback(async () => {
  // ...mismo cuerpo que antes
}, \[cerrarSesion, navigate])

useEffect(() => {
  cargar()
  return () => {
    solicitudActual.current += 1
  }
}, \[cargar])
```

* **`components/Navbar.jsx`, línea 18:** `<a href="/">` recarga toda la aplicación en vez de navegar con el router. Corrección: `<Link className='navbar-brand fw-semibold' to='/'>LaundryDesk</Link>`, importando `Link` de `react-router-dom`.
* **`App.jsx`, líneas 45 a 58:** no hay ruta comodín. Una URL inexistente muestra una pantalla en blanco. Corrección: agregar `<Route path='\*' element={<Navigate to='/' replace />} />`, importando `Navigate`.

### H13 · Configuración del repositorio y pruebas

* **Archivo:** el paquete no incluye `package-lock.json` ni `.gitignore`. `package.json` no tiene script de pruebas ni de lint.
* **Problema:** sin lock file, cada instalación puede resolver versiones distintas de React o Vite. Sin `.gitignore`, `node\_modules` y `.env` pueden subirse al repositorio. Sin pruebas ni lint, la verificación depende de revisar a mano.
* **Por qué es un problema:** es un riesgo de configuración (SWEBOK gestión de configuración) y de verificación (SWEBOK 3.2). El archivo `.env` puede contener la URL del backend o credenciales de prueba.
* **Corrección propuesta:** generar el lock file, ignorar los archivos sensibles y agregar scripts.

```gitignore
# .gitignore
node\_modules/
dist/
verify-dist/
.env
```

```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "test": "vitest run",
  "lint": "eslint ."
}
```

Comandos: `npm install` (genera `package-lock.json`), `npm install -D vitest eslint eslint-plugin-react-hooks`.

## Resumen priorizado

Hay 13 hallazgos: 2 altos, 7 medios, 1 bajo-medio y 3 bajos. Los dos altos son la consulta simulada en la pantalla pública (H11) y la sesión que no se invalida (H1).

|ID|Severidad|Archivo|Líneas|Hallazgo|
|-|-|-|-|-|
|H11|Alta|`pages/HomePage.jsx`|14 a 32, 51|Consulta simulada; no usa `seguimientosService`.|
|H1|Alta|`services/authService.js`|61 a 65|Cerrar sesión no revoca el JWT (3600 s). Requiere backend.|
|H3|Media|`pages/PedidosPage.jsx`|53|Respuesta con formato inesperado se muestra como lista vacía. Sin paginación.|
|H4|Media|`services/api.js`|129, 169|Errores que escapan de `ApiError`.|
|H2|Media|`services/api.js`|37 a 47|Token legible por cualquier script; falta CSP.|
|H5|Media|`services/pedidosService.js` y otros|48 a 88|IDs sin codificar en las rutas.|
|H7|Media|`serviciosService.js`, `horariosService.js`|19 a 35, 13 a 26|CRUD idéntico repetido (DRY).|
|H8|Media|`services/api.js`|128 a 205|`request()` con siete responsabilidades (SRP).|
|H13|Media|Repositorio|No aplica|Sin lock file, sin `.gitignore`, sin pruebas ni lint.|
|H6|Baja-media|`context/AuthContext.jsx`|33 a 38|El comentario no coincide con el comportamiento.|
|H9|Baja|Varios|Ver sección|Nombres mezclados en español e inglés.|
|H10|Baja|`services/authService.js`, `src/`|45 a 50|Código muerto y scripts de verificación dentro de la entrega.|
|H12|Baja|`PedidosPage.jsx`, `Navbar.jsx`, `App.jsx`|73 a 79, 18, 45 a 58|Dependencias de `useEffect`, enlace que recarga la app y falta de ruta 404.|

Orden sugerido de corrección:

1. H11 y H1, por riesgo para el usuario.
2. H3, H4, H2 y H5, por confiabilidad y seguridad.
3. H7, H8 y H13, porque facilitan todo lo demás.
4. H9, H10 y H12, al final.

Limitaciones de esta revisión: no ejecuté el build ni las pruebas, porque el paquete no incluye dependencias. Las correcciones están escritas, pero no probadas. No revisé el backend ni el contrato `openapi\_equipo.yaml`; los hallazgos H1 y H3 dependen de ellos. Los números de línea corresponden a los archivos tal como llegaron en el zip.

