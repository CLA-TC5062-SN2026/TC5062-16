# Diferencias entre SRS individuales
## LaundryDesk — 21st Street Laundry

**Objetivo:** documentar las diferencias identificadas entre los cuatro SRS individuales, las aportaciones de cada integrante y la propuesta de resolución utilizada para construir el borrador de `SRS_equipo.md`. Las resoluciones deberán ser validadas por el equipo antes de declararlas definitivas.

---

# 1. Documentos comparados

Para la consolidación se utilizaron cuatro versiones individuales:

1. **SRS de Isai** — versión actualizada conforme al nuevo `proyecto_base.md`.
2. **SRS de SVA** — `SRS_final_SVA.md`.
3. **SRS de Colunga** — `SRS_final_Colunga.md`.
4. **SRS de Compañero 3** — `SRS_final_Compañero3.md`.

El `proyecto_base.md` actualizado se utilizó como referencia común de alcance cuando existía una contradicción directa entre las versiones individuales.

---

# 2. Criterio utilizado para la consolidación

Las diferencias se clasificaron de la siguiente forma:

- **Consenso:** funcionalidad o regla presente de forma equivalente en todos o en la mayoría de los SRS y compatible con el proyecto base vigente.
- **Gap:** requerimiento identificado únicamente por uno o algunos integrantes que no contradice necesariamente al resto.
- **Conflicto:** dos o más SRS especifican comportamientos o alcances incompatibles.

Para resolver conflictos se aplicaron, en orden:

1. Alcance vigente de `proyecto_base.md`.
2. Coincidencia entre varios SRS.
3. Menor cantidad de supuestos no validados.
4. Simplicidad y coherencia con el MVP.
5. Posibilidad de dejar una funcionalidad como evolución futura sin perderla del proyecto.

---

# 3. Consensos principales

## 3.1 Información pública del negocio

Los cuatro SRS reconocen la necesidad de que LaundryDesk publique información del negocio, especialmente servicios, precios y horarios.

**Resolución:** se conserva como `RF-01 — Consultar información pública del negocio`.

---

## 3.2 Administrador único y protegido por autenticación

Las versiones coinciden en que el dueño será inicialmente el usuario administrador y que las funciones internas requieren protección mediante autenticación.

**Resolución:** se consolida como `RF-02` y se refuerza mediante `RNF-05`.

---

## 3.3 Registro de pedidos wash & fold

Todos los documentos consideran necesario registrar pedidos de wash & fold con información del cliente.

Existe una diferencia sobre quién inicia el registro, documentada posteriormente como conflicto.

**Resolución:** se conserva el registro del pedido como función central del MVP.

---

## 3.4 Código único de seguimiento

Todos los SRS incluyen un identificador o código que permite distinguir un pedido y utilizarlo para su seguimiento.

**Resolución:** se consolida como `RF-05` y se agrega la restricción de no utilizar una secuencia simple predecible en `RNF-03`.

---

## 3.5 Consulta del estado sin cuenta de cliente

Las cuatro versiones coinciden en que el cliente no debe crear una cuenta para consultar el avance de su pedido.

**Resolución:** se consolida como `RF-06` y `RD-05`.

---

## 3.6 Gestión administrativa de pedidos y estados

Todos los integrantes identificaron la necesidad de que el dueño pueda consultar pedidos y modificar su estado.

**Resolución:** se divide en `RF-07 — Consultar y filtrar pedidos` y `RF-08 — Gestionar el estado de un pedido` para mantener responsabilidades claras.

---

## 3.7 Servicios, precios y horarios editables

Todos los SRS incluyen, con distintos niveles de detalle, la posibilidad de mantener actualizada la información pública sin intervención de un desarrollador.

**Resolución:** se consolida en `RF-11`.

---

## 3.8 Exclusión de pagos en línea e integración con máquinas

Existe coincidencia en que la primera versión no procesará pagos en línea ni dependerá de sensores o integración con las máquinas físicas.

**Resolución:** ambas restricciones permanecen fuera del alcance del MVP.

---

# 4. Gaps identificados y decisiones

