# Software Requirements Specification (SRS)
## LaundryDesk — 21st Street Laundry

**Versión:** 0.9 — Borrador consolidado para validación del equipo  
**Estructura:** IEEE 830 simplificada  
**Documento:** Contrato compartido del proyecto  
**Proyecto:** LaundryDesk  

---

# 1. Introducción

## 1.1 Propósito del documento

El presente documento consolida los SRS individuales elaborados por los integrantes del equipo y establece la especificación compartida de **LaundryDesk** para 21st Street Laundry.

Su objetivo es servir como fuente de verdad para las siguientes etapas del proyecto: definición del Product Backlog, diseño de API, desarrollo de backend y frontend, pruebas y documentación final.

El documento define:

- El alcance de la primera versión.
- Los actores y responsabilidades principales.
- Los requerimientos funcionales.
- Los requerimientos no funcionales.
- Las reglas de dominio.
- Los criterios de aceptación en formato Given-When-Then.
- La trazabilidad mediante identificadores `RF-XX-AC-Y`.

Los identificadores definidos en esta versión deberán conservarse en las actividades posteriores del equipo.

---

## 1.2 Alcance del sistema

**LaundryDesk** será una aplicación web para apoyar la operación del servicio de **wash & fold** de 21st Street Laundry y mantener actualizada la información pública del negocio.

Actualmente, 21st Street Laundry funciona principalmente como una lavandería de autoservicio. El nuevo servicio de wash & fold requiere una herramienta para registrar pedidos, identificar al cliente, controlar el estado de la ropa, consultar la carga de trabajo y permitir que el cliente conozca el avance de su pedido sin tener que llamar al negocio.

LaundryDesk contará con una sección pública para clientes y una sección administrativa protegida mediante autenticación.

### Dentro del alcance de la primera versión

- Consulta pública de servicios, precios y horarios.
- Autenticación del administrador.
- Registro administrativo de pedidos de wash & fold.
- Registro de datos del cliente asociados al pedido.
- Registro y actualización de peso, precio final e instrucciones especiales.
- Generación de un código único de seguimiento.
- Consulta pública del estado del pedido mediante código.
- Consulta y filtrado administrativo de pedidos.
- Actualización y corrección controlada de estados.
- Registro de notas e incidencias.
- Cancelación de pedidos conforme a las reglas de negocio.
- Notificación por correo electrónico cuando un pedido se encuentre listo, cuando exista un correo registrado.
- Administración de servicios, precios y horarios.
- Protección y conservación controlada de datos personales.

### Fuera del alcance de la primera versión

- Recolección de ropa a domicilio.
- Entrega de ropa a domicilio.
- Agenda de recolecciones por franjas horarias.
- Validación de cobertura geográfica.
- Tarifas de recolección.
- Cuentas de cliente.
- Historial personalizado por cliente.
- Pagos en línea.
- Almacenamiento de datos bancarios o de tarjetas.
- Notificaciones mediante SMS.
- Integración automática con lavadoras o secadoras.
- Consulta en tiempo real de disponibilidad de máquinas.
- Administración de múltiples empleados o roles diferenciados.
- Promociones personalizadas por cliente.

La recolección a domicilio se considera una posible evolución futura y requerirá una nueva revisión de requerimientos antes de incorporarse a la línea base del sistema.

---

## 1.3 Definiciones y acrónimos

| Término | Definición |
|---|---|
| **LaundryDesk** | Aplicación web definida en este proyecto. |
| **21st Street Laundry** | Negocio para el cual se desarrolla LaundryDesk. |
| **Wash & fold** | Servicio en el que el cliente entrega ropa para que el personal la lave, seque y doble. |
| **Cliente** | Persona que utiliza los servicios de 21st Street Laundry. |
| **Administrador** | Dueño del negocio y único usuario con acceso administrativo en la primera versión. |
| **Pedido** | Registro de un servicio wash & fold asociado a un cliente. |
| **Código de seguimiento** | Identificador único utilizado para consultar públicamente el estado de un pedido. |
| **Pedido activo** | Pedido cuyo estado no es `Entregado` ni `Cancelado`. |
| **Pedido cerrado** | Pedido cuyo estado final es `Entregado` o `Cancelado`. |
| **Incidencia** | Observación o situación excepcional registrada durante el procesamiento de un pedido. |
| **RF** | Requerimiento Funcional. |
| **RNF** | Requerimiento No Funcional. |
| **RD** | Requerimiento de Dominio. |
| **AC** | Acceptance Criterion / Criterio de aceptación. |
| **SRS** | Software Requirements Specification. |
| **MVP** | Minimum Viable Product / Producto Mínimo Viable. |
| **Given-When-Then** | Estructura para expresar una precondición, una acción y un resultado observable. |

