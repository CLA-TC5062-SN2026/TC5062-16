"""
Manejador de excepciones centralizado.

openapi_equipo.yaml exige un formato de error único:
    {codigo, mensaje, errores: [{campo, mensaje}]}
y un uso preciso de los códigos HTTP:
    400 solo si el cuerpo no es JSON interpretable
    401 sin token, token inválido o token expirado
    404 recurso inexistente, o id de ruta que no es UUID válido
    409 la petición es válida pero choca con el estado de los datos
    422 el JSON es válido pero algún campo no pasa la validación

DRF por sí solo no produce este formato (usa {"detail": "..."} o un dict
plano de errores por campo) ni estos códigos (ValidationError es 400 por
defecto, no 422). Este archivo traduce las excepciones de DRF/Django al
contrato. Ver revision_sql.md, "Correcciones al código generado".
"""

import logging

from django.db import IntegrityError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Excepción base para los errores de negocio definidos en el contrato."""

    status_code = 400
    codigo = "ERROR_INTERNO"
    mensaje = "Ocurrió un problema."

    def __init__(self, mensaje=None):
        if mensaje:
            self.mensaje = mensaje
        super().__init__(self.mensaje)


class CredencialesInvalidasError(ApiError):
    status_code = 401
    codigo = "CREDENCIALES_INVALIDAS"
    mensaje = "Correo o contraseña incorrectos."


class AdministradorYaRegistradoError(ApiError):
    status_code = 409
    codigo = "ADMINISTRADOR_YA_REGISTRADO"
    mensaje = "La cuenta administrativa ya fue registrada."


class NombreServicioDuplicadoError(ApiError):
    status_code = 409
    codigo = "NOMBRE_SERVICIO_DUPLICADO"
    mensaje = "Ya existe un servicio activo con ese nombre."


class DiaHorarioDuplicadoError(ApiError):
    status_code = 409
    codigo = "DIA_HORARIO_DUPLICADO"
    mensaje = "Ese día ya tiene un horario; modifícalo en lugar de crear otro."


class TransicionNoPermitidaError(ApiError):
    status_code = 409
    codigo = "TRANSICION_NO_PERMITIDA"


class RequiereRevisionManualError(ApiError):
    status_code = 409
    codigo = "REQUIERE_REVISION_MANUAL"


class PedidoAnonimizadoError(ApiError):
    status_code = 409
    codigo = "PEDIDO_ANONIMIZADO"
    mensaje = "El pedido fue anonimizado y no admite cambios."


def _flatten_drf_detail(detail):
    """Convierte el `detail` de un ValidationError de DRF a la lista
    `errores: [{campo, mensaje}]` que pide el contrato."""
    errores = []
    if isinstance(detail, dict):
        for campo, mensajes in detail.items():
            if isinstance(mensajes, (list, tuple)):
                for m in mensajes:
                    errores.append({"campo": campo, "mensaje": str(m)})
            elif isinstance(mensajes, dict):
                for subcampo, submsgs in mensajes.items():
                    submsgs = submsgs if isinstance(submsgs, (list, tuple)) else [submsgs]
                    for m in submsgs:
                        errores.append(
                            {"campo": f"{campo}.{subcampo}", "mensaje": str(m)}
                        )
            else:
                errores.append({"campo": campo, "mensaje": str(mensajes)})
    elif isinstance(detail, (list, tuple)):
        for m in detail:
            errores.append({"campo": "non_field_errors", "mensaje": str(m)})
    else:
        errores.append({"campo": "non_field_errors", "mensaje": str(detail)})
    return errores


def laundrydesk_exception_handler(exc, context):
    # 1) Errores de negocio propios (409 principalmente).
    if isinstance(exc, ApiError):
        return Response(
            {"codigo": exc.codigo, "mensaje": exc.mensaje},
            status=exc.status_code,
        )

    # 2) Cuerpo no es JSON interpretable -> 400, único uso de 400.
    if isinstance(exc, drf_exceptions.ParseError):
        return Response(
            {
                "codigo": "SOLICITUD_MAL_FORMADA",
                "mensaje": "El cuerpo de la solicitud no es JSON válido.",
            },
            status=400,
        )

    # 3) Validación de campos -> 422 (DRF por defecto usaría 400).
    if isinstance(exc, drf_exceptions.ValidationError):
        return Response(
            {
                "codigo": "VALIDACION",
                "mensaje": "Revisa los campos marcados.",
                "errores": _flatten_drf_detail(exc.detail),
            },
            status=422,
        )

    # 4) No encontrado (incluye Http404, p.ej. UUID inválido en la ruta).
    if isinstance(exc, (Http404, drf_exceptions.NotFound)):
        return Response(
            {
                "codigo": "NO_ENCONTRADO",
                "mensaje": "El recurso solicitado no existe.",
            },
            status=404,
        )

    # 5) No autenticado: sin token, token inválido o token expirado.
    if isinstance(
        exc, (drf_exceptions.NotAuthenticated, drf_exceptions.AuthenticationFailed)
    ):
        return Response(
            {"codigo": "NO_AUTENTICADO", "mensaje": "Inicia sesión para continuar."},
            status=401,
        )

    # 6) Fallback de integridad de BD no capturado antes en el servicio:
    #    nunca debería llegar aquí si las vistas validan primero, pero
    #    sirve de red de seguridad para no exponer un 500 con traza SQL.
    if isinstance(exc, IntegrityError):
        logger.exception("IntegrityError no manejado explícitamente")
        return Response(
            {
                "codigo": "VALIDACION",
                "mensaje": "La operación choca con una restricción de la base de datos.",
            },
            status=409,
        )

    # 7) Deja que DRF maneje lo que reconozca (p. ej. MethodNotAllowed).
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    # 8) Cualquier otra excepción no prevista -> 500 genérico, sin detalle
    #    técnico en la respuesta (se registra en el log del servidor).
    logger.exception("Error interno no manejado")
    return Response(
        {
            "codigo": "ERROR_INTERNO",
            "mensaje": "Ocurrió un problema. Intenta de nuevo en unos minutos.",
        },
        status=500,
    )