| Gap | Identificado principalmente por | Análisis | Propuesta de consolidación |
|---|---|---|---|
| Registrar peso y precio final después de crear el pedido | Colunga, Compañero 3, SVA; parcialmente Isai | Compatible con el proceso físico de recibir y pesar ropa | **Incluir** como RF-04 |
| Instrucciones especiales del pedido | Colunga, Compañero 3, SVA | Compatible y útil para la operación sin cambiar el alcance | **Incluir** dentro de RF-04 |
| Notas e incidencias | Isai y Colunga; relacionado con instrucciones en otros SRS | Ayuda a documentar daños, observaciones o situaciones excepcionales | **Incluir** como RF-09 |
| Corrección o reversión de estado | Isai, Colunga y SVA | Reduce errores operativos del administrador | **Incluir** como corrección manual explícita en RF-08 |
| Cancelación de pedidos | Isai, Colunga y SVA | Es compatible con wash & fold, aunque las reglas varían | **Incluir** solo antes de iniciar procesamiento; después requiere revisión manual |
| Retención/eliminación de datos después de un año | Isai y SVA | Compatible con privacidad; no afecta el flujo principal | **Incluir** como RD-07 con máximo de 12 meses |
| Compatibilidad móvil | SVA, Colunga y Compañero 3 | El dueño y clientes pueden utilizar celular | **Incluir** como RNF-04 |
| Disponibilidad mínima de 99 % | Isai y SVA | Medible y compatible con una aplicación web | **Incluir** como RNF-01 |
| Código no secuencial/predecible | SVA, Colunga y Compañero 3 | Mejora la protección de la consulta pública | **Incluir** como RNF-03, sin imponer longitud específica |
| Verificación del cliente con últimos cuatro dígitos de teléfono | Colunga | Mejora seguridad, pero añade fricción y no aparece como requisito común | **No incluir por ahora**; posible mejora posterior |
| Verificación de identidad al entregar | Colunga | No aparece como regla común ni en el proyecto base vigente | **No incluir por ahora**; pendiente de validación de negocio |
| Límite diario de pedidos y rechazo automático | Colunga | El valor y la regla no están confirmados en los demás SRS | **No incluir** en la línea base actual |
| Respaldo automático cada 24 horas y recuperación en 4 horas | SVA | Especificación técnica útil, pero no fue acordada por el resto | **No incluir** como obligación de esta línea base; puede revisarse en diseño técnico |
| Publicar promociones o mensajes informativos | SVA y Compañero 3 | El proyecto base vigente prioriza servicios, precios y horarios | **No incluir en MVP**; posible evolución posterior |

---

# 5. Conflictos identificados y resolución

## 5.1 Recolección a domicilio

### Diferencia

- **SVA:** incluye recolección en la primera versión, con agenda, capacidad, aprobación/rechazo y tarifas.
- **Compañero 3:** incluye solicitud de recolección, zona de cobertura y horarios.
- **Colunga:** establece explícitamente que la recolección no se ofrece todavía y la deja fuera de alcance.
- **Isai:** en la versión actualizada la recolección queda fuera del MVP y se considera una evolución futura.

### Resolución

Se adopta el alcance del `proyecto_base.md` vigente:

**La recolección y entrega a domicilio quedan fuera de la primera versión.**

Por lo tanto, se eliminan del SRS consolidado:

- Solicitud de recolección.
- Ventanas de recolección.
- Cobertura geográfica.
- Capacidad por ventana.
- Tarifas de recolección.
- Estados `Solicitado`, `Programado`, `Recolectado`, `Rechazado` y `No se encontró al cliente` cuando dependan específicamente de la recolección.

Se conserva como `RD-08` la posibilidad de incorporarla en una versión futura mediante una nueva revisión de requerimientos.

---

## 5.2 Quién registra el pedido de wash & fold

### Diferencia

- **Isai:** el administrador registra el pedido recibido físicamente.
- **Colunga:** el administrador registra el pedido nuevo.
- **SVA:** diferencia entre solicitudes en línea de recolección y pedidos registrados en mostrador.
- **Compañero 3:** permite que el cliente solicite wash & fold directamente desde la sección pública.

### Resolución

El `proyecto_base.md` actualizado indica que el nuevo servicio debe ser operado por el dueño y que el administrador registra los pedidos.

**La primera versión utilizará registro administrativo de pedidos.**

El cliente no crea el pedido desde el portal público; utiliza el portal para consultar información y posteriormente realizar seguimiento mediante código.

---

## 5.3 Notificaciones: SMS contra correo electrónico

### Diferencia

- **SVA:** propone SMS y correo, incluyendo reglas TCPA/10DLC.
- **Isai:** utiliza correo electrónico para el aviso de pedido listo.
- **Colunga:** propone evitar servicios externos con costo variable por uso y no depende de SMS.
- **Compañero 3:** no define un mecanismo de notificación específico.

### Resolución

Para reducir complejidad, costo y dependencias regulatorias:

**La primera versión utilizará correo electrónico únicamente cuando el pedido tenga un correo registrado.**

SMS queda fuera del MVP.

La falla del servicio de correo no podrá revertir el estado del pedido.

---

## 5.4 Flujo de estados

### Diferencia

Las versiones que incluyen recolección agregan estados como `Solicitado`, `Programado` y `Recolectado`. Colunga e Isai utilizan como núcleo de wash & fold el flujo `Recibido → En proceso → Listo → Entregado`.

### Resolución

Se establece como flujo normal oficial:

**Recibido → En proceso → Listo → Entregado**

`Cancelado` se conserva como estado excepcional.

Los estados propios de recolección se eliminan de esta versión.

---

## 5.5 Cálculo exacto del precio

### Diferencia

- **SVA:** especifica precio por libra, mínimo de 10 libras y ejemplos de cálculo.
- **Colunga:** establece que el precio depende del peso, pero reconoce reglas todavía no validadas.
- **Compañero 3:** permite registrar peso y precio final después de recibir la ropa.
- **Isai:** registra peso y precio pero no fija una fórmula específica.

