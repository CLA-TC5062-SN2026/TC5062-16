"""
Serializadores.

Puntos de revision_sql.md que se resuelven aquí (sección 8 "Pendientes" de
la versión con openapi_equipo.yaml):
- Formato de hora `HH:MM`: TimeField(format='%H:%M', input_formats=[...]),
  en vez del '08:00:00' por defecto de DRF.
- Precio y Peso como cadena decimal (nunca number), con los mismos límites
  que los patrones `Precio`/`Peso` del contrato.
- Servicio inactivo al registrar un pedido: PrimaryKeyRelatedField con un
  queryset restringido a `activo=True`, así que un servicio_id inactivo
  cae sola, naturalmente, en el 422 de "no existe" (antes se validaba solo
  en el contrato, no en código: ver sección 8, pendiente 1 de la versión
  anterior del revision).
"""

import re
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import (
    Administrador,
    HistorialEstado,
    HorarioAtencion,
    NotaPedido,
    Pedido,
    Servicio,
)

PRECIO_RE = re.compile(r"^\d{1,8}(\.\d{1,2})?$")
PESO_RE = re.compile(r"^(?!0+(\.0{1,2})?$)\d{1,5}(\.\d{1,2})?$")


class PrecioField(serializers.CharField):
    """Monto como cadena decimal, >= 0, hasta 8 enteros y 2 decimales
    (columna NUMERIC(10,2)). Nunca `number`, igual que el contrato."""

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if not PRECIO_RE.match(data):
            raise serializers.ValidationError(
                "Debe ser un monto válido, p. ej. '2.50' (hasta 8 enteros y 2 decimales, mayor o igual a 0)."
            )
        return Decimal(data)

    def to_representation(self, value):
        if value is None:
            return None
        return f"{Decimal(value):.2f}"


class PesoField(serializers.CharField):
    """Peso en libras como cadena decimal, > 0 y <= 99999.99
    (columna NUMERIC(7,2), CHECK peso > 0)."""

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if not PESO_RE.match(data):
            raise serializers.ValidationError(
                "Debe ser un peso válido en libras, mayor que 0 y hasta 99999.99, p. ej. '12.40'."
            )
        return Decimal(data)

    def to_representation(self, value):
        if value is None:
            return None
        return f"{Decimal(value):.2f}"


class HoraField(serializers.TimeField):
    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%H:%M")
        kwargs.setdefault("input_formats", ["%H:%M"])
        super().__init__(**kwargs)


def texto_obligatorio(max_length):
    """CharField equivalente al patrón `\\S` del contrato: con
    trim_whitespace=True, una cadena vacía o solo de espacios/tabs se
    rechaza igual que el patrón (allow_blank=False)."""
    return serializers.CharField(max_length=max_length, allow_blank=False, trim_whitespace=True)


# --------------------------------------------------------------------- servicio
class ServicioSerializer(serializers.ModelSerializer):
    precio = PrecioField()

    class Meta:
        model = Servicio
        fields = ["id", "nombre", "descripcion", "precio", "unidad", "activo"]
        read_only_fields = ["id"]


class ServicioCrearSerializer(serializers.ModelSerializer):
    nombre = texto_obligatorio(100)
    unidad = texto_obligatorio(20)
    precio = PrecioField()
    descripcion = serializers.CharField(
        max_length=500, required=False, allow_null=True, allow_blank=True
    )
    activo = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Servicio
        fields = ["nombre", "descripcion", "precio", "unidad", "activo"]


class ServicioActualizarSerializer(serializers.ModelSerializer):
    nombre = texto_obligatorio(100)
    unidad = texto_obligatorio(20)
    precio = PrecioField()
    descripcion = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Servicio
        fields = ["nombre", "descripcion", "precio", "unidad", "activo"]
        extra_kwargs = {
            "nombre": {"required": False},
            "unidad": {"required": False},
            "precio": {"required": False},
            "descripcion": {"required": False},
            "activo": {"required": False},
        }

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Envía al menos un campo para actualizar."}
            )
        return attrs


