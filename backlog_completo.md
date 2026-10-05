# Product Backlog — LaundryDesk

**Fuente:** `SRS_equipo.md`  
**Versión:** 1.0 — Propuesta inicial para revisión del equipo  
**Método de estimación:** Story Points, escala Fibonacci (1, 2, 3, 5, 8, 13)

---

## ÉPICA EP-01 — Portal público y seguimiento del cliente

**Objetivo:** Permitir que cualquier cliente consulte información vigente del negocio y conozca el estado de su pedido sin crear una cuenta.

### HU-01 — Consultar servicios, precios y horarios

**Historia de usuario:**  
Como **cliente**, quiero **consultar los servicios activos, precios vigentes y horarios de 21st Street Laundry**, para **conocer la oferta actual del negocio sin tener que llamar**.

**Prioridad:** Alta  
**Story Points:** 3  
**Trazabilidad:** RF-01; RNF-04

**Criterios de aceptación:**

1. **Dado que** un visitante accede al portal público, **cuando** consulta los servicios del negocio, **entonces** el sistema muestra los servicios activos y sus precios vigentes sin solicitar autenticación.
2. **Dado que** existen horarios configurados, **cuando** el visitante consulta la información del negocio, **entonces** el sistema muestra los horarios vigentes.

---

### HU-02 — Consultar el estado de un pedido

**Historia de usuario:**  
Como **cliente**, quiero **consultar el estado de mi pedido mediante mi código de seguimiento**, para **conocer su avance sin crear una cuenta ni llamar a la lavandería**.

**Prioridad:** Alta  
**Story Points:** 3  
**Trazabilidad:** RF-06; RNF-02; RNF-03; RD-05

**Criterios de aceptación:**

1. **Dado que** el cliente proporciona un código válido, **cuando** realiza la consulta, **entonces** el sistema muestra el código, el estado actual y la fecha de recepción sin mostrar datos personales o notas internas.
2. **Dado que** el código proporcionado no corresponde a un pedido, **cuando** se realiza la consulta, **entonces** el sistema informa que el código no fue encontrado y no muestra información de otros pedidos.
3. **Dado que** el pedido se encuentra en estado `Listo`, **cuando** el cliente consulta el código, **entonces** el sistema indica que está listo y muestra la fecha desde la cual se encuentra en ese estado cuando esté disponible.

---

## ÉPICA EP-02 — Acceso administrativo y recepción de pedidos

**Objetivo:** Permitir al dueño acceder de forma controlada al área administrativa y registrar correctamente los pedidos de wash & fold.

### HU-03 — Iniciar sesión como administrador

**Historia de usuario:**  
Como **administrador**, quiero **autenticarme antes de acceder al área administrativa**, para **proteger las funciones internas y los datos de los clientes**.

**Prioridad:** Alta  
**Story Points:** 3  
**Trazabilidad:** RF-02; RNF-05; RD-06

**Criterios de aceptación:**

1. **Dado que** el administrador proporciona credenciales válidas, **cuando** inicia sesión, **entonces** el sistema permite el acceso al área administrativa.
2. **Dado que** las credenciales son incorrectas, **cuando** intenta iniciar sesión, **entonces** el sistema rechaza el acceso.
3. **Dado que** un usuario no autenticado intenta acceder directamente a una función administrativa, **cuando** realiza la solicitud, **entonces** el sistema niega el acceso y solicita autenticación.

---

### HU-04 — Registrar un pedido de wash & fold

**Historia de usuario:**  
Como **administrador**, quiero **registrar un nuevo pedido de wash & fold con los datos básicos del cliente**, para **iniciar su trazabilidad desde el momento en que la ropa es recibida**.

**Prioridad:** Alta  
**Story Points:** 5  
**Trazabilidad:** RF-03; RD-02

**Criterios de aceptación:**

1. **Dado que** el administrador está autenticado y proporciona nombre, teléfono, servicio y fecha de recepción, **cuando** confirma el registro, **entonces** el sistema crea el pedido con estado inicial `Recibido`.
2. **Dado que** falta uno o más datos obligatorios, **cuando** intenta registrar el pedido, **entonces** el sistema identifica los campos faltantes y no crea el pedido.

---

### HU-05 — Completar los datos operativos del pedido

**Historia de usuario:**  
Como **administrador**, quiero **registrar o actualizar el peso, precio final e instrucciones especiales de un pedido**, para **mantener completa y actualizada la información necesaria para su operación**.

**Prioridad:** Alta  
**Story Points:** 5  
**Trazabilidad:** RF-04; RD-03

**Criterios de aceptación:**