### Resolución

Se conserva únicamente la regla compartida y verificable:

**El administrador puede registrar o actualizar peso y precio final.**

No se fija en esta línea base:

- Precio por libra específico.
- Mínimo de 10 libras.
- Fórmula automática de cálculo.

Estas reglas podrán incorporarse cuando sean confirmadas por el negocio.

---

## 5.6 Seguridad de la consulta pública

### Diferencia

- **Colunga:** exige ticket más últimos cuatro dígitos del teléfono y propone bloqueo por intentos fallidos.
- **SVA:** utiliza código de seguimiento y especifica un código no predecible.
- **Compañero 3:** utiliza código único y evita mostrar teléfono/dirección.
- **Isai:** utiliza código único y evita mostrar datos personales.

### Resolución

El MVP conservará la experiencia simple indicada por el proyecto:

**La consulta se realizará mediante el código de seguimiento, sin cuenta de usuario.**

Como controles mínimos:

- El código deberá ser único y no secuencial simple.
- La vista pública no mostrará datos personales.

La verificación con teléfono y los bloqueos de intentos se documentan como posibles mejoras de seguridad, no como obligación de la línea base actual.

---

## 5.7 Promociones

### Diferencia

SVA y Compañero 3 incluyen promociones o mensajes informativos. El SRS actualizado de Isai y el de Colunga priorizan servicios, precios y horarios, en concordancia con el proyecto base vigente.

### Resolución

Las promociones no se consideran indispensables para el MVP consolidado.

Se dejan fuera de esta línea base y podrán convertirse en una historia de usuario futura si el Product Owner las prioriza posteriormente.

---

# 6. Aportación de cada integrante al SRS consolidado

## 6.1 Aportaciones del SRS de Isai

Se tomaron principalmente:

- Alineación con el `proyecto_base.md` actualizado.
- Exclusión de recolección a domicilio del MVP.
- Registro administrativo del pedido.
- Flujo `Recibido → En proceso → Listo → Entregado`.
- Gestión de pedidos y filtrado.
- Notas e incidencias.
- Corrección manual de estados.
- Notificación por correo de pedido listo.
- Disponibilidad del 99 %.
- Conservación de datos por un máximo de 12 meses.

---

## 6.2 Aportaciones del SRS de SVA

Se tomaron principalmente:

- Separación clara entre portal público y panel administrativo.
- Importancia de una interfaz móvil.
- Código de seguimiento no predecible.
- Capacidad de actualizar información pública sin intervención del equipo de desarrollo.
- Corrección/reversión de errores de estado como necesidad operativa.
- Retención y depuración de datos personales después de un año.
- Criterios de aceptación detallados y verificables.

No se incorporaron sus reglas específicas de recolección, SMS, ventanas, tarifas y capacidad porque contradicen el alcance vigente.

---

## 6.3 Aportaciones del SRS de Colunga

Se tomaron principalmente:

- Exclusión explícita de recolección en la etapa actual.
- Registro administrativo de pedidos.
- Lista de pedidos activos.
- Registro posterior de peso y precio final.
- Notas asociadas al pedido.
- Cancelación antes del procesamiento.
- Corrección de estados marcados por error.
- Énfasis en privacidad del cliente.
- Código no secuencial.
- Interfaz pensada para uso desde celular.

No se incorporaron por falta de consenso el límite diario, la verificación con los últimos cuatro dígitos del teléfono, la verificación de identidad en la entrega y otras reglas marcadas en ese documento como supuestos pendientes de validar.

---

## 6.4 Aportaciones del SRS de Compañero 3

Se tomaron principalmente:

- Estructura clara de sección pública y administrativa.
- Registro de instrucciones especiales.
- Registro y actualización de peso y precio final.
- Protección de información personal durante el seguimiento.
- Compatibilidad móvil.
- Persistencia de los pedidos.
- Administración separada de servicios, precios y horarios.

No se incorporaron la solicitud de recolección ni sus reglas de cobertura y horario debido al cambio de alcance del proyecto base.

---

# 7. Resultado de la consolidación

La propuesta de consolidación produce una línea base común compuesta por:

- **12 requerimientos funcionales.**
- **6 requerimientos no funcionales.**
- **8 requerimientos de dominio.**
- **34 criterios de aceptación con identificadores consistentes.**

El principal conflicto fue el alcance de la recolección a domicilio. Se resolvió tomando como referencia el `proyecto_base.md` vigente y clasificando esta funcionalidad como evolución futura.

Los gaps compatibles con el nuevo alcance —como peso y precio posterior, notas, corrección de estados, compatibilidad móvil y conservación de datos— se incorporaron al SRS consolidado cuando agregaban valor sin contradecir el MVP.

Una vez que los integrantes validen estas resoluciones, `SRS_equipo.md` podrá establecerse como la fuente de verdad del equipo para las siguientes actividades del curso.
