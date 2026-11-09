"""
Configuración de Django para LaundryDesk.

Evolución de seguridad de la actividad posterior a S05-S06-A1:
- JWTAuthentication es el mecanismo de autenticación por defecto.
- IsAuthenticated es el permiso por defecto; las vistas públicas declaran
  AllowAny de forma explícita según openapi_equipo.yaml.
- Las tablas del dominio siguen siendo `managed = False` porque se crean con
  esquema_bd.sql; Django no redefine el esquema físico.
- TIME_ZONE = America/Mexico_City y USE_TZ = True para conservar coherencia
  con los campos TIMESTAMPTZ y los filtros de fecha del contrato.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "inseguro-solo-para-desarrollo-local")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "rest_framework",
    "corsheaders",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Antes de CommonMiddleware a propósito: django-cors-headers debe poder
    # agregar los headers CORS a cualquier respuesta, incluidas las que
    # CommonMiddleware pudiera generar (p. ej. redirects).
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos: PostgreSQL 16, variables de entorno (.env / .env.example).
# Las 7 tablas del dominio (administrador, servicio, horario_atencion,
# pedido, historial_estado, nota_pedido, notificacion) ya existen: se
# importaron con esquema_bd.sql. Los modelos de api/models.py son
# `managed = False` y apuntan a esas tablas por nombre (db_table).
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "laundrydesk"),
        "USER": os.environ.get("DB_USER", "laundrydesk"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# JWT. El secret nunca debe quedar hard-coded en el repositorio.
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("Falta JWT_SECRET en el archivo .env")

try:
    JWT_EXPIRATION = int(os.environ.get("JWT_EXPIRATION", "3600"))
except ValueError as exc:
    raise RuntimeError("JWT_EXPIRATION debe ser un entero en segundos") from exc

# CORS: el frontend (Vite) corre en un origen distinto al backend (Django)
# tanto en desarrollo (localhost:5173 vs localhost:8000) como en producción
# si quedan en dominios separados de Render. Sin esto, el navegador bloquea
# toda llamada de authService/serviciosService/etc. aunque el código del
# frontend sea correcto. El origen por defecto es el puerto de Vite en
# desarrollo; agrega el dominio real de producción (y, si se usa, la URL
# pública de un Codespace) a CORS_ALLOWED_ORIGINS en el .env.
CORS_ALLOWED_ORIGINS = [
    origen.strip()
    for origen in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origen.strip()
]
# El JWT va en el header Authorization, no en una cookie, así que no hace
# falta CORS_ALLOW_CREDENTIALS. 'authorization' ya está en la lista de
# headers permitidos por defecto de django-cors-headers.

# Compatibilidad únicamente para convertir el `admin_temporal` sembrado en
# S05-S06-A1 durante POST /auth/register. Los CRUD protegidos ya NO usan este
# identificador: toman al administrador autenticado desde request.user (JWT).
ADMIN_ID_TEMPORAL = os.environ.get(
    "ADMIN_ID_TEMPORAL", "00000000-0000-0000-0000-000000000001"
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "api.exceptions.laundrydesk_exception_handler",
    # Parte 2: JWT es la autenticación por defecto y todo endpoint queda
    # protegido salvo que su vista declare explícitamente AllowAny.
    "DEFAULT_AUTHENTICATION_CLASSES": ["api.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNICODE_JSON": True,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
