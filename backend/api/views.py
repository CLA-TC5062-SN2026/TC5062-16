"""Vistas de LaundryDesk.

Parte 2 de seguridad:
- JWTAuthentication es la autenticación por defecto.
- Las operaciones administrativas requieren IsAuthenticated.
- Las operaciones públicas declaran AllowAny.
- Los endpoints mixtos (GET público / escritura protegida) resuelven permisos
  por método.
- Los pedidos y cambios de estado registran al administrador autenticado desde
  request.user, eliminando el uso operativo de ADMIN_ID_TEMPORAL.
"""

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .auth_utils import create_access_token, hash_password, verify_password
from .authentication import JWTAuthentication
from .exceptions import (
    AdministradorYaRegistradoError,
    CredencialesInvalidasError,
    DiaHorarioDuplicadoError,
    NombreServicioDuplicadoError,
)
from .models import Administrador, HistorialEstado, HorarioAtencion, NotaPedido, Pedido, Servicio
from .pagination import PedidoPageNumberPagination
from .serializers import (
    AdministradorPublicoSerializer,
    CambioEstadoSerializer,
    CambioEstadoSolicitudSerializer,
    HorarioActualizarSerializer,
    LoginSerializer,
    HorarioCrearSerializer,
    HorarioSerializer,
    NotaCrearSerializer,
    NotaSerializer,
    PedidoActualizarSerializer,
    PedidoCrearSerializer,
    PedidoDetalleSerializer,
    PedidoResumenSerializer,
    RegistroAdministradorSerializer,
    SeguimientoPublicoSerializer,
    ServicioActualizarSerializer,
    ServicioCrearSerializer,
    ServicioSerializer,
)


# ------------------------------------------------------------- autenticación
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroAdministradorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Transición desde S05-S06-A1: aquella entrega sembraba un
        # `admin_temporal` para satisfacer las FK de pedidos. Si es la única
        # cuenta existente, el primer registro la convierte en la cuenta real
        # conservando su UUID y todas las referencias históricas.
        temporal = Administrador.objects.filter(
            id=settings.ADMIN_ID_TEMPORAL, usuario="admin_temporal"
        ).first()
        otros = Administrador.objects.exclude(id=settings.ADMIN_ID_TEMPORAL).exists()

        if otros or (Administrador.objects.exists() and temporal is None):
            raise AdministradorYaRegistradoError()

        try:
            with transaction.atomic():
                if temporal is not None:
                    temporal.usuario = data["usuario"]
                    temporal.email = data["email"]
                    temporal.password_hash = hash_password(data["password"])
                    temporal.activo = True
                    temporal.save(
                        update_fields=["usuario", "email", "password_hash", "activo"]
                    )
                    administrador = temporal
                else:
                    administrador = Administrador.objects.create(
                        usuario=data["usuario"],
                        email=data["email"],
                        password_hash=hash_password(data["password"]),
                        activo=True,
                    )
        except IntegrityError as exc:
            raise AdministradorYaRegistradoError() from exc

        return Response(
            AdministradorPublicoSerializer(administrador).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            administrador = Administrador.objects.get(email__iexact=data["email"], activo=True)
        except Administrador.DoesNotExist as exc:
            raise CredencialesInvalidasError() from exc

        if not verify_password(data["password"], administrador.password_hash):
            raise CredencialesInvalidasError()

        token, expira_en = create_access_token(administrador)
        return Response(
            {"access": token, "tipo": "Bearer", "expira_en": expira_en},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(AdministradorPublicoSerializer(request.user).data)


# ------------------------------------------------------------------- servicio
class ServicioListCreateView(generics.ListCreateAPIView):
    queryset = Servicio.objects.all().order_by("nombre")

    def get_permissions(self):
        # GET es público; POST modifica configuración administrativa.
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return ServicioCrearSerializer if self.request.method == "POST" else ServicioSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Contrato OpenAPI: el público solo ve servicios activos. Un token
        # válido puede solicitar también los inactivos con
        # ?incluir_inactivos=true.
        valor = self.request.query_params.get("incluir_inactivos", "false").lower()
        if valor not in {"true", "false"}:
            raise ValidationError(
                {"incluir_inactivos": ["Debe ser true o false."]}
            )

        if valor == "true":
            if not getattr(self.request.user, "is_authenticated", False):
                raise NotAuthenticated("Se requiere autenticación para incluir servicios inactivos.")
            return qs

        return qs.filter(activo=True)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise NombreServicioDuplicadoError()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            ServicioSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )


class ServicioDetailView(generics.RetrieveUpdateAPIView):
    queryset = Servicio.objects.all()

    def get_permissions(self):
        # GET es público solo para servicios activos. PATCH requiere JWT.
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "GET" and not getattr(
            self.request.user, "is_authenticated", False
        ):
            return qs.filter(activo=True)
        return qs

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ServicioActualizarSerializer
        return ServicioSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            raise NombreServicioDuplicadoError()
        return Response(ServicioSerializer(instance).data)


# -------------------------------------------------------------------- horario
class HorarioListCreateView(generics.ListCreateAPIView):
    queryset = HorarioAtencion.objects.all().order_by("id")

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return HorarioCrearSerializer if self.request.method == "POST" else HorarioSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            raise DiaHorarioDuplicadoError()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            HorarioSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )


class HorarioDetailView(generics.RetrieveUpdateAPIView):
    queryset = HorarioAtencion.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return HorarioActualizarSerializer
        return HorarioSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(HorarioSerializer(instance).data)


# --------------------------------------------------------------------- pedido
class PedidoListCreateView(generics.ListCreateAPIView):
    pagination_class = PedidoPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return PedidoCrearSerializer if self.request.method == "POST" else PedidoResumenSerializer

    def get_queryset(self):
        qs = Pedido.objects.all().order_by("-fecha_recepcion")
        parametros = self.request.query_params
        estado = parametros.get("estado")
        if estado:
            qs = qs.filter(estado_actual=estado)
        codigo = parametros.get("codigo_seguimiento")
        if codigo:
            qs = qs.filter(codigo_seguimiento=codigo)
        telefono = parametros.get("telefono_cliente")
        if telefono:
            qs = qs.filter(telefono_cliente=services.normalizar_telefono(telefono))
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Pedido + primer historial forman una sola unidad lógica. El
        # administrador sale del JWT validado, no de un UUID temporal.
        with transaction.atomic():
            pedido = Pedido.objects.create(
                codigo_seguimiento=services.generar_codigo_seguimiento(),
                administrador=request.user,
                **serializer.validated_data,
            )
            HistorialEstado.objects.create(
                pedido=pedido,
                estado_anterior=None,
                estado_nuevo="RECIBIDO",
                administrador=request.user,
            )
        return Response(
            PedidoDetalleSerializer(pedido).data, status=status.HTTP_201_CREATED
        )


class PedidoDetailView(generics.RetrieveUpdateAPIView):
    queryset = Pedido.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PedidoDetalleSerializer

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return PedidoActualizarSerializer
        return PedidoDetalleSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PedidoDetalleSerializer(instance).data)


class PedidoEstadoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        solicitud = CambioEstadoSolicitudSerializer(data=request.data)
        solicitud.is_valid(raise_exception=True)
        historial = services.cambiar_estado(
            pedido,
            administrador_id=request.user.id,
            **solicitud.validated_data,
        )
        return Response(CambioEstadoSerializer(historial).data)


class PedidoCambiosEstadoView(generics.ListAPIView):
    serializer_class = CambioEstadoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pedido = get_object_or_404(Pedido, pk=self.kwargs["pedido_id"])
        return pedido.historial.order_by("fecha_cambio")


class PedidoNotasView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    # Solo POST: el contrato (openapi_equipo.yaml) consulta las notas
    # dentro de GET /pedidos/{pedido_id} (PedidoDetalleSerializer.notas),
    # no con un GET aparte sobre esta ruta. No se expone un endpoint que
    # el contrato no define.
    serializer_class = NotaCrearSerializer

    def create(self, request, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=self.kwargs["pedido_id"])
        if pedido.anonimizado:
            from .exceptions import PedidoAnonimizadoError

            raise PedidoAnonimizadoError()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nota = NotaPedido.objects.create(pedido=pedido, **serializer.validated_data)
        return Response(NotaSerializer(nota).data, status=status.HTTP_201_CREATED)


class SeguimientoView(generics.RetrieveAPIView):
    serializer_class = SeguimientoPublicoSerializer
    permission_classes = [AllowAny]
    lookup_field = "codigo_seguimiento"
    lookup_url_kwarg = "codigo_seguimiento"
    queryset = Pedido.objects.all()
