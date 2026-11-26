# Retrospectiva del proyecto — LaundryDesk

## Sección A — Retrospectiva SCRUM

### ¿Qué salió bien?

Uno de los principales aciertos del proyecto fue que el equipo logró transformar un problema operativo relativamente abierto en una arquitectura funcional y separada por responsabilidades.

A lo largo de las iteraciones se consolidaron el SRS, el Product Backlog, el esquema de datos, el contrato de API, el backend y el frontend. En particular, la separación entre frontend, capa de servicios, API REST, lógica de negocio y persistencia permitió desarrollar y revisar cada parte con cierta independencia.

También fue positivo que varias decisiones técnicas quedaran explícitas. Ejemplos de ello son el uso de React y Vite en frontend, Django REST Framework en backend, PostgreSQL para persistencia, JWT para autenticación y Fetch centralizado mediante `api.js`.

Las verificaciones realizadas durante las últimas iteraciones también permitieron encontrar problemas que no eran evidentes durante la generación inicial del código. El script `verify:servicios`, las pruebas manuales de autenticación, el análisis estático y el Code Review ayudaron a comprobar comportamientos concretos en vez de asumir que el código generado funcionaba.

Otro resultado positivo fue utilizar ramas de trabajo para aislar cambios y refactorizaciones antes de proponer su integración a `main`. Esto permitió revisar modificaciones como H11, H8 y H7 sin alterar directamente la versión principal utilizada por el equipo.

---

### ¿Qué no salió bien?

El problema más importante no estuvo únicamente en el código, sino en la consistencia de los artefactos construidos durante el proyecto.

Durante varias semanas los entregables se almacenaron principalmente como archivos ZIP. Esto dificultó comparar versiones y detectar cuándo un documento dejó de corresponder con otro.

También existieron diferencias entre documentos que inicialmente parecían válidos por separado. Por ejemplo, el esquema SQL original del proyecto no contiene la columna `email` que posteriormente utiliza el modelo `Administrador`. Debido a que los modelos utilizan `managed = False`, Django no crea automáticamente esa columna, por lo que una instalación desde cero utilizando únicamente una versión antigua del esquema puede presentar problemas con el flujo de autenticación.

Otro ejemplo fue la consolidación del SRS. Los identificadores de requerimientos cambiaron de significado entre documentos y algunas decisiones de negocio no quedaron incorporadas de manera uniforme en todos los artefactos.

También se encontraron divergencias entre el contrato de API y la implementación, por ejemplo en algunos filtros del listado de pedidos y en determinadas formas de respuesta.

Finalmente, el alcance implementado quedó desbalanceado entre backend y frontend. El backend contiene gran parte de la lógica necesaria para registrar pedidos, modificar estados, registrar notas y administrar servicios y horarios, pero varias de estas operaciones todavía no cuentan con una interfaz gráfica.

---

### ¿Qué haríamos diferente la próxima vez?

Desde el inicio utilizaríamos el repositorio Git como la fuente principal de los artefactos del proyecto y evitaríamos entregar versiones sucesivas únicamente dentro de archivos ZIP.

También mantendríamos una matriz de trazabilidad viva desde las primeras semanas:

`Requerimiento → Historia de usuario → Contrato → Implementación → Prueba`

La matriz se actualizaría dentro del mismo sprint en que cambia cualquiera de sus elementos.

Añadiríamos a la Definition of Done una prueba de instalación desde cero. Al cierre de cada sprint, una persona distinta debería clonar el repositorio en un entorno limpio y levantar el sistema utilizando únicamente el README. Si se requiere un paso que no se encuentra documentado, la historia todavía no debería considerarse completamente terminada.

También realizaríamos una revisión periódica de consistencia entre `SRS_equipo.md`, el contrato de API, el esquema SQL y los modelos/serializers. Los linters comprueban propiedades de archivos individuales, pero no pueden determinar si diferentes artefactos describen exactamente el mismo sistema.

Por último, priorizaríamos antes los flujos verticales completos. En lugar de implementar muchas operaciones únicamente en backend, sería preferible completar primero un conjunto pequeño de historias desde la interfaz hasta la base de datos y sus pruebas.

---

### Uso de herramientas y agentes de IA durante el proyecto

Los agentes de IA fueron especialmente útiles en actividades de comparación de alternativas, generación de scaffolding, revisión de código, documentación, interpretación de resultados de herramientas y propuestas de refactorización.

También ayudaron a acelerar tareas repetitivas, como transformar hallazgos de un Code Review en propuestas concretas de cambio o generar primeras versiones de documentos técnicos.

Sin embargo, también generaron trabajo adicional cuando no tenían acceso a la misma versión del proyecto que estaba utilizando el equipo. En algunos momentos fue necesario localizar nuevamente la versión correcta del frontend o backend y validar cada propuesta contra el código real.

Esto cambió la forma de utilizar IA durante el desarrollo. En las últimas actividades dejamos de considerar una respuesta del agente como un resultado terminado y comenzamos a tratarla como una propuesta que debía validarse mediante:

- inspección del archivo real;
- `git diff`;
- compilación;
- pruebas o scripts de verificación;
- comparación contra SRS, contrato y esquema.

La principal lección es que la IA fue más útil como asistente de análisis, documentación y revisión que como sustituto de la verificación técnica.

---

## Sección B — Consistencia problema-solución

### ¿La aplicación construida resuelve el problema planteado?

La solución construida resuelve parcialmente el problema original.

LaundryDesk buscaba evitar que el control de pedidos de wash & fold dependiera de la memoria del personal y reducir las llamadas de clientes preguntando por el estado de su ropa.

El backend construido representa los conceptos principales del negocio:

- pedidos;
- código de seguimiento;
- estados e historial;
- notas;
- servicios;
- horarios;
- autenticación administrativa;
- registro de solicitudes de notificación.

Además, el backend cuenta con una consulta pública de seguimiento mediante código.

Sin embargo, en la versión final de `main`, la pantalla pública todavía utiliza una respuesta simulada y no consume directamente el endpoint real de seguimiento. Por ello, esta funcionalidad se considera parcialmente implementada de extremo a extremo.

El área administrativa sí permite autenticarse y visualizar la lista de pedidos utilizando información obtenida del backend.

Por lo tanto, existe evidencia concreta de que la arquitectura permite centralizar la información del pedido y proporciona la base técnica necesaria para ofrecer seguimiento al cliente.

Sin embargo, el producto todavía no cubre toda la operación definida en el SRS desde la interfaz gráfica.

---

### ¿Qué partes del problema original no logra resolver todavía?

La principal limitación es que varias capacidades implementadas en la API todavía no son accesibles desde una pantalla administrativa.

Actualmente faltan interfaces para:

- registrar nuevos pedidos;
- completar o modificar peso, precio e instrucciones;
- cambiar o corregir estados;
- registrar notas e incidencias;
- cancelar pedidos;
- administrar servicios y horarios.

Tampoco existe todavía el proceso que envía físicamente los correos. El backend registra una notificación como `PENDIENTE` cuando corresponde, pero el componente encargado de procesarla y realizar el envío quedó fuera de la implementación final.

También queda pendiente la anonimización automática de datos personales después del periodo de retención.

Existen además obstáculos técnicos y documentales que deben cerrarse antes de considerar al producto listo para una instalación nueva, entre ellos la diferencia histórica entre el esquema SQL y el modelo actual de Django.

Finalmente, el proyecto no cuenta con una URL pública de producción documentada ni con un conjunto amplio de pruebas automatizadas end-to-end.

---

### ¿Quedaron fuera del alcance o son obstáculos técnicos?

Hay una combinación de ambas situaciones.

Algunas funciones fueron excluidas deliberadamente del MVP, por ejemplo:

- pagos en línea;
- recolección y entrega a domicilio;
- SMS;
- múltiples empleados con diferentes roles.

Estas funciones no representan deuda respecto al alcance acordado.

En cambio, las pantallas administrativas faltantes, el envío efectivo de correo, la anonimización automática de información, las divergencias contrato-backend y las inconsistencias de instalación sí representan trabajo pendiente dentro del alcance o deuda técnica acumulada.

Esta diferencia es importante: una funcionalidad explícitamente excluida del MVP no debe considerarse un defecto, mientras que una funcionalidad incluida en el SRS pero implementada únicamente de forma parcial sí debe registrarse como trabajo pendiente.

---

### ¿Qué demostraríamos primero al stakeholder?

La primera demostración estaría relacionada con el flujo central de un pedido.

Comenzaríamos mostrando el inicio de sesión administrativo y la consulta del listado de pedidos, demostrando que la información de la operación puede mantenerse centralizada y protegida mediante autenticación.

Posteriormente utilizaríamos la API para demostrar el registro de un pedido, la generación automática de su código de seguimiento, la actualización de sus datos y los cambios controlados de estado.

También mostraríamos el endpoint público de seguimiento utilizando un código real generado por el sistema, aclarando que la integración de esta consulta con la pantalla pública todavía está pendiente en la versión final de `main`.

Finalmente, demostraríamos un caso de error controlado, como una transición de estado no permitida o un acceso administrativo sin autenticación.

El orden de la demostración busca comenzar por el valor observable para el negocio y después mostrar las capacidades técnicas que respaldan el flujo completo.

---

## Conclusión

LaundryDesk alcanzó una base técnica funcional, especialmente en el backend, la autenticación administrativa y la gestión de pedidos mediante API.

La mayor lección del proyecto no fue únicamente aprender a construir código, sino reconocer que la calidad de un sistema también depende de mantener consistentes sus artefactos.

Un archivo puede ser correcto de manera aislada y aun así describir un sistema incompatible con el resto del proyecto.

Por ello, en una siguiente iteración incorporaríamos formalmente la trazabilidad, la instalación desde cero y la comparación entre requerimientos, contrato, esquema y código como actividades de cierre de cada sprint.