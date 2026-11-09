# Capa de servicios — LaundryDesk Frontend

**Actividad:** S07-S08-A1, Parte 1
**Alcance de este documento:** decisiones de diseño de `frontend/src/services/`. No cubre el flujo de autenticación ni la ruta protegida (Parte 2).

## 1. Cliente HTTP

Se usa **Fetch API nativo**, no Axios. Esta decisión ya estaba fijada en `decision_stack_frontend_FINAL.md` (sección 6) y confirmada en el `README.md` del frontend y en `package.json` (Axios no está instalado). No se agregó ninguna dependencia nueva.

## 2. Interceptores

Fetch no tiene interceptores nativos como Axios. Para cumplir el mismo propósito se centralizó toda llamada HTTP en una única función, `request()`, dentro de `src/services/api.js`. Ningún componente ni ningún otro servicio llama a `fetch` directamente; todos pasan por `request()`, que:

- arma la URL completa a partir de `VITE_API_URL` + la ruta del recurso;
- agrega el header `Authorization: Bearer <token>` automáticamente cuando hay una sesión guardada;
- serializa el `body` como JSON y fija `Content-Type: application/json`;
- aplica un timeout de 15 segundos por solicitud (`AbortController`);
- parsea la respuesta y, si el backend respondió con un error, lanza una excepción `ApiError` común en vez de dejar que cada pantalla interprete el `Response` por su cuenta.

Los cinco módulos por recurso (`authService.js`, `serviciosService.js`, `horariosService.js`, `pedidosService.js`, `seguimientosService.js`) son capas delgadas sobre `request()`: cada función ahí solo arma la ruta y el cuerpo de la petición según `openapi_equipo.yaml`.

## 3. Dónde se almacena el token

El JWT se guarda en **`sessionStorage`** (clave `laundrydesk_token`), dentro del propio `api.js` (`getToken`/`setToken`/`clearToken`), no en cada componente.

Razones:

- El backend (`backend/api/auth_utils.py`) emite un único *access token* sin *refresh token*; expira a los `JWT_EXPIRATION` segundos (3600 por defecto, 1 hora).
- Esta entrega no incluye pantalla de logout ("Se eliminó la página de registro y el logout completo para reducir tiempo", instrucciones S07-S08-A1), así que cerrar la pestaña cumple ese papel.
- Frente a `localStorage`, `sessionStorage` reduce la ventana de exposición si hubiera un XSS: el token no sobrevive a cerrar la pestaña ni se comparte entre pestañas.

**Riesgo que queda abierto:** ni `sessionStorage` ni `localStorage` protegen contra XSS (ambos son legibles por JavaScript). La mitigación real es evitar XSS en la interfaz (nunca usar `dangerouslySetInnerHTML` con datos del usuario, etc.), no el mecanismo de almacenamiento. Si más adelante se requiere una sesión que sobreviva a cerrar el navegador, la alternativa a evaluar es una cookie `httpOnly` emitida por el backend, que hoy no existe.

## 4. Manejo de errores centralizado

Todo error pasa una sola vez por `request()` en `api.js`, nunca disperso en los componentes:

| Caso | Qué hace `request()` |
|---|---|
| Sin conexión, backend caído, CORS, timeout | Captura la excepción de `fetch`, la registra en consola para depuración, y lanza `ApiError` con `codigo: 'ERROR_RED'` y un mensaje en español listo para mostrar al usuario (nunca el error técnico crudo). |
| Respuesta no es JSON interpretable | Lanza `ApiError` con `codigo: 'RESPUESTA_INVALIDA'`. |
| Respuesta HTTP de error (401/404/409/422/500, formato `{codigo, mensaje, errores?}` de `openapi_equipo.yaml`) | Lanza `ApiError` con esos mismos `codigo`, `mensaje` y `errores`, más el `status` HTTP. |
| 401 específicamente | Además de lanzar el error, limpia el token guardado (`clearToken()`), para que la siguiente pantalla protegida redirija al login en vez de reintentar con un token que el backend ya rechazó. |

Cada función de los servicios por recurso simplemente deja que `ApiError` se propague; las pantallas (Parte 2) la capturan con `try/catch` y leen `error.mensaje` (texto para el usuario) o `error.errores` (lista de `{campo, mensaje}` en los `422`, para marcar campos de formulario).

> **Nota de corrección:** la primera versión entregada seteaba el mensaje solo en `error.message` (heredado de `Error`) y nunca en `error.mensaje`, el campo que esta misma documentación dice que hay que leer. `run-verify.mjs` (sección 8) lo detectó; ya está corregido en `api.js` — `ApiError` ahora expone ambos (`message` para logs/consola, `mensaje` para la interfaz).

## 5. Estructura final

```text
src/services/
├── api.js                 # cliente fetch + ApiError + almacenamiento del token
├── authService.js          # /auth/register, /auth/login, /auth/me
├── serviciosService.js      # /servicios
├── horariosService.js       # /horarios
├── pedidosService.js        # /pedidos y sus subrecursos (estado, cambios-estado, notas)
└── seguimientosService.js   # /seguimientos/{codigo} (público)
```

Coincide con la estructura esperada en `decision_stack_frontend_FINAL.md` (sección 6), con `seguimientosService.js` agregado porque el contrato lo define como un recurso propio.

## 6. Variable de entorno

`VITE_API_URL` ya estaba configurada en `.env`/`.env.example` (`http://localhost:8000/api/v1`), tal como fija `decision_stack_frontend_FINAL.md`. `api.js` la lee con `import.meta.env.VITE_API_URL` y advierte en consola si falta.

## 7. Riesgos y divergencias encontradas (para resolver antes de la Parte 2 / el video)

