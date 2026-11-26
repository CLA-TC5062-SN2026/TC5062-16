# Matriz de trazabilidad de requerimientos — LaundryDesk

## 1. Objetivo

Esta matriz conecta los requerimientos funcionales definidos en `SRS_equipo.md` con las historias de usuario del `backlog_completo.md`, la implementación disponible en la rama `main` y la evidencia de verificación disponible al cierre del proyecto.

La clasificación considera el sistema completo, no únicamente la existencia de un endpoint.

- **Completo:** el comportamiento requerido se encuentra implementado de extremo a extremo o la capacidad requerida está completamente cubierta.
- **Parcialmente implementado:** existe una parte funcional de la solución, pero falta algún elemento requerido para completar el flujo.
- **No implementado:** no existe una implementación funcional del requerimiento.

> La evaluación corresponde al estado de la rama `main` utilizada para la entrega final. Los cambios disponibles únicamente en otras ramas no se consideran implementados.

---

## 2. Matriz de trazabilidad

| Requerimiento del SRS | Historia(s) de usuario | Implementación / endpoint | Evidencia de verificación | Estado | Justificación |
|---|---|---|---|---|---|
| **RF-01 — Consultar información pública del negocio** | HU-01 — Consultar servicios, precios y horarios | `GET /api/v1/servicios`; `GET /api/v1/horarios` | **PM-01**. Endpoints públicos disponibles sin JWT | **Parcialmente implementado** | El backend expone servicios y horarios, pero el frontend público actual no muestra ambos catálogos al visitante. |
| **RF-02 — Autenticar al administrador** | HU-03 — Iniciar sesión como administrador | `POST /api/v1/auth/login`; `GET /api/v1/auth/me`; `AuthContext.jsx`; `LoginPage.jsx`; `RutaProtegida.jsx` | **PM-02**; `npm run verify:servicios`; `S07_S08_A2/flujo_auth.mp4` | **Completo** | Existe autenticación real mediante JWT, almacenamiento de la sesión durante la pestaña y protección de las rutas administrativas. |
| **RF-03 — Registrar un pedido de wash & fold** | HU-04 — Registrar un pedido | `POST /api/v1/pedidos` | **PM-03** | **Parcialmente implementado** | La API permite crear pedidos, pero no existe una pantalla administrativa para hacerlo desde el frontend. |
| **RF-04 — Completar o actualizar datos operativos del pedido** | HU-05 — Completar los datos operativos | `PATCH /api/v1/pedidos/{id}` | **PM-04** | **Parcialmente implementado** | El endpoint permite modificar información del pedido, pero la operación todavía no está disponible mediante una pantalla administrativa. |
| **RF-05 — Generar código de seguimiento** | HU-06 — Generar código único | `generar_codigo_seguimiento()` en `backend/api/services.py` durante la creación del pedido | **PM-03** | **Completo** | Al crear el pedido se genera un código de seguimiento aleatorio, se comprueba su unicidad y queda asociado al pedido. |
| **RF-06 — Consultar públicamente el estado de un pedido** | HU-02 — Consultar estado del pedido | `GET /api/v1/seguimientos/{codigo_seguimiento}`; `seguimientosService.js` | **PM-05** | **Parcialmente implementado** | El endpoint público y la capa de servicios existen, pero `HomePage.jsx` en `main` todavía utiliza una respuesta simulada y no consulta el backend real. |
| **RF-07 — Consultar y filtrar pedidos** | HU-07 — Consultar pedidos; HU-08 — Filtrar pedidos | `GET /api/v1/pedidos`; `PedidosPage.jsx`; `pedidosService.js` | **PM-06**; evidencia audiovisual `S07_S08_A2/flujo_e2e.mp4` | **Parcialmente implementado** | El listado funciona en backend y frontend, pero la interfaz no ofrece filtros. Además, existen diferencias entre los filtros descritos en el contrato y los implementados en backend. |
| **RF-08 — Gestionar el estado de un pedido** | HU-09 — Actualizar estado; HU-10 — Corregir estado | `PUT /api/v1/pedidos/{id}/estado`; `GET /api/v1/pedidos/{id}/cambios-estado` | **PM-07** | **Parcialmente implementado** | El backend implementa transiciones, historial y correcciones controladas, pero no existe una interfaz administrativa para ejecutar estas operaciones. |
| **RF-09 — Registrar notas e incidencias** | HU-11 — Registrar notas e incidencias | `POST /api/v1/pedidos/{id}/notas` | **PM-08** | **Parcialmente implementado** | La operación existe en la API y no modifica el estado del pedido, pero no existe una pantalla administrativa para registrar o consultar las notas. |
| **RF-10 — Cancelar un pedido** | HU-12 — Cancelar pedido antes de procesamiento | `PUT /api/v1/pedidos/{id}/estado` con estado `CANCELADO` | **PM-09** | **Parcialmente implementado** | El backend soporta cancelación, pero no existe una interfaz gráfica. Además, el SRS permite la cancelación normal desde `Recibido`, mientras el backend actual también la permite desde `En proceso`. |
| **RF-11 — Administrar servicios, precios y horarios** | HU-13 — Administrar servicios; HU-14 — Actualizar precios y horarios | `GET/POST /api/v1/servicios`; `GET/PATCH /api/v1/servicios/{id}`; `GET/POST /api/v1/horarios`; `GET/PATCH /api/v1/horarios/{id}` | **PM-10**; `npm run verify:servicios` verifica la capa HTTP del frontend | **Parcialmente implementado** | El CRUD necesario está disponible en la API y existen servicios frontend, pero no existen pantallas administrativas para estas operaciones. |
| **RF-12 — Notificar que un pedido está listo** | HU-15 — Notificar al cliente | `cambiar_estado()` registra una `Notificacion` con canal `CORREO` y estado `PENDIENTE` al cambiar a `LISTO` cuando existe correo | **PM-11** | **Parcialmente implementado** | Se implementó el registro transaccional de la notificación, pero no existe el proceso externo encargado de enviar físicamente el correo. |