1. **Dado que** existe un pedido sin peso registrado, **cuando** el administrador captura un peso válido y confirma, **entonces** el sistema guarda el valor asociado al pedido.
2. **Dado que** existe un pedido, **cuando** el administrador registra o modifica el precio final, **entonces** el sistema conserva el nuevo valor como precio actual.
3. **Dado que** el administrador agrega instrucciones especiales, **cuando** guarda los cambios, **entonces** el sistema las asocia al pedido sin modificar su estado.

---

### HU-06 — Generar un código único de seguimiento

**Historia de usuario:**  
Como **administrador**, quiero **que cada pedido registrado reciba automáticamente un código único de seguimiento**, para **poder entregarlo al cliente y habilitar la consulta posterior del pedido**.

**Prioridad:** Alta  
**Story Points:** 3  
**Trazabilidad:** RF-05; RNF-03

**Criterios de aceptación:**

1. **Dado que** un pedido se registra correctamente, **cuando** finaliza su creación, **entonces** el sistema genera un código de seguimiento asociado exclusivamente a ese pedido.
2. **Dado que** existen pedidos previamente registrados, **cuando** se crea uno nuevo, **entonces** su código no coincide con ningún código existente y no se genera como una secuencia simple predecible.

---

## ÉPICA EP-03 — Gestión operativa del ciclo de vida del pedido

**Objetivo:** Permitir al administrador conocer la carga de trabajo y controlar el pedido desde su recepción hasta su cierre.

### HU-07 — Consultar la lista de pedidos

**Historia de usuario:**  
Como **administrador**, quiero **consultar una lista consolidada de los pedidos registrados y su estado actual**, para **tener visibilidad de la carga de trabajo del negocio**.

**Prioridad:** Alta  
**Story Points:** 5  
**Trazabilidad:** RF-07

**Criterios de aceptación:**

1. **Dado que** existen pedidos registrados y el administrador está autenticado, **cuando** abre la sección de pedidos, **entonces** el sistema muestra los pedidos con su código y estado actual.
2. **Dado que** no existen pedidos registrados, **cuando** el administrador abre la sección, **entonces** el sistema indica que no existen pedidos disponibles.

---

### HU-08 — Filtrar pedidos

**Historia de usuario:**  
Como **administrador**, quiero **filtrar los pedidos por estado, fecha o ambos criterios**, para **localizar rápidamente los pedidos que requieren atención**.

**Prioridad:** Media  
**Story Points:** 3  
**Trazabilidad:** RF-07

**Criterios de aceptación:**

1. **Dado que** existen pedidos con diferentes fechas y estados, **cuando** el administrador aplica un filtro, **entonces** el sistema muestra únicamente los pedidos que cumplen los criterios seleccionados.
2. **Dado que** ningún pedido cumple los filtros aplicados, **cuando** se realiza la consulta, **entonces** el sistema informa que no existen pedidos para esos criterios.

---

### HU-09 — Actualizar el estado normal del pedido

**Historia de usuario:**  
Como **administrador**, quiero **actualizar el estado de un pedido siguiendo su flujo normal**, para **reflejar correctamente el avance real del servicio de wash & fold**.

**Prioridad:** Alta  
**Story Points:** 5  
**Trazabilidad:** RF-08; RD-01

**Criterios de aceptación:**

1. **Dado que** un pedido está en `Recibido`, `En proceso` o `Listo`, **cuando** el administrador selecciona el siguiente estado permitido y confirma, **entonces** el sistema guarda respectivamente `En proceso`, `Listo` o `Entregado`.
2. **Dado que** el administrador intenta una transición normal que no corresponde al flujo `Recibido → En proceso → Listo → Entregado`, **cuando** confirma el cambio, **entonces** el sistema rechaza la transición.

---

### HU-10 — Corregir un estado registrado por error

**Historia de usuario:**  
Como **administrador**, quiero **corregir manualmente un estado que fue registrado por error**, para **mantener la información del pedido consistente con la situación real**.

**Prioridad:** Media  
**Story Points:** 5  
**Trazabilidad:** RF-08

**Criterios de aceptación:**

1. **Dado que** un pedido tiene un estado incorrecto, **cuando** el administrador selecciona la opción de corrección manual y confirma explícitamente el cambio, **entonces** el sistema guarda el estado corregido.
2. **Dado que** se realiza una corrección manual, **cuando** posteriormente se consulta el pedido, **entonces** el estado corregido aparece como el estado vigente.

---

### HU-11 — Registrar notas e incidencias

**Historia de usuario:**  
Como **administrador**, quiero **registrar notas o incidencias relacionadas con un pedido**, para **conservar información relevante sin alterar automáticamente su flujo operativo**.