# --------------------------------------------------------------------- horario
class HorarioSerializer(serializers.ModelSerializer):
    hora_apertura = HoraField(allow_null=True)
    hora_cierre = HoraField(allow_null=True)

    class Meta:
        model = HorarioAtencion
        fields = ["id", "dia_semana", "hora_apertura", "hora_cierre", "cerrado"]
        read_only_fields = ["id"]


class HorarioCrearSerializer(serializers.ModelSerializer):
    hora_apertura = HoraField(required=False, allow_null=True)
    hora_cierre = HoraField(required=False, allow_null=True)
    cerrado = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = HorarioAtencion
        fields = ["dia_semana", "hora_apertura", "hora_cierre", "cerrado"]

    def validate(self, attrs):
        cerrado = attrs.get("cerrado", False)
        apertura = attrs.get("hora_apertura")
        cierre = attrs.get("hora_cierre")
        if not cerrado:
            errores = {}
            if apertura is None:
                errores["hora_apertura"] = "Obligatoria si el día no está cerrado."
            if cierre is None:
                errores["hora_cierre"] = "Obligatoria si el día no está cerrado."
            if errores:
                raise serializers.ValidationError(errores)
            if apertura >= cierre:
                raise serializers.ValidationError(
                    {"hora_cierre": "Debe ser posterior a hora_apertura."}
                )
        return attrs


class HorarioActualizarSerializer(serializers.ModelSerializer):
    hora_apertura = HoraField(required=False, allow_null=True)
    hora_cierre = HoraField(required=False, allow_null=True)

    class Meta:
        model = HorarioAtencion
        fields = ["dia_semana", "hora_apertura", "hora_cierre", "cerrado"]
        extra_kwargs = {
            "dia_semana": {"required": False},
            "cerrado": {"required": False},
        }

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Envía al menos un campo para actualizar."}
            )
        instancia = self.instance
        cerrado = attrs.get("cerrado", instancia.cerrado if instancia else False)
        apertura = attrs.get(
            "hora_apertura", instancia.hora_apertura if instancia else None
        )
        cierre = attrs.get("hora_cierre", instancia.hora_cierre if instancia else None)
        if not cerrado:
            errores = {}
            if apertura is None:
                errores["hora_apertura"] = "Obligatoria si el día no está cerrado."
            if cierre is None:
                errores["hora_cierre"] = "Obligatoria si el día no está cerrado."
            if errores:
                raise serializers.ValidationError(errores)
            if apertura >= cierre:
                raise serializers.ValidationError(
                    {"hora_cierre": "Debe ser posterior a hora_apertura."}
                )
        return attrs


# ---------------------------------------------------------------------- notas
class NotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaPedido
        fields = ["id", "tipo", "texto", "fecha_registro"]
        read_only_fields = ["id", "fecha_registro"]


class NotaCrearSerializer(serializers.ModelSerializer):
    texto = texto_obligatorio(2000)

    class Meta:
        model = NotaPedido
        fields = ["tipo", "texto"]


# -------------------------------------------------------------------- pedido
class PedidoResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            "id",
            "codigo_seguimiento",
            "estado_actual",
            "fecha_recepcion",
            "nombre_cliente",
        ]


class PedidoDetalleSerializer(serializers.ModelSerializer):
    peso = PesoField(allow_null=True, required=False)
    precio_final = PrecioField(allow_null=True, required=False)
    notas = NotaSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id",
            "codigo_seguimiento",
            "fecha_recepcion",
            "nombre_cliente",
            "telefono_cliente",
            "email_cliente",
            "peso",
            "precio_final",
            "instrucciones_especiales",
            "estado_actual",
            "fecha_listo",
            "fecha_cierre",
            "anonimizado",
            "servicio_id",
            "administrador_id",
            "notas",
        ]
        read_only_fields = [
            "id",
            "codigo_seguimiento",
            "estado_actual",
            "fecha_listo",
            "fecha_cierre",
            "anonimizado",
            "administrador_id",
            "notas",
        ]