---

## 3. Resumen de implementación

| Estado | Requerimientos |
|---|---|
| **Completo** | RF-02, RF-05 |
| **Parcialmente implementado** | RF-01, RF-03, RF-04, RF-06, RF-07, RF-08, RF-09, RF-10, RF-11, RF-12 |
| **No implementado** | Ninguno completamente ausente |

El núcleo de negocio se encuentra considerablemente más avanzado en el backend que en el frontend.

El principal gap del proyecto no es la ausencia de la lógica de dominio, sino que varias capacidades disponibles mediante API todavía no cuentan con una interfaz gráfica para el administrador.

---

## 4. Divergencias relevantes encontradas

### 4.1 Cancelación de pedidos

El SRS establece que un pedido puede cancelarse normalmente mientras se encuentra en estado `Recibido`.

La implementación actual también permite una transición normal:

```text
EN_PROCESO → CANCELADO
```

Por ello, RF-10 permanece como parcialmente implementado respecto a la especificación.

### 4.2 Filtros de pedidos

El SRS contempla filtrado administrativo por fecha y estado.

El backend actual no coincide completamente con los filtros definidos en el contrato de API, y la pantalla `PedidosPage.jsx` no incorpora controles de filtrado.

### 4.3 Seguimiento público

El backend incluye:

```text
GET /api/v1/seguimientos/{codigo_seguimiento}
```

y el frontend cuenta con `seguimientosService.js`.

Sin embargo, la versión de `HomePage.jsx` disponible en `main` todavía muestra una respuesta de demostración mediante temporizador y no consume el endpoint real.

Por ello, RF-06 se clasifica como parcialmente implementado.

### 4.4 Notificación por correo

El cambio de un pedido a `LISTO` puede crear una notificación en estado `PENDIENTE`.

Este mecanismo implementa la preparación de la notificación y evita que una falla posterior de correo revierta el cambio de estado.

Sin embargo, no existe todavía un componente que procese dichas notificaciones y envíe físicamente el correo.

---

## 5. Casos manuales de cierre

Los siguientes casos se definen como evidencia reproducible para la validación final y la preparación de la demo.

### PM-01 — Información pública

**Objetivo:** comprobar acceso público a información del negocio.

1. Ejecutar `GET /api/v1/servicios` sin JWT.
2. Ejecutar `GET /api/v1/horarios` sin JWT.

**Resultado esperado:** HTTP `200` y datos públicos sin requerir autenticación.

---

### PM-02 — Autenticación y protección

**Objetivo:** comprobar autenticación administrativa.

1. Iniciar sesión con credenciales válidas.
2. Confirmar recepción del JWT.
3. Acceder a `/pedidos` con JWT.
4. Intentar acceder al endpoint administrativo sin JWT.
5. Probar credenciales incorrectas.

**Resultado esperado:**

- Credenciales válidas → acceso permitido.
- Sin token → `401`.
- Credenciales incorrectas → autenticación rechazada.

---

### PM-03 — Crear pedido y generar código

**Objetivo:** comprobar registro de pedidos y generación del código de seguimiento.