1. **CORS no configurado en el backend.** `backend/config/settings.py` no incluye `django-cors-headers` ni `CorsMiddleware`. Al correr `npm run dev` (Vite, por defecto `localhost:5173`) contra `python manage.py runserver` (`localhost:8000`), el navegador bloqueará las llamadas por CORS aunque el código del frontend sea correcto — el login fallará con un error de red antes de llegar a escribir una sola línea de la Parte 2. Dos formas de resolverlo, no excluyentes:
   - **(A) `django-cors-headers` en el backend (recomendado — ya preparado, ver `backend_cors_fix.zip`).** Agrega el paquete, declara `CORS_ALLOWED_ORIGINS` (leída del `.env`, por defecto `http://localhost:5173`) y pone `CorsMiddleware` antes de `CommonMiddleware`. No toca `VITE_API_URL` (sigue siendo `http://localhost:8000/api/v1`, tal como lo documenta `decision_stack_frontend_FINAL.md`) y es lo que de todas formas hará falta en producción si el frontend y el backend quedan en dominios distintos de Render. Verificado con `python manage.py check` (0 issues) y un preflight CORS simulado: un origen permitido recibe `Access-Control-Allow-Origin`, uno no permitido no lo recibe. Falta que alguien con el backend lo aplique y lo pruebe contra la base de datos real.
   - **(B) Proxy de desarrollo en `vite.config.js` (solo frontend, pero divergente del documento del equipo).** Agregar `server.proxy: { '/api': 'http://localhost:8000' }` y cambiar `VITE_API_URL` a una ruta relativa (`/api/v1`) durante desarrollo; el navegador le habla a Vite y Vite reenvía la petición desde el servidor, sin CORS de por medio. Es una solución que no requiere tocar el backend, pero contradice el valor de `VITE_API_URL` que ya fijó el equipo en `decision_stack_frontend_FINAL.md`, y **no sirve para producción**: `vite build` genera archivos estáticos sin proxy, así que el CORS real en el backend va a hacer falta tarde o temprano de cualquier forma.
2. **`GET /pedidos`: filtros distintos entre el contrato y el backend implementado.** `openapi_equipo.yaml` documenta `estado_actual` (repetible), `fecha_desde` y `fecha_hasta`. `backend/api/views.py:PedidoListCreateView` filtra hoy con `estado`, `codigo_seguimiento` y `telefono_cliente`, y no implementa `fecha_desde`/`fecha_hasta`. `pedidosService.listar()` sigue el contrato (spec-first); si el backend no se actualiza, esos filtros no tendrán efecto todavía. La paginación (`pagina`, `tamano_pagina`) sí coincide entre ambos.
3. **`PUT /pedidos/{id}/estado`: forma de la respuesta distinta.** El contrato define `ResultadoCambioEstado` (`{pedido, cambio, aviso_correo}`). `backend/api/views.py:PedidoEstadoView` devuelve directamente el objeto `CambioEstado`. No afecta a esta actividad, pero hay que confirmarlo contra el backend real antes de construir la pantalla de cambio de estado.
4. **No hay refresh token.** El JWT expira en 1 hora (`JWT_EXPIRATION`) y no existe un endpoint para renovarlo. Cuando expira, cualquier llamada protegida devuelve 401, `api.js` limpia el token automáticamente, y el usuario deberá volver a iniciar sesión (lo resuelve la ruta protegida de la Parte 2).

## 8. Verificación (instrucciones, Parte 1, paso 2)

Las instrucciones piden verificar tres cosas antes de dar por buena la capa de servicios: que la URL base se lea de la variable de entorno, que el token se guarde de forma segura, y que los errores de red den un mensaje útil (no solo en consola). Como todavía no hay un backend corriendo para probar el flujo real, se automatizaron las tres como pruebas que simulan las respuestas del backend (sin red real) y se corren con:

```bash
npm run verify:servicios
```

Esto compila `src/_dev_verify_services.mjs` con Vite (`vite.verify.config.js`, para que `import.meta.env.VITE_API_URL` se resuelva igual que en la app real) y lo ejecuta con Node (`run-verify.mjs`, que simula `window.sessionStorage` y `fetch`). Comprueba:

1. `API_URL` viene de `VITE_API_URL`, no está hardcodeada en `api.js`.
2. `setToken()` guarda en `sessionStorage` bajo la clave correcta, y `request()` efectivamente agrega `Authorization: Bearer <token>` en cada llamada.
3. Un fallo de red (`fetch` lanzando, como pasaría por CORS o sin conexión) se traduce a un `ApiError` con `codigo: 'ERROR_RED'` y un mensaje en español apto para mostrar al usuario — nunca la excepción técnica cruda.
4. (Extra) Un `401` del backend limpia el token guardado, y un login `200` guarda el `access` token real.

Última corrida: **10/10 checks en verde** (ver nota de corrección en la sección 4 — esta prueba fue justo la que encontró el bug de `error.mensaje`).

Esto verifica la capa de servicios **de forma aislada**, sin depender de que el backend esté corriendo. Para verificar el flujo end-to-end contra el backend real (una vez resuelto el CORS de la sección 7) hace falta la Parte 2: una pantalla de login que llame a `authService.login()` de verdad e inspeccionar en DevTools → Application → Session Storage que `laundrydesk_token` aparece con el JWT real que devuelve `POST /auth/login`.

`src/_dev_verify_services.mjs`, `vite.verify.config.js`, `.env.verify` y `run-verify.mjs` son herramientas de desarrollo, no parte de la aplicación: no se importan desde `main.jsx` ni desde ninguna pantalla.
