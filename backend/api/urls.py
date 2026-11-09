"""
Rutas bajo /api/v1/ (config/urls.py), siguiendo exactamente las rutas de
openapi_equipo.yaml. Se usa el convertidor `uuid` de Django en los
parámetros *_id: si alguien manda un id que no es un UUID válido, Django
responde 404 antes de que la vista se ejecute (api/exceptions.py lo
traduce al formato del contrato), que es justo el comportamiento que pide
la sección "404 ... o id de ruta que no es UUID válido".

La autenticación se expone como /auth/register, /auth/login y /auth/me.
La protección de los CRUD administrativos se aplica mediante JWT en la Parte 2.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("auth/register", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login", views.LoginView.as_view(), name="auth-login"),
    path("auth/me", views.MeView.as_view(), name="auth-me"),
    path("servicios", views.ServicioListCreateView.as_view(), name="servicio-list"),
    path(
        "servicios/<uuid:pk>",
        views.ServicioDetailView.as_view(),
        name="servicio-detail",
    ),
    path("horarios", views.HorarioListCreateView.as_view(), name="horario-list"),
    path(
        "horarios/<uuid:pk>",
        views.HorarioDetailView.as_view(),
        name="horario-detail",
    ),
    path("pedidos", views.PedidoListCreateView.as_view(), name="pedido-list"),
    path("pedidos/<uuid:pk>", views.PedidoDetailView.as_view(), name="pedido-detail"),
    path(
        "pedidos/<uuid:pedido_id>/estado",
        views.PedidoEstadoView.as_view(),
        name="pedido-estado",
    ),
    path(
        "pedidos/<uuid:pedido_id>/cambios-estado",
        views.PedidoCambiosEstadoView.as_view(),
        name="pedido-cambios-estado",
    ),
    path(
        "pedidos/<uuid:pedido_id>/notas",
        views.PedidoNotasView.as_view(),
        name="pedido-notas",
    ),
    path(
        "seguimientos/<str:codigo_seguimiento>",
        views.SeguimientoView.as_view(),
        name="seguimiento",
    ),
]