class PedidoCrearSerializer(serializers.ModelSerializer):
    nombre_cliente = texto_obligatorio(150)
    telefono_cliente = texto_obligatorio(20)
    servicio_id = serializers.PrimaryKeyRelatedField(
        source="servicio",
        queryset=Servicio.objects.filter(activo=True),
        error_messages={
            "does_not_exist": "El servicio no existe o está inactivo."
        },
    )
    peso = PesoField(allow_null=True, required=False)
    precio_final = PrecioField(allow_null=True, required=False)
    instrucciones_especiales = serializers.CharField(
        max_length=1000, allow_null=True, allow_blank=True, required=False
    )
    email_cliente = serializers.EmailField(
        max_length=254, allow_null=True, required=False
    )
    fecha_recepcion = serializers.DateTimeField(required=False)

    class Meta:
        model = Pedido
        fields = [
            "nombre_cliente",
            "telefono_cliente",
            "email_cliente",
            "servicio_id",
            "fecha_recepcion",
            "peso",
            "precio_final",
            "instrucciones_especiales",
        ]

    def validate_fecha_recepcion(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "No puede ser posterior al momento del registro."
            )
        return value

    def validate_telefono_cliente(self, value):
        # Normalización (revision_sql.md sección 6, punto 7): sin espacios
        # ni guiones, para que la búsqueda por teléfono sea exacta.
        return re.sub(r"[\s\-]", "", value)


class PedidoActualizarSerializer(serializers.ModelSerializer):
    peso = PesoField(allow_null=True, required=False)
    precio_final = PrecioField(allow_null=True, required=False)
    instrucciones_especiales = serializers.CharField(
        max_length=1000, allow_null=True, allow_blank=True, required=False
    )

    class Meta:
        model = Pedido
        fields = ["peso", "precio_final", "instrucciones_especiales"]

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Envía al menos un campo para actualizar."}
            )
        return attrs


class CambioEstadoSolicitudSerializer(serializers.Serializer):
    estado_nuevo = serializers.ChoiceField(
        choices=[c[0] for c in Pedido._meta.get_field("estado_actual").choices]
    )
    es_correccion = serializers.BooleanField(required=False, default=False)
    confirmacion = serializers.BooleanField(required=False, default=False)
    motivo = serializers.CharField(
        max_length=500, required=False, allow_blank=True, trim_whitespace=True
    )

    def validate(self, attrs):
        if attrs.get("es_correccion"):
            errores = {}
            if not attrs.get("confirmacion"):
                errores["confirmacion"] = "Obligatorio y en true para una corrección manual."
            motivo = attrs.get("motivo", "")
            if not motivo or not motivo.strip():
                errores["motivo"] = "Indica el motivo de la corrección."
            if errores:
                raise serializers.ValidationError(errores)
        return attrs


class CambioEstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialEstado
        fields = [
            "id",
            "estado_anterior",
            "estado_nuevo",
            "fecha_cambio",
            "es_correccion",
            "motivo",
            "administrador_id",
        ]


class SeguimientoPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ["codigo_seguimiento", "estado_actual", "fecha_recepcion", "fecha_listo"]


# ---------------------------------------------------------- autenticación
class AdministradorPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = ["id", "usuario", "email", "activo"]
        read_only_fields = fields


class RegistroAdministradorSerializer(serializers.Serializer):
    usuario = texto_obligatorio(150)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        min_length=8, max_length=128, write_only=True, trim_whitespace=False
    )

    def validate_email(self, value):
        return value.strip().lower()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(
        max_length=128, write_only=True, trim_whitespace=False
    )

    def validate_email(self, value):
        return value.strip().lower()