---

# 2. Descripción general

## 2.1 Perspectiva del producto

LaundryDesk será un sistema web nuevo e independiente. No sustituirá ni se conectará con las máquinas de autoservicio.

El sistema tendrá dos áreas principales:

### Portal público

Disponible sin autenticación.

Permitirá al cliente:

- Consultar servicios activos.
- Consultar precios vigentes.
- Consultar horarios.
- Introducir un código de seguimiento.
- Consultar el estado de un pedido.

### Área administrativa

Disponible únicamente mediante autenticación.

Permitirá al dueño:

- Registrar pedidos de wash & fold.
- Completar o actualizar datos operativos del pedido.
- Consultar y filtrar pedidos.
- Consultar el detalle de un pedido.
- Modificar estados.
- Corregir un estado registrado por error.
- Registrar notas e incidencias.
- Cancelar pedidos cuando corresponda.
- Actualizar servicios, precios y horarios.

LaundryDesk podrá utilizar un servicio externo de correo electrónico para enviar avisos relacionados con pedidos listos.

---

## 2.2 Funciones principales del producto

1. Mostrar información pública vigente del negocio.
2. Autenticar al administrador.
3. Registrar pedidos de wash & fold.
4. Registrar peso, precio final e instrucciones especiales.
5. Generar códigos únicos de seguimiento.
6. Permitir la consulta pública del estado de pedidos.
7. Mostrar al administrador los pedidos registrados.
8. Filtrar pedidos por fecha y estado.
9. Gestionar el ciclo de vida del pedido.
10. Corregir estados registrados por error.
11. Registrar notas e incidencias.
12. Gestionar cancelaciones.
13. Actualizar servicios, precios y horarios.
14. Generar notificaciones por correo cuando un pedido esté listo.

---

## 2.3 Características de los usuarios

### Cliente

El cliente utilizará principalmente la sección pública del sistema.

No deberá crear una cuenta ni recordar una contraseña para consultar información del negocio o revisar el estado de su pedido.

La interfaz deberá ser comprensible para usuarios con distintos niveles de experiencia digital y usable desde dispositivos móviles.

### Administrador

El administrador será inicialmente el dueño de 21st Street Laundry.

Será el único usuario con privilegios administrativos y deberá autenticarse antes de acceder a las funciones internas.

No se asume que tenga conocimientos técnicos especializados. Las operaciones frecuentes deberán poder realizarse mediante la interfaz gráfica sin modificar código ni acceder directamente a la base de datos.

---

## 2.4 Restricciones generales

- Existirá un solo usuario administrador en la primera versión.
- Los clientes no estarán obligados a crear una cuenta.
- La información personal no deberá mostrarse en la consulta pública.
- El sistema no procesará pagos en línea.
- El sistema no almacenará datos de tarjetas o información bancaria.
- El sistema no dependerá de sensores o modificaciones físicas en las máquinas.
- La recolección a domicilio no forma parte del MVP.
- Las notificaciones SMS no forman parte del MVP.
- La información pública deberá poder modificarse sin cambiar código fuente.
- Una falla del servicio externo de correo no deberá revertir cambios guardados en un pedido.

---

# 3. Requerimientos específicos

## 3.1 Requerimientos funcionales

### RF-01 — Consultar información pública del negocio

El sistema debe permitir a cualquier visitante consultar sin autenticación los servicios activos, precios vigentes y horarios de atención de 21st Street Laundry.

#### Criterios de aceptación

**RF-01-AC-1**  
**Dado que** un visitante accede al portal público,  
**cuando** consulta los servicios del negocio,  
**entonces** el sistema debe mostrar los servicios activos y sus precios vigentes sin solicitar autenticación.

