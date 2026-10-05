# Priorización comparada — LaundryDesk

**Backlog analizado:** `backlog_completo.md` (15 historias, 4 épicas)
**Fuentes de la priorización propia:** entrevista con el cliente real y su
ronda de seguimiento posterior
**Objetivo:** contrastar la priorización propuesta por el agente en rol de
Product Owner con la priorización derivada del contacto directo con el
stakeholder.

---

## 1. Priorización del agente

Se solicitó al agente adoptar el rol de Product Owner y ordenar las 15
historias por valor de negocio. Su criterio rector fue el flujo de valor
definido en el SRS: registro → código → procesamiento → estado → consulta
del cliente → aviso → entrega, colocando arriba las historias que forman ese
flujo según su dependencia mutua, y abajo las que atienden excepciones o
aportan comodidad, por considerar que tienen alternativa manual mientras el
volumen sea bajo.

| # | HU | Historia |
|---|---|---|
| 1 | HU-03 | Iniciar sesión como administrador |
| 2 | HU-04 | Registrar un pedido de wash & fold |
| 3 | HU-06 | Generar código único de seguimiento |
| 4 | HU-07 | Consultar la lista de pedidos |
| 5 | HU-09 | Actualizar el estado normal del pedido |
| 6 | HU-02 | Consultar el estado de un pedido (cliente) |
| 7 | HU-05 | Completar peso, precio final e instrucciones |
| 8 | HU-15 | Notificar por correo cuando el pedido esté listo |
| 9 | HU-01 | Consultar servicios, precios y horarios |
| 10 | HU-14 | Actualizar precios y horarios |
| 11 | HU-10 | Corregir un estado registrado por error |
| 12 | HU-12 | Cancelar un pedido antes de procesarlo |
| 13 | HU-11 | Registrar notas e incidencias |
| 14 | HU-08 | Filtrar pedidos |
| 15 | HU-13 | Administrar los servicios ofrecidos |

El agente propuso además que las historias 1 a 8 constituyeran el corte de un
primer incremento utilizable, y señaló por iniciativa propia que HU-01 y
HU-14 están etiquetadas como prioridad Alta en el backlog pese a quedar
fuera de ese corte.

---

## 2. Priorización propia

La priorización propia parte de un insumo que el agente no tenía: la
entrevista con el dueño del negocio. En ella el stakeholder indicó que
concibe el sistema como una herramienta de operación interna más que como
software de cara al cliente, que lo imprescindible para arrancar es registrar
pedidos, conservar su historial y notificar al cliente, y que el sistema
perdería su confianza si informara que un pedido está listo cuando no lo
está.

| # | HU | Historia | Posición del agente |
|---|---|---|---|
| 1 | HU-03 | Iniciar sesión como administrador | 1 |
| 2 | HU-04 | Registrar un pedido de wash & fold | 2 |
| 3 | HU-06 | Generar código único de seguimiento | 3 |
| 4 | HU-05 | Completar peso, precio final e instrucciones | 7 |
| 5 | HU-07 | Consultar la lista de pedidos | 4 |
| 6 | HU-09 | Actualizar el estado normal del pedido | 5 |
| 7 | HU-15 | Notificar cuando el pedido esté listo | 8 |
| 8 | HU-10 | Corregir un estado registrado por error | 11 |
| 9 | HU-11 | Registrar notas e incidencias | 13 |
| 10 | HU-12 | Cancelar un pedido antes de procesarlo | 12 |
| 11 | HU-08 | Filtrar pedidos | 14 |
| 12 | HU-02 | Consultar el estado de un pedido (cliente) | 6 |
| 13 | HU-01 | Consultar servicios, precios y horarios | 9 |
| 14 | HU-14 | Actualizar precios y horarios | 10 |
| 15 | HU-13 | Administrar los servicios ofrecidos | 15 |

---

## 3. Dónde coinciden las dos priorizaciones

Ambas colocan en los tres primeros lugares la autenticación, el registro del
pedido y la generación del código de seguimiento, y por la misma razón: son
habilitadores sin los cuales ninguna otra historia puede ejecutarse. También
coinciden en que la administración del catálogo de servicios (HU-13) es lo
menos urgente, dado que el catálogo de wash & fold es pequeño, estable y
puede precargarse.

La coincidencia en estos extremos sugiere que, cuando la decisión depende de
dependencias funcionales verificables en el documento, la priorización del
agente es confiable.

---

## 4. Dónde difieren y por qué

### 4.1 HU-02, consulta pública del estado: del lugar 6 al 12

Es la diferencia más grande y la más significativa. El agente la coloca sexta
porque el SRS la presenta como el valor principal para el cliente final, y la
describe como la historia que cierra el primer incremento utilizable de punta
a punta. Sin embargo, el stakeholder declaró explícitamente que piensa en una
operación interna y no en un sistema de cara al cliente, y que lo que
resuelve su problema es el aviso automático, no que el cliente consulte.

La consulta pública no se elimina, porque forma parte del alcance acordado
por el equipo, pero deja de ser parte del primer incremento.

### 4.2 HU-15, notificación al cliente: del lugar 8 al 7

