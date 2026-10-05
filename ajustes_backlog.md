# Ajustes críticos al Product Backlog — LaundryDesk

**Fuente revisada:** `SRS_equipo.md`  
**Objetivo:** documentar los cambios realizados después de revisar críticamente las historias generadas a partir del SRS consolidado.

---

## 1. Criterios de revisión aplicados

La revisión buscó que cada historia:

- Entregara valor identificable para cliente o administrador.
- Tuviera un alcance suficientemente pequeño para poder estimarse.
- Mantuviera trazabilidad con el `SRS_equipo.md`.
- No introdujera funcionalidad fuera del MVP.
- Incluyera criterios de aceptación observables y verificables.
- No mezclara varias responsabilidades independientes dentro de una misma historia.
- Utilizara Story Points como medida relativa de complejidad y no como horas.

---

## 2. Ajustes generales realizados

1. Se eliminaron del backlog todas las historias relacionadas con recolección a domicilio, cobertura, ventanas de recolección, tarifas de recolección, SMS, pagos en línea e integración con máquinas, porque están fuera de la línea base actual.
2. Se definieron cuatro épicas para separar claramente experiencia pública, recepción de pedidos, operación interna y configuración del negocio.
3. Se separó la consulta de pedidos de su filtrado para evitar una historia excesivamente amplia.
4. Se separó la actualización normal de estados de la corrección manual de estados porque representan reglas y riesgos distintos.
5. Se separó la administración de servicios de la actualización de precios y horarios para generar historias más pequeñas y fáciles de estimar.
6. Se mantuvo la generación del código de seguimiento como historia independiente debido a sus requisitos de unicidad y no predictibilidad.
7. Se incorporaron en los criterios de aceptación las restricciones de privacidad, autenticación, integridad y persistencia relevantes del SRS.
8. Las prioridades se asignaron inicialmente según dependencia funcional y valor para poner en operación el flujo principal del wash & fold.

---

## 3. Revisión por historia

| Historia | Ajuste realizado durante la revisión | Resultado |
|---|---|---|
| **HU-01** | Se limitó a servicios activos, precios vigentes y horarios; no incluye promociones, máquinas ni recolección. | Historia enfocada en RF-01. |
| **HU-02** | Se agregó explícitamente privacidad ante consultas y comportamiento para código inválido. | Consulta pública verificable y segura. |
| **HU-03** | Se agregó el escenario de intento de acceso administrativo sin autenticación. | Cubre control de acceso, no solo login exitoso. |
| **HU-04** | Se estableció al administrador como quien registra el pedido, en lugar del cliente. | Alineada con el alcance definitivo del proyecto. |
| **HU-05** | Se separó de HU-04 porque peso, precio e instrucciones pueden conocerse después del registro inicial. | Reduce tamaño y dependencias de HU-04. |
| **HU-06** | Se mantuvo independiente por la regla de unicidad y no predictibilidad del código. | Facilita pruebas específicas de seguridad/trazabilidad. |
| **HU-07** | Se concentró únicamente en visualizar la lista consolidada. | Evita combinar consulta y filtros en una sola historia. |
| **HU-08** | Los filtros por estado y fecha se definieron como historia separada. | Puede implementarse después de la lista básica. |
| **HU-09** | Se restringieron las transiciones normales al flujo Recibido → En proceso → Listo → Entregado. | Criterio consistente con RD-01. |
| **HU-10** | La corrección de errores se separó del flujo normal y requiere confirmación explícita. | Reduce riesgo de cambios accidentales. |
| **HU-11** | Se especificó que las notas no modifican el estado y no son visibles públicamente. | Conserva trazabilidad interna y privacidad. |
| **HU-12** | Se precisó que la cancelación automática solo aplica en `Recibido`; estados posteriores requieren revisión manual. | Alineada con RD-04. |
| **HU-13** | Se enfocó en alta, modificación y desactivación de servicios. | Evita mezclar contenido de catálogo con precios/horarios. |
| **HU-14** | Se mantuvieron juntos precios y horarios por compartir el mismo propósito: información pública vigente. | Historia pequeña con valor inmediato para el negocio. |
| **HU-15** | Se añadió el escenario de falla del servicio de correo y el caso sin correo registrado. | Protege la integridad del pedido frente a dependencias externas. |

---

## 4. Revisión de estimaciones

Las historias de consulta o actualización simple se estimaron principalmente en **3 Story Points**. Las historias que implican formularios con persistencia, múltiples reglas de negocio, integración externa o manejo de estados se estimaron principalmente en **5 Story Points**.

No se asignaron historias de 8 o 13 puntos porque durante la revisión las funcionalidades grandes fueron divididas en historias más pequeñas. Si durante el refinamiento técnico alguna historia revela mayor complejidad o incertidumbre, el equipo deberá reestimarla antes de incorporarla a un Sprint.

---

## 5. Resultado de la revisión

El backlog final contiene:

- **4 épicas.**
- **15 historias de usuario.**
- **59 Story Points iniciales.**
- Al menos **2 criterios de aceptación por historia**.
- Prioridades Alta, Media o Baja según valor y dependencia.
- Trazabilidad directa con los requerimientos funcionales y no funcionales relevantes del `SRS_equipo.md`.

El backlog se considera listo para una primera sesión de refinamiento del equipo y para la creación posterior de Issues en GitHub Projects.