**RF-01-AC-2**  
**Dado que** existen horarios de atención configurados,  
**cuando** un visitante consulta la información del negocio,  
**entonces** el sistema debe mostrar los horarios vigentes.

---

### RF-02 — Autenticar al administrador

El sistema debe requerir autenticación antes de permitir el acceso a cualquier función administrativa.

#### Criterios de aceptación

**RF-02-AC-1**  
**Dado que** el administrador proporciona credenciales válidas,  
**cuando** solicita iniciar sesión,  
**entonces** el sistema debe autenticarlo y permitirle acceder al área administrativa.

**RF-02-AC-2**  
**Dado que** las credenciales proporcionadas son incorrectas,  
**cuando** se intenta iniciar sesión,  
**entonces** el sistema debe rechazar la autenticación y no permitir el acceso administrativo.

**RF-02-AC-3**  
**Dado que** un usuario no autenticado intenta acceder directamente a una función administrativa,  
**cuando** realiza la solicitud,  
**entonces** el sistema debe negar el acceso y solicitar autenticación.

---

### RF-03 — Registrar un pedido de wash & fold

El sistema debe permitir al administrador registrar un nuevo pedido de wash & fold.

El registro deberá incluir como mínimo:

- Nombre del cliente.
- Número de teléfono.
- Servicio solicitado.
- Fecha de recepción.

El sistema permitirá registrar un correo electrónico cuando el cliente desee recibir notificaciones digitales.

#### Criterios de aceptación

**RF-03-AC-1**  
**Dado que** el administrador está autenticado y proporciona todos los datos obligatorios,  
**cuando** confirma el registro,  
**entonces** el sistema debe crear el pedido con estado inicial `Recibido`.

**RF-03-AC-2**  
**Dado que** falta uno o más datos obligatorios,  
**cuando** el administrador intenta registrar el pedido,  
**entonces** el sistema debe indicar los campos faltantes y no crear el pedido.

**RF-03-AC-3**  
**Dado que** un usuario no autenticado intenta registrar un pedido,  
**cuando** solicita ejecutar la operación,  
**entonces** el sistema debe rechazarla.

---

### RF-04 — Completar o actualizar datos operativos del pedido

El sistema debe permitir al administrador registrar o modificar el peso, el precio final y las instrucciones especiales asociadas con un pedido.

El peso y el precio podrán registrarse después de la creación inicial cuando todavía no se conozcan en el momento de recepción.

#### Criterios de aceptación

**RF-04-AC-1**  
**Dado que** existe un pedido registrado sin peso,  
**cuando** el administrador captura un peso válido y confirma el cambio,  
**entonces** el sistema debe guardar dicho peso asociado al pedido.

**RF-04-AC-2**  
**Dado que** existe un pedido registrado,  
**cuando** el administrador registra o modifica su precio final y confirma el cambio,  
**entonces** el sistema debe conservar el nuevo valor como precio actual del pedido.

**RF-04-AC-3**  
**Dado que** existe un pedido,  
**cuando** el administrador registra instrucciones especiales,  
**entonces** el sistema debe asociarlas con el pedido sin modificar su estado.

---

### RF-05 — Generar código de seguimiento

El sistema debe generar automáticamente un código único de seguimiento para cada pedido registrado.

#### Criterios de aceptación

**RF-05-AC-1**  
**Dado que** un pedido fue registrado correctamente,  
**cuando** finaliza su creación,  
**entonces** el sistema debe generar un código de seguimiento asociado exclusivamente con dicho pedido.

**RF-05-AC-2**  
**Dado que** existen pedidos previamente registrados,  
**cuando** se crea un nuevo pedido,  
**entonces** su código de seguimiento no debe coincidir con el código de ningún pedido existente.

---

### RF-06 — Consultar públicamente el estado de un pedido

El sistema debe permitir a un cliente consultar el estado de su pedido mediante el código de seguimiento, sin crear una cuenta.

#### Criterios de aceptación

**RF-06-AC-1**  
**Dado que** el cliente proporciona un código de seguimiento válido,  
**cuando** realiza la consulta,  
**entonces** el sistema debe mostrar el código, el estado actual y la fecha de recepción del pedido.

