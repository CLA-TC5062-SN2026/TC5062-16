"""
Lógica de negocio que no cabe en un serializer porque involucra reglas de
varias columnas a la vez o varias tablas (revision_sql.md, secciones 5 y 6).

Todo lo de aquí corre dentro de una sola transacción con
`transaction.atomic()`, y cada UPDATE que toca varias columnas relacionadas
(estado_actual + fecha_listo + fecha_cierre, por ejemplo) se hace en una
sola instrucción `.save(update_fields=[...])` o un solo `.update(...)`,
nunca en updates separados: PostgreSQL evalúa los CHECK por instrucción,
no por transacción, así que una secuencia de updates parciales podría
dejar una fila momentáneamente inválida y disparar el CHECK antes de
tiempo (ver revision_sql.md sección 5).
"""

import secrets
import string
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .exceptions import (
    PedidoAnonimizadoError,
    RequiereRevisionManualError,
    TransicionNoPermitidaError,
)
from .models import HistorialEstado, Notificacion, Pedido

_ALFABETO_CODIGO = string.ascii_uppercase + string.digits
_LONGITUD_CODIGO = 8

# Flujo normal de estados (revision_sql.md sección 6, punto 1).
_TRANSICIONES_NORMALES = {
    "RECIBIDO": {"EN_PROCESO", "CANCELADO"},
    "EN_PROCESO": {"LISTO", "CANCELADO"},
    "LISTO": {"ENTREGADO"},
    "ENTREGADO": set(),
    "CANCELADO": set(),
}

# Transiciones que SÍ pueden pasar, pero solo como corrección manual
# explícita (es_correccion=True, con confirmacion y motivo): por ejemplo
# reabrir un pedido cancelado por error, o retroceder un estado.
_TRANSICIONES_CORRECCION_PERMITIDA = {
    "CANCELADO": {"RECIBIDO", "EN_PROCESO"},
    "ENTREGADO": {"LISTO"},
    "LISTO": {"EN_PROCESO"},
    "EN_PROCESO": {"RECIBIDO"},
}


def generar_codigo_seguimiento():
    """Código corto, impredecible (secrets, no random), para que un
    cliente no pueda adivinar el código de otro pedido (revision_sql.md
    sección 6, punto 2: el código debe ser difícil de adivinar, no solo
    único)."""
    for _ in range(20):
        codigo = "".join(
            secrets.choice(_ALFABETO_CODIGO) for _ in range(_LONGITUD_CODIGO)
        )
        if not Pedido.objects.filter(codigo_seguimiento=codigo).exists():
            return codigo
    # Prácticamente imposible con 36**8 combinaciones, pero cubre el caso.
    raise RuntimeError("No se pudo generar un código de seguimiento único.")


def normalizar_telefono(telefono):
    return "".join(ch for ch in telefono if not ch.isspace() and ch != "-")


@transaction.atomic
def cambiar_estado(
    pedido,
    estado_nuevo,
    administrador_id,
    es_correccion=False,
    confirmacion=False,
    motivo="",
):
    """Aplica el cambio de estado de un pedido según las reglas de
    PUT /pedidos/{pedido_id}/estado.

    Devuelve la fila de HistorialEstado creada. Lanza:
    - PedidoAnonimizadoError (409) si el pedido ya fue anonimizado.
    - TransicionNoPermitidaError (409) si la transición no es válida ni
      en flujo normal ni como corrección.
    - RequiereRevisionManualError (409) si se intenta CANCELADO desde un
      estado que no es parte del flujo normal de cancelación y no se
      marcó es_correccion (para no cancelar "por accidente" algo que ya
      iba avanzado).
    """
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)

    if pedido.anonimizado:
        raise PedidoAnonimizadoError()

    estado_anterior = pedido.estado_actual

    # Idempotencia (PUT): pedir el mismo estado que ya tiene no es un
    # error, simplemente no hace nada y se reporta sin crear historial
    # nuevo (revision_sql.md sección 6, punto 3).
    if estado_nuevo == estado_anterior:
        ultimo = pedido.historial.order_by("-fecha_cambio").first()
        return ultimo

    permitido_normal = estado_nuevo in _TRANSICIONES_NORMALES.get(estado_anterior, set())
    permitido_correccion = estado_nuevo in _TRANSICIONES_CORRECCION_PERMITIDA.get(
        estado_anterior, set()
    )

    if not permitido_normal and not permitido_correccion:
        raise TransicionNoPermitidaError(
            f"No se puede pasar de {estado_anterior} a {estado_nuevo}."
        )

    if permitido_correccion and not permitido_normal:
        # Es una transición que solo tiene sentido como corrección manual
        # (por ejemplo, reabrir un pedido CANCELADO o ENTREGADO).
        if not (es_correccion and confirmacion and motivo and motivo.strip()):
            raise RequiereRevisionManualError(
                "Esa transición requiere es_correccion=true, confirmacion=true y un motivo."
            )

    ahora = timezone.now()
    campos_a_actualizar = {"estado_actual": estado_nuevo}

    if estado_nuevo == "LISTO":
        campos_a_actualizar["fecha_listo"] = ahora
    if estado_nuevo in ("ENTREGADO", "CANCELADO"):
        campos_a_actualizar["fecha_cierre"] = ahora
    # Corrección que regresa un pedido a un estado anterior al de "listo"
    # o "cerrado": limpiar las fechas que ya no aplican, en la MISMA
    # instrucción UPDATE (no en una aparte) para no violar momentáneamente
    # ningún CHECK que relacione estado_actual con esas fechas.
    if es_correccion:
        if estado_nuevo not in ("LISTO", "ENTREGADO"):
            campos_a_actualizar["fecha_listo"] = None
        if estado_nuevo != "ENTREGADO" and estado_nuevo != "CANCELADO":
            campos_a_actualizar["fecha_cierre"] = None

    for campo, valor in campos_a_actualizar.items():
        setattr(pedido, campo, valor)
    pedido.save(update_fields=list(campos_a_actualizar.keys()))

    historial = HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        es_correccion=es_correccion,
        motivo=motivo or None,
        administrador_id=administrador_id,
    )

    # Patrón outbox (revision_sql.md sección 5): nunca se envía el correo
    # aquí mismo, solo se deja la intención registrada en `notificacion`
    # para que un proceso aparte (fuera de alcance de este entregable) la
    # envíe y actualice su estado_envio.
    if estado_nuevo == "LISTO" and pedido.email_cliente:
        Notificacion.objects.create(
            pedido=pedido,
            canal="CORREO",
            destinatario=pedido.email_cliente,
            estado_envio="PENDIENTE",
        )

    return historial


def fecha_limite_retencion():
    """12 meses de retención (RD-07): un pedido con fecha_cierre anterior
    a esto es candidato a anonimización. No se usa en los endpoints de
    este entregable (no hay un job programado todavía), pero queda listo
    para quien lo implemente."""
    return timezone.now() - timedelta(days=365)
