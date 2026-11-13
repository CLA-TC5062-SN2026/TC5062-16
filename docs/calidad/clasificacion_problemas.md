# Clasificación de problemas de calidad de código

## 1. Objetivo

Se realizó un análisis estático del backend de LaundryDesk con el propósito de identificar problemas potenciales de calidad, mantenibilidad, tipado y estructura antes de realizar el Code Review y la evaluación de principios SOLID.

Se utilizaron las siguientes herramientas:

- **Pylint**, con soporte para Django mediante `pylint-django`.
- **Mypy**, configurado con `django-stubs` y `djangorestframework-stubs`.

La salida completa de ambas herramientas se almacenó en:

`output_linter.txt`

## 2. Resultado general

Pylint evaluó el backend con una calificación de:

**8.91 / 10**

Mypy, después de configurar correctamente los plugins para Django y Django REST Framework, encontró:

**4 errores en 2 archivos, después de revisar 19 archivos fuente.**

Durante una primera ejecución, Mypy reportó 55 errores. Sin embargo, la mayoría correspondían a campos del ORM de Django que la herramienta no interpretaba correctamente debido a que todavía no se habían configurado los plugins específicos del framework.

Una vez realizada la configuración adecuada, dichos resultados desaparecieron.

Esto demuestra que los resultados de una herramienta de análisis estático deben interpretarse antes de considerarse defectos reales del software.

---

# 3. Problemas críticos

## No se identificaron problemas críticos mediante el análisis estático

No se encontraron evidencias directas de:

- Inyección SQL.
- Credenciales o secretos expuestos.
- Imports rotos.
- Uso de variables inexistentes.
- Errores de sintaxis.
- Vulnerabilidades de seguridad evidentes.
- Errores que necesariamente provoquen la caída del sistema.

Esto no significa que el sistema esté libre de defectos, sino que las herramientas utilizadas no detectaron un problema que pudiera clasificarse como crítico en esta etapa.

---

# 4. Problemas importantes

## 4.1 Manejador de excepciones con demasiados caminos de salida

**Archivo:** `api/exceptions.py`  
**Línea aproximada:** 109  
**Regla Pylint:** `R0911 - too-many-return-statements`

Pylint detectó que la función central de manejo de excepciones contiene más instrucciones `return` de las recomendadas.

### Motivo

La función concentra el tratamiento de diferentes tipos de errores:

- Errores propios del negocio.
- Errores de validación.
- Errores de autenticación.
- Recursos no encontrados.
- Errores de integridad.
- Errores internos.

Aunque actualmente la función es comprensible, agregar nuevos tipos de error puede incrementar progresivamente su complejidad.

### Riesgo

- Mayor dificultad de mantenimiento.
- Mayor cantidad de caminos de ejecución.
- Mayor dificultad para realizar pruebas unitarias.
- Posible incumplimiento del principio de responsabilidad única.

### Clasificación

**Importante – Mantenibilidad**

---

## 4.2 Función de cambio de estado con demasiados argumentos

**Archivo:** `api/services.py`  
**Línea aproximada:** 72  
**Reglas Pylint:**

- `R0913 - too-many-arguments`
- `R0917 - too-many-positional-arguments`

La función encargada del cambio de estado de un pedido recibe seis argumentos.

### Motivo

Una cantidad elevada de parámetros puede indicar que una función está comenzando a manejar demasiada información o responsabilidades.

También aumenta la posibilidad de utilizar incorrectamente parámetros posicionales al invocarla.

### Riesgo

- Menor legibilidad.
- Mayor acoplamiento.
- Mayor dificultad para extender la operación.
- Mayor probabilidad de errores durante futuras modificaciones.

### Posible mejora

En una iteración posterior podría evaluarse agrupar la información relacionada con la operación en un objeto, DTO o estructura específica.

### Clasificación

**Importante – Diseño y mantenibilidad**

---

## 4.3 Pérdida de contexto al transformar excepciones

**Archivo:** `api/views.py`  
**Líneas aproximadas:** 173, 214 y 234  
**Regla Pylint:** `W0707 - raise-missing-from`

Se encontraron bloques donde una excepción `IntegrityError` es capturada y posteriormente reemplazada por una excepción específica del dominio.

Ejemplo conceptual:

```python
except IntegrityError:
    raise NombreServicioDuplicadoError()
```

### Motivo

Al generar una nueva excepción sin utilizar `from`, se dificulta identificar cuál fue la excepción original que provocó el problema.

Una implementación más adecuada sería:

```python
except IntegrityError as exc:
    raise NombreServicioDuplicadoError() from exc
```

### Beneficio

La API puede seguir entregando un error de negocio comprensible para el usuario mientras que el servidor conserva información útil para:

- Logs.
- Debugging.
- Soporte.
- Análisis de incidentes.

### Clasificación

**Importante – Trazabilidad y mantenibilidad**

---

## 4.4 Obtención dinámica de `choices` no segura para el analizador de tipos

**Archivo:** `api/serializers.py`  
**Línea:** 347  
**Herramienta:** Mypy  
**Regla:** `union-attr`

El código obtiene dinámicamente las opciones de estado mediante información interna del modelo.

Mypy indica que el atributo `choices` podría ser `None`.