**RF-06-AC-2**  
**Dado que** el pedido se encuentra en estado `Listo`,  
**cuando** el cliente consulta un código válido,  
**entonces** el sistema debe indicar que el pedido está listo y mostrar la fecha desde la cual se encuentra en ese estado, cuando esté disponible.

**RF-06-AC-3**  
**Dado que** el código proporcionado no corresponde a ningún pedido,  
**cuando** se realiza la consulta,  
**entonces** el sistema debe informar que el código no fue encontrado y no mostrar información de otros pedidos.

---

### RF-07 — Consultar y filtrar pedidos desde el área administrativa

El sistema debe permitir al administrador consultar una lista consolidada de pedidos y aplicar filtros por estado, fecha o ambos.

#### Criterios de aceptación

**RF-07-AC-1**  
**Dado que** el administrador está autenticado y existen pedidos registrados,  
**cuando** abre la sección de pedidos,  
**entonces** el sistema debe mostrar los pedidos junto con su código y estado actual.

**RF-07-AC-2**  
**Dado que** existen pedidos con diferentes fechas y estados,  
**cuando** el administrador aplica un filtro por fecha, estado o ambos,  
**entonces** el sistema debe mostrar únicamente los pedidos que cumplan los criterios seleccionados.

**RF-07-AC-3**  
**Dado que** no existen pedidos que cumplan los filtros seleccionados,  
**cuando** el administrador realiza la consulta,  
**entonces** el sistema debe indicar que no existen pedidos para esos criterios.

---

### RF-08 — Gestionar el estado de un pedido

El sistema debe permitir al administrador actualizar el estado de un pedido de acuerdo con el flujo normal definido por el dominio y realizar una corrección manual cuando un estado haya sido registrado por error.

#### Criterios de aceptación

**RF-08-AC-1**  
**Dado que** un pedido está en estado `Recibido`,  
**cuando** el administrador confirma el cambio a `En proceso`,  
**entonces** el sistema debe guardar `En proceso` como estado actual.

**RF-08-AC-2**  
**Dado que** un pedido está en estado `En proceso`,  
**cuando** el administrador confirma el cambio a `Listo`,  
**entonces** el sistema debe guardar `Listo` como estado actual.

**RF-08-AC-3**  
**Dado que** un pedido está en estado `Listo`,  
**cuando** el administrador confirma el cambio a `Entregado`,  
**entonces** el sistema debe guardar `Entregado` como estado actual.

**RF-08-AC-4**  
**Dado que** el administrador intenta realizar una transición normal que no corresponde al flujo definido en RD-01,  
**cuando** confirma el cambio,  
**entonces** el sistema debe rechazar la transición normal.

**RF-08-AC-5**  
**Dado que** un estado fue registrado por error,  
**cuando** el administrador selecciona una corrección manual y la confirma explícitamente,  
**entonces** el sistema debe guardar el estado corregido como estado vigente.

---

### RF-09 — Registrar notas e incidencias

El sistema debe permitir al administrador registrar notas o incidencias asociadas con un pedido sin alterar automáticamente su estado.

#### Criterios de aceptación

**RF-09-AC-1**  
**Dado que** existe un pedido,  
**cuando** el administrador registra una nota o incidencia,  
**entonces** el sistema debe guardarla asociada con dicho pedido sin cambiar su estado.

**RF-09-AC-2**  
**Dado que** un pedido tiene notas o incidencias registradas,  
**cuando** el administrador consulta su detalle,  
**entonces** el sistema debe mostrar las notas e incidencias asociadas.

---

### RF-10 — Cancelar un pedido

El sistema debe permitir al administrador cancelar un pedido antes de que haya iniciado el procesamiento normal de la ropa.

#### Criterios de aceptación

**RF-10-AC-1**  
**Dado que** un pedido está en estado `Recibido`,  
**cuando** el administrador confirma su cancelación,  
**entonces** el sistema debe cambiar su estado a `Cancelado`.

**RF-10-AC-2**  
**Dado que** un pedido se encuentra en estado `En proceso`, `Listo` o `Entregado`,  
**cuando** el administrador intenta cancelarlo mediante el flujo normal,  
**entonces** el sistema no debe cancelarlo automáticamente y debe indicar que el caso requiere revisión manual.