El agente ubica la notificación después de la consulta pública con un
argumento explícito: HU-02 ya cubre la necesidad en modalidad "pull", de modo
que la notificación es la mejora "push". Esa jerarquía es exactamente la
inversa de la que expresó el stakeholder. Para él, la notificación es la
función principal y la consulta es secundaria; de hecho, definió como
criterio de éxito del sistema que, tras algunas semanas de operación, no
hubiera pedidos perdidos ni clientes sin notificar.

### 4.3 HU-05, peso y precio final: del lugar 7 al 4

El agente la baja argumentando que el SRS permite capturar estos datos
después del registro inicial (RD-03), lo cual da margen temporal, y asume que
el cobro ocurre al entregar el pedido. El cliente real indicó que el cobro
ocurre al inicio del servicio y que el precio se calcula por libra al recibir
la ropa. Si el precio se conoce y se cobra en el mostrador, no es un dato
diferible, sino parte del registro.

Esta diferencia revela además que RD-03 del SRS contradice lo que el cliente
describió, y que el equipo deberá corregirlo.

### 4.4 HU-10, corregir un estado registrado por error: del lugar 11 al 8

El agente identifica correctamente el riesgo —señala que un "Listo" falso
dispararía un correo falso— pero concluye que, por ser un caso poco
frecuente, pertenece al grupo de excepciones. El stakeholder identificó
precisamente ese escenario como su criterio de fracaso: que el sistema
informe que un pedido está listo cuando no se ha procesado. Por la misma
razón solicitó una confirmación doble antes de marcar un pedido como "Listo".

La frecuencia de un fallo no es el único criterio para priorizarlo; su
consecuencia también cuenta. Una función que previene el escenario que el
cliente considera inaceptable no puede tratarse como comodidad.

### 4.5 HU-11, notas e incidencias: del lugar 13 al 9

El agente considera que el campo de instrucciones especiales de HU-05 cubre
parcialmente esta necesidad y que las incidencias no bloquean el flujo. El
cliente mencionó que el negocio cuenta con una política de reembolso para
prendas dañadas o extraviadas, lo que convierte el registro de incidencias en
el respaldo documental de esa política, y no en una anotación opcional.

### 4.6 HU-01 y HU-14, información pública: de los lugares 9 y 10 a los 13 y 14

El agente ya había señalado que ambas están sobrevaloradas en el backlog. La
entrevista refuerza esa lectura por dos motivos: el negocio ya mantiene
presencia en línea mediante una página de Facebook y una ficha de Google
Maps, y el propio dueño indicó que los precios y horarios cambian con muy
poca frecuencia.

Cabe señalar que el agente justificó esta posición afirmando que el negocio
comunica hoy esa información "por letrero, teléfono y redes". Los letreros no
aparecen en ninguna fuente del proyecto; los canales confirmados por el
cliente son una página de Facebook y una ficha de Google Maps,
desactualizadas. La conclusión del agente es correcta, pero la sustenta en un
dato que no verificó.

---

## 5. Lectura del contraste

La priorización del agente es internamente consistente y correcta respecto a
su única fuente de información, que es el SRS consolidado. Su criterio es la
dependencia funcional: ordena las historias según lo que debe existir antes de
que otra cosa pueda funcionar, y en eso no comete errores.

La priorización propia difiere porque incorpora una fuente que el documento no
contiene: lo que el stakeholder considera valioso. Las dos listas se separan
precisamente en las historias donde el valor de negocio no puede deducirse de
la especificación, sino que depende de cómo opera el negocio y de qué le
preocupa al dueño.

El caso más claro es la pareja HU-02 y HU-15. El agente razona que la consulta
cubre la necesidad y la notificación la mejora; el cliente sostiene lo
contrario. Ninguna de las dos lecturas puede derivarse del SRS, porque el
documento describe ambas funciones sin indicar cuál resuelve el problema
central del negocio. El agente eligió una interpretación razonable y resultó
ser la equivocada.

De aquí se desprende una limitación concreta del uso de un agente como Product
Owner: puede ordenar correctamente por dependencia, pero no puede priorizar
por valor, porque el valor no está en el documento. En este caso, colocó en el
sexto lugar una función que el cliente no considera necesaria, y en el
undécimo una que previene el escenario que el cliente describió como
inaceptable.

Un segundo riesgo observado es que el agente completa con supuestos los vacíos
de información, como ocurrió con los canales de comunicación del negocio, sin
distinguir entre lo que el documento afirma y lo que él infiere.

---

## 6. Acciones derivadas

1. Reclasificar HU-01 y HU-14 de prioridad Alta a Media en
   `backlog_completo.md`, conforme a lo señalado tanto por el agente como por
   la entrevista.
2. Elevar HU-10 y HU-11 de Media a Alta, por su relación con el criterio de
   fracaso declarado por el cliente y con la política de reembolso del
   negocio.
3. Registrar como pendiente la corrección de RD-03 en `SRS_equipo.md`, dado
   que el momento del cobro declarado por el cliente contradice la regla
   vigente.
4. Someter a discusión del equipo el descenso de HU-02, por tratarse de una
   historia incluida en el alcance acordado por todos.
5. Documentar en la definición del sprint el supuesto de datos precargados que
   el agente identificó: HU-04 requiere un catálogo de servicios y HU-01
   requiere información que mostrar, y ambos pueden resolverse con datos
   iniciales sin adelantar HU-13 ni HU-14.