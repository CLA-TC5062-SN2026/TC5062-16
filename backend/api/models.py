"""
Modelos equivalentes a los que generaría `manage.py inspectdb` sobre
esquema_bd.sql, corregidos a mano según revision_sql.md sección 5
("Para quien escriba los servicios CRUD en Django"):

- Todos son `managed = False`: las tablas ya existen en PostgreSQL
  (esquema_bd.sql). Django nunca las crea, altera ni borra.
- Los enums (CHECK en SQL) se declaran como `choices`, porque inspectdb no
  los genera a partir de un CHECK (no son tipos ENUM nativos).
- `servicio_nombre_activo_uq` (índice único parcial) se declara en
  Meta.constraints, porque inspectdb no detecta índices parciales.
- Las FK usan db_column explícito con el mismo nombre de columna del SQL
  (sufijo _id), y el mismo ON DELETE del esquema (RESTRICT o CASCADE).
"""

import uuid

from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Trim, Upper
from django.utils import timezone

ESTADO_PEDIDO_CHOICES = [
    ("RECIBIDO", "Recibido"),
    ("EN_PROCESO", "En proceso"),
    ("LISTO", "Listo"),
    ("ENTREGADO", "Entregado"),
    ("CANCELADO", "Cancelado"),
]

TIPO_NOTA_CHOICES = [
    ("NOTA", "Nota"),
    ("INCIDENCIA", "Incidencia"),
]

DIA_SEMANA_CHOICES = [
    ("LUNES", "Lunes"),
    ("MARTES", "Martes"),
    ("MIERCOLES", "Miércoles"),
    ("JUEVES", "Jueves"),
    ("VIERNES", "Viernes"),
    ("SABADO", "Sábado"),
    ("DOMINGO", "Domingo"),
]

CANAL_NOTIFICACION_CHOICES = [
    ("CORREO", "Correo"),
    ("SMS", "SMS"),
]

ESTADO_ENVIO_CHOICES = [
    ("PENDIENTE", "Pendiente"),
    ("ENVIADA", "Enviada"),
    ("FALLIDA", "Fallida"),
]


class Administrador(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "administrador"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.usuario


class Servicio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "servicio"
        constraints = [
            UniqueConstraint(
                Upper(Trim("nombre")),
                condition=Q(activo=True),
                name="servicio_nombre_activo_uq",
            )
        ]

    def __str__(self):
        return self.nombre


class HorarioAtencion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dia_semana = models.CharField(
        max_length=10, choices=DIA_SEMANA_CHOICES, unique=True
    )
    hora_apertura = models.TimeField(null=True, blank=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    cerrado = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "horario_atencion"

    def __str__(self):
        return self.dia_semana


class Pedido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_seguimiento = models.CharField(max_length=20, unique=True)
    fecha_recepcion = models.DateTimeField(default=timezone.now)

    nombre_cliente = models.CharField(max_length=150)
    telefono_cliente = models.CharField(max_length=20)
    email_cliente = models.EmailField(max_length=254, null=True, blank=True)

    peso = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    precio_final = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    instrucciones_especiales = models.TextField(null=True, blank=True)

    estado_actual = models.CharField(
        max_length=20, choices=ESTADO_PEDIDO_CHOICES, default="RECIBIDO"
    )
    fecha_listo = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    anonimizado = models.BooleanField(default=False)

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.RESTRICT,
        db_column="servicio_id",
        related_name="pedidos",
    )
    administrador = models.ForeignKey(
        Administrador,
        on_delete=models.RESTRICT,
        db_column="administrador_id",
        related_name="pedidos",
    )

    class Meta:
        managed = False
        db_table = "pedido"

    def __str__(self):
        return self.codigo_seguimiento


class HistorialEstado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estado_anterior = models.CharField(
        max_length=20, choices=ESTADO_PEDIDO_CHOICES, null=True, blank=True
    )
    estado_nuevo = models.CharField(max_length=20, choices=ESTADO_PEDIDO_CHOICES)
    fecha_cambio = models.DateTimeField(default=timezone.now)
    es_correccion = models.BooleanField(default=False)
    motivo = models.TextField(null=True, blank=True)

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="pedido_id",
        related_name="historial",
    )
    administrador = models.ForeignKey(
        Administrador,
        on_delete=models.RESTRICT,
        db_column="administrador_id",
        related_name="cambios_estado",
    )

    class Meta:
        managed = False
        db_table = "historial_estado"

    def __str__(self):
        return f"{self.pedido_id}: {self.estado_anterior} -> {self.estado_nuevo}"


class NotaPedido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=10, choices=TIPO_NOTA_CHOICES)
    texto = models.TextField()
    fecha_registro = models.DateTimeField(default=timezone.now)

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="pedido_id",
        related_name="notas",
    )

    class Meta:
        managed = False
        db_table = "nota_pedido"

    def __str__(self):
        return f"{self.tipo}: {self.texto[:40]}"


class Notificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    canal = models.CharField(
        max_length=10, choices=CANAL_NOTIFICACION_CHOICES, default="CORREO"
    )
    destinatario = models.CharField(max_length=254)
    estado_envio = models.CharField(
        max_length=10, choices=ESTADO_ENVIO_CHOICES, default="PENDIENTE"
    )
    intentos = models.IntegerField(default=0)
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="pedido_id",
        related_name="notificaciones",
    )

    class Meta:
        managed = False
        db_table = "notificacion"

    def __str__(self):
        return f"{self.canal} -> {self.destinatario} ({self.estado_envio})"