---

### RF-11 — Administrar servicios, precios y horarios

El sistema debe permitir al administrador crear, modificar o desactivar servicios y actualizar precios y horarios sin modificar el código fuente.

#### Criterios de aceptación

**RF-11-AC-1**  
**Dado que** el administrador está autenticado,  
**cuando** crea o modifica un servicio con información válida y guarda los cambios,  
**entonces** el sistema debe conservar la nueva configuración.

**RF-11-AC-2**  
**Dado que** el administrador modifica un precio u horario y guarda los cambios,  
**cuando** un visitante consulta posteriormente la información pública,  
**entonces** el sistema debe mostrar el valor vigente actualizado.

**RF-11-AC-3**  
**Dado que** el administrador desactiva un servicio,  
**cuando** un visitante consulta posteriormente los servicios disponibles,  
**entonces** el servicio desactivado no debe aparecer como disponible.

---

### RF-12 — Notificar que un pedido está listo

El sistema debe permitir generar una notificación por correo electrónico cuando un pedido cambie al estado `Listo`, siempre que el pedido tenga un correo electrónico registrado.

#### Criterios de aceptación

**RF-12-AC-1**  
**Dado que** un pedido tiene un correo electrónico asociado,  
**cuando** su estado cambia a `Listo`,  
**entonces** LaundryDesk debe generar una solicitud al servicio de correo con al menos el destinatario, el código de seguimiento y el nuevo estado.

**RF-12-AC-2**  
**Dado que** el servicio externo de correo devuelve un error o no está disponible,  
**cuando** el cambio del pedido a `Listo` ya fue almacenado,  
**entonces** la falla del correo no debe revertir el estado guardado.

**RF-12-AC-3**  
**Dado que** un pedido no tiene correo electrónico registrado,  
**cuando** cambia al estado `Listo`,  
**entonces** el sistema debe guardar normalmente el nuevo estado sin bloquear la operación.

---

## 3.2 Requerimientos no funcionales

### RNF-01 — Disponibilidad

LaundryDesk debe mantener una disponibilidad mensual mínima del **99 % durante los horarios de operación vigentes** configurados para 21st Street Laundry.

**Categoría:** Disponibilidad

---

### RNF-02 — Protección de datos personales

Los datos personales de los clientes deberán ser accesibles únicamente desde el área administrativa autenticada.

La consulta pública no deberá mostrar, como mínimo:

- Número de teléfono.
- Correo electrónico.
- Instrucciones internas.
- Notas o incidencias administrativas.

**Categoría:** Seguridad / Privacidad

---

### RNF-03 — Protección del código de seguimiento

El código de seguimiento debe ser único y no deberá generarse como una secuencia numérica incremental simple o fácilmente predecible a partir de códigos anteriores.

**Categoría:** Seguridad

---

### RNF-04 — Usabilidad y compatibilidad móvil

Las funciones principales del portal público y del área administrativa deberán poder utilizarse desde dispositivos móviles mediante una interfaz gráfica adaptable, sin requerir desplazamiento horizontal para las operaciones principales.

El administrador no deberá necesitar modificar código fuente, archivos de configuración ni acceder directamente a la base de datos para realizar las operaciones definidas en este SRS.

**Categoría:** Usabilidad

---

### RNF-05 — Control de acceso

Todas las funciones que creen, modifiquen o eliminen información administrativa deberán requerir una sesión autenticada.

Las funciones públicas deberán permanecer separadas de las funciones administrativas.

**Categoría:** Seguridad

---

### RNF-06 — Integridad y persistencia de pedidos

La información de los pedidos y sus estados deberá conservarse aunque el usuario cierre el navegador o cambie de dispositivo.

Una falla de un servicio externo, incluyendo el servicio de correo electrónico, no deberá provocar pérdida de pedidos ni revertir cambios previamente almacenados.

**Categoría:** Confiabilidad / Persistencia

---

## 3.3 Requerimientos de dominio

### RD-01 — Flujo normal del pedido

El flujo normal de un pedido wash & fold será:

**Recibido → En proceso → Listo → Entregado**

Las actualizaciones normales deberán respetar este orden.

---

### RD-02 — Estado inicial

Todo pedido de wash & fold registrado correctamente deberá iniciar con estado `Recibido`.

---

### RD-03 — Peso y precio final

El peso y el precio final de un pedido podrán completarse después del registro inicial cuando no sean conocidos al momento de recibir al cliente.

No se establece en esta línea base una fórmula fija de cálculo de precio por libra ni un mínimo de peso, debido a que los SRS individuales no presentaron una regla común confirmada.

---

### RD-04 — Cancelación

Un pedido en estado `Recibido` podrá cancelarse mediante el flujo normal.

Una cancelación solicitada una vez iniciado el procesamiento requerirá revisión manual.

---

### RD-05 — Consulta sin cuenta de cliente

Los clientes podrán consultar información pública y el estado de sus pedidos sin crear una cuenta.

El código de seguimiento será el identificador principal utilizado para la consulta pública.

---

### RD-06 — Usuario administrador

Durante la primera versión, el dueño de 21st Street Laundry será el único usuario con privilegios administrativos.

La administración de empleados o roles diferenciados queda fuera del alcance del MVP.

---

### RD-07 — Conservación de datos

Se considera pedido cerrado aquel cuyo estado final sea `Entregado` o `Cancelado`.

Los datos personales asociados con pedidos cerrados podrán conservarse durante un máximo de **12 meses a partir de la fecha de cierre**. Después de ese periodo deberán eliminarse o anonimizarse.

---

### RD-08 — Recolección a domicilio como evolución futura

La recolección y entrega a domicilio no forman parte de la primera versión de LaundryDesk.

Si estas modalidades se incorporan posteriormente, deberán especificarse nuevas reglas para cobertura, horarios, capacidad, tarifas y estados adicionales antes de implementarlas.

---

# 4. Matriz de trazabilidad

| Requerimiento | Función / Caso de uso conceptual | Criterios de aceptación |
|---|---|---|
| RF-01 | Consultar información pública | RF-01-AC-1, RF-01-AC-2 |
| RF-02 | Autenticar administrador | RF-02-AC-1, RF-02-AC-2, RF-02-AC-3 |
| RF-03 | Registrar pedido wash & fold | RF-03-AC-1, RF-03-AC-2, RF-03-AC-3 |
| RF-04 | Completar datos operativos | RF-04-AC-1, RF-04-AC-2, RF-04-AC-3 |
| RF-05 | Generar código de seguimiento | RF-05-AC-1, RF-05-AC-2 |
| RF-06 | Consultar estado del pedido | RF-06-AC-1, RF-06-AC-2, RF-06-AC-3 |
| RF-07 | Consultar y filtrar pedidos | RF-07-AC-1, RF-07-AC-2, RF-07-AC-3 |
| RF-08 | Gestionar estados | RF-08-AC-1 a RF-08-AC-5 |
| RF-09 | Registrar notas e incidencias | RF-09-AC-1, RF-09-AC-2 |
| RF-10 | Cancelar pedido | RF-10-AC-1, RF-10-AC-2 |
| RF-11 | Administrar servicios, precios y horarios | RF-11-AC-1 a RF-11-AC-3 |
| RF-12 | Notificar pedido listo | RF-12-AC-1, RF-12-AC-2, RF-12-AC-3 |

---

# 5. Resumen de la línea base consolidada

La línea base del equipo establece el siguiente flujo principal:

**Información pública → registro administrativo del pedido → código de seguimiento → procesamiento → actualización de estado → consulta del cliente → notificación de pedido listo → entrega.**

Esta versión contiene:

- **12 requerimientos funcionales.**
- **6 requerimientos no funcionales.**
- **8 requerimientos de dominio.**
- **34 criterios de aceptación identificados de forma única.**

La recolección a domicilio, las ventanas de recolección, las reglas de cobertura, las tarifas de recolección, las notificaciones SMS y la integración con máquinas quedan fuera de esta línea base.

Una vez validado por los integrantes del equipo, este `SRS_equipo.md` se convertirá en la fuente de verdad del proyecto para las actividades posteriores del curso.