1. Ejecutar `POST /api/v1/pedidos` autenticado.
2. Proporcionar los datos requeridos.
3. Revisar la respuesta.

**Resultado esperado:** pedido creado y código de seguimiento generado automáticamente.

---

### PM-04 — Actualizar pedido

**Objetivo:** comprobar modificación de datos operativos.

1. Seleccionar un pedido existente.
2. Ejecutar `PATCH /api/v1/pedidos/{id}`.
3. Cambiar un dato permitido.
4. Consultar nuevamente el pedido.

**Resultado esperado:** el cambio queda persistido.

---

### PM-05 — Seguimiento público

**Objetivo:** comprobar la capacidad real de seguimiento disponible en backend.

1. Tomar el código creado en PM-03.
2. Ejecutar `GET /api/v1/seguimientos/{codigo}` sin JWT.
3. Probar también un código inexistente.

**Resultado esperado:**

- Código válido → estado del pedido.
- Código inexistente → error controlado.

---

### PM-06 — Consulta administrativa de pedidos

**Objetivo:** comprobar el listado de pedidos.

1. Iniciar sesión en el frontend.
2. Entrar a `/pedidos`.
3. Verificar que aparezcan los pedidos existentes.

**Resultado esperado:** listado obtenido desde el backend y mostrado en la interfaz.

---

### PM-07 — Gestión de estados y error controlado

**Objetivo:** comprobar las reglas de transición.

1. Seleccionar un pedido en estado `RECIBIDO`.
2. Cambiarlo a `EN_PROCESO`.
3. Consultar el historial.
4. Intentar posteriormente una transición no permitida.

**Resultado esperado:**

- Transición válida → cambio registrado.
- Historial → registra el cambio.
- Transición inválida → rechazo mediante error controlado.

Este caso es candidato para mostrar el **caso de error manejado en el video final**.

---

### PM-08 — Registrar nota

**Objetivo:** comprobar el registro de notas e incidencias.

1. Ejecutar `POST /api/v1/pedidos/{id}/notas`.
2. Registrar una nota.
3. Consultar el pedido.

**Resultado esperado:** la nota queda asociada al pedido sin modificar su estado.

---

### PM-09 — Cancelación

**Objetivo:** comprobar el comportamiento de cancelación.

1. Crear o seleccionar un pedido `RECIBIDO`.
2. Cambiarlo a `CANCELADO`.
3. Consultar el historial.

**Resultado esperado:** el pedido queda cancelado y el evento queda registrado.

> La prueba también deberá considerar la divergencia conocida de cancelación desde `EN_PROCESO`.

---

### PM-10 — Servicios y horarios

**Objetivo:** comprobar las operaciones administrativas de configuración.

Ejecutar mediante API:

```text
GET /servicios
POST /servicios
PATCH /servicios/{id}

GET /horarios
POST /horarios
PATCH /horarios/{id}
```

**Resultado esperado:** los datos se crean y modifican correctamente con autenticación administrativa cuando corresponde.

---

### PM-11 — Notificación pendiente

**Objetivo:** comprobar la preparación de una notificación.

1. Utilizar un pedido con correo electrónico registrado.
2. Cambiar el estado a `LISTO`.
3. Verificar el registro de notificación.

**Resultado esperado:** se crea una notificación con canal `CORREO` y estado `PENDIENTE`.

> Esta prueba no implica que el correo haya sido enviado físicamente.

---

## 6. Evidencia adicional disponible

El repositorio contiene evidencia complementaria:

- `S07_S08_A2/flujo_auth.mp4`
- `S07_S08_A2/flujo_e2e.mp4`
- `frontend/src/_dev_verify_services.mjs`
- `frontend/run-verify.mjs`
- `frontend/vite.verify.config.js`
- `code_review.md`
- `S09_A1.zip`

La capa de servicios frontend puede verificarse mediante:

```bash
cd frontend
npm run verify:servicios
```

La última documentación de esa verificación reportó **10/10 comprobaciones satisfactorias** para el comportamiento aislado de la capa de servicios.

---

## 7. Conclusión

LaundryDesk implementa la mayor parte de las capacidades de dominio definidas en el SRS, particularmente a nivel de backend.

Los requerimientos completamente cubiertos son la autenticación administrativa y la generación del código de seguimiento.

El resto presenta principalmente brechas de integración con la interfaz gráfica o componentes complementarios pendientes, como el envío efectivo de correo.

La matriz refleja el estado real de la rama `main` al cierre del proyecto y evita considerar como implementadas funcionalidades que únicamente existen en ramas no integradas.