### Motivo

Django permite acceder dinámicamente a los metadatos de un modelo, pero el sistema de tipos no puede garantizar que el campo obtenido siempre tenga opciones.

### Riesgo

El comportamiento actual puede funcionar correctamente en tiempo de ejecución, pero:

- El tipado no puede verificarlo.
- Existe mayor dependencia de los metadatos internos del modelo.
- La intención del código es menos explícita.

### Posible mejora

El proyecto ya define una colección explícita de estados permitidos en `models.py`, por lo que podría reutilizarse directamente esa constante en el serializer.

### Clasificación

**Importante – Tipado y mantenibilidad**

---

## 4.5 Estado opcional de la paginación según los tipos de DRF

**Archivo:** `api/pagination.py`  
**Líneas:** 23–25  
**Herramienta:** Mypy

Mypy reportó tres situaciones:

- `self.page` podría ser `None` antes de acceder a `paginator`.
- `self.page` podría ser `None` antes de acceder a `number`.
- `self.request` podría ser `None` al enviarse a `get_page_size()`.

### Motivo

Django REST Framework normalmente inicializa estas propiedades antes de ejecutar `get_paginated_response()`.

Sin embargo, el contrato de tipos de DRF declara dichas propiedades como opcionales, por lo que Mypy no puede garantizar que siempre tengan un valor.

### Riesgo

No se ha demostrado un fallo real en ejecución, pero el código depende de una precondición implícita del ciclo de vida de DRF.

### Posible mejora

Hacer explícita dicha precondición mediante validaciones, variables locales correctamente tipadas o técnicas compatibles con el framework.

### Clasificación

**Importante – Robustez del tipado**

---

# 5. Problemas menores

## 5.1 Falta de docstrings

**Reglas Pylint:**

- `C0114 - missing-module-docstring`
- `C0115 - missing-class-docstring`
- `C0116 - missing-function-docstring`

Se encontraron múltiples módulos, clases y funciones sin documentación mediante docstrings.

### Motivo

No afecta directamente el funcionamiento del sistema, pero reduce la facilidad para comprender rápidamente las responsabilidades de cada componente.

### Clasificación

**Menor – Documentación**

---

## 5.2 Líneas mayores al límite definido

**Regla Pylint:** `C0301 - line-too-long`

Algunas líneas superan el límite configurado de 100 caracteres.

### Motivo

Es principalmente un problema de legibilidad y estilo.

### Clasificación

**Menor – Estilo**

---

## 5.3 Comparación que puede simplificarse

**Archivo:** `api/services.py`  
**Regla Pylint:** `R1714 - consider-using-in`

Una condición compara una variable individualmente contra diferentes valores.

Puede expresarse de forma más compacta utilizando `in` o `not in`.

Ejemplo:

```python
estado_nuevo not in ("ENTREGADO", "CANCELADO")
```

### Motivo

La modificación mejora legibilidad pero no cambia el comportamiento del sistema.

### Clasificación

**Menor – Legibilidad**

---

## 5.4 Importación dentro de un método

**Archivo:** `api/views.py`  
**Línea aproximada:** 364  
**Regla Pylint:** `C0415 - import-outside-toplevel`

Se encontró una excepción importada dentro de un método.

### Motivo

En este caso no parece existir una necesidad clara de realizar una importación diferida.

Moverla junto con el resto de imports del módulo haría más visibles las dependencias.

### Clasificación

**Menor – Organización del código**

---

# 6. Hallazgos contextuales y falsos positivos

Durante el análisis se identificaron algunos resultados que no necesariamente representan defectos reales.

## Serializers sin métodos `create()` y `update()`

Pylint reportó `W0223` en serializers utilizados principalmente para validar información de entrada, como:

- Login.
- Registro de administrador.
- Cambio de estado.

Estos serializers no necesariamente tienen la responsabilidad de crear o actualizar directamente un modelo.

Por ello, el hallazgo se considera:

**Contextual / posible falso positivo del análisis de Pylint sobre DRF.**

---

## Import dentro de `manage.py`

Pylint detectó una importación fuera del nivel superior en `manage.py`.

Este comportamiento forma parte de la estructura habitual generada por Django para ejecutar comandos administrativos.

No se considera necesaria una modificación únicamente para satisfacer al linter.

**Clasificación: contextual / aceptado.**

---

# 7. Conclusión

El backend presenta en general una calidad estática adecuada, reflejada también en la calificación de **8.91/10 obtenida con Pylint**.

No se encontraron problemas críticos mediante las herramientas utilizadas.

Los principales hallazgos se relacionan con:

1. Complejidad del manejador central de excepciones.
2. Cantidad de parámetros utilizados en el servicio de cambio de estado.
3. Conservación de la causa original de excepciones.
4. Uso de estructuras dinámicas difíciles de comprobar mediante tipado estático.
5. Precondiciones implícitas dentro de la paginación de Django REST Framework.

Los problemas menores corresponden principalmente a documentación, estilo y legibilidad.

También se comprobó que una herramienta de análisis estático puede generar falsos positivos si no está configurada específicamente para el framework utilizado. Por esta razón fue necesario configurar Mypy con soporte para Django y Django REST Framework antes de considerar sus resultados como evidencia válida.