**Prioridad:** Media  
**Story Points:** 3  
**Trazabilidad:** RF-09; RNF-02

**Criterios de aceptación:**

1. **Dado que** existe un pedido, **cuando** el administrador registra una nota o incidencia, **entonces** el sistema la guarda asociada al pedido sin modificar su estado.
2. **Dado que** un pedido tiene notas o incidencias, **cuando** el administrador consulta su detalle, **entonces** el sistema las muestra en el área administrativa y no en la consulta pública.

---

### HU-12 — Cancelar un pedido antes de su procesamiento

**Historia de usuario:**  
Como **administrador**, quiero **cancelar un pedido que todavía no ha iniciado su procesamiento**, para **cerrar correctamente pedidos que ya no deben continuar**.

**Prioridad:** Media  
**Story Points:** 3  
**Trazabilidad:** RF-10; RD-04

**Criterios de aceptación:**

1. **Dado que** un pedido está en estado `Recibido`, **cuando** el administrador confirma su cancelación, **entonces** el sistema cambia su estado a `Cancelado`.
2. **Dado que** un pedido se encuentra en `En proceso`, `Listo` o `Entregado`, **cuando** se intenta cancelar mediante el flujo normal, **entonces** el sistema no lo cancela automáticamente e indica que el caso requiere revisión manual.

---

## ÉPICA EP-04 — Configuración del negocio y comunicación

**Objetivo:** Dar autonomía al dueño para mantener la información del negocio actualizada y reducir consultas manuales del cliente.

### HU-13 — Administrar los servicios ofrecidos

**Historia de usuario:**  
Como **administrador**, quiero **crear, modificar o desactivar servicios desde LaundryDesk**, para **mantener actualizada la oferta del negocio sin depender de un desarrollador**.

**Prioridad:** Media  
**Story Points:** 5  
**Trazabilidad:** RF-11; RNF-04

**Criterios de aceptación:**

1. **Dado que** el administrador está autenticado, **cuando** crea o modifica un servicio con información válida, **entonces** el sistema conserva la nueva configuración.
2. **Dado que** el administrador desactiva un servicio, **cuando** un visitante consulta los servicios disponibles, **entonces** dicho servicio no aparece como activo.

---

### HU-14 — Actualizar precios y horarios

**Historia de usuario:**  
Como **administrador**, quiero **actualizar los precios y horarios del negocio**, para **asegurar que los clientes siempre consulten información vigente**.

**Prioridad:** Alta  
**Story Points:** 3  
**Trazabilidad:** RF-11; RF-01

**Criterios de aceptación:**

1. **Dado que** el administrador modifica un precio u horario y guarda el cambio, **cuando** la operación finaliza correctamente, **entonces** el sistema conserva el nuevo valor.
2. **Dado que** existe una actualización guardada, **cuando** un visitante consulta posteriormente la información pública, **entonces** el sistema muestra el precio u horario vigente y no el valor anterior.

---

### HU-15 — Notificar al cliente cuando el pedido esté listo

**Historia de usuario:**  
Como **cliente**, quiero **recibir un correo cuando mi pedido esté listo**, para **saber que puedo recogerlo sin tener que llamar a la lavandería**.

**Prioridad:** Alta  
**Story Points:** 5  
**Trazabilidad:** RF-12; RNF-06

**Criterios de aceptación:**

1. **Dado que** un pedido tiene un correo electrónico asociado, **cuando** cambia al estado `Listo`, **entonces** el sistema genera una solicitud de correo con el destinatario, código de seguimiento y nuevo estado.
2. **Dado que** el servicio de correo falla después de que el estado `Listo` fue almacenado, **cuando** ocurre el error, **entonces** el sistema conserva el nuevo estado y no revierte el pedido.
3. **Dado que** un pedido no tiene correo electrónico registrado, **cuando** cambia a `Listo`, **entonces** el sistema guarda normalmente el cambio de estado sin bloquear la operación.

---

# Resumen del backlog

| Épica | Historias | Story Points |
|---|---:|---:|
| EP-01 — Portal público y seguimiento | HU-01 a HU-02 | 6 |
| EP-02 — Acceso administrativo y recepción | HU-03 a HU-06 | 16 |
| EP-03 — Gestión operativa | HU-07 a HU-12 | 24 |
| EP-04 — Configuración y comunicación | HU-13 a HU-15 | 13 |
| **Total** | **15 historias** | **59 SP** |

> Las estimaciones son iniciales y deberán ser revisadas por el equipo antes de comprometer un Sprint. Los Story Points representan complejidad, esfuerzo e incertidumbre relativa, no horas de trabajo.
