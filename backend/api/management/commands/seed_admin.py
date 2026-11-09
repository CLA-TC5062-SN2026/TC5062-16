"""
Crea (de forma idempotente) la fila de `administrador` con el mismo id que
settings.ADMIN_ID_TEMPORAL, para que pedido.administrador_id e
historial_estado.administrador_id (ambas FK obligatorias, NOT NULL) tengan
algo válido a qué apuntar mientras no exista autenticación real.

Uso:
    python manage.py seed_admin

Se puede correr tantas veces como se quiera: si el administrador ya
existe, no hace nada (get_or_create).
"""

import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import Administrador


class Command(BaseCommand):
    help = "Crea el admin_temporal de compatibilidad para el primer registro JWT."

    def handle(self, *args, **options):
        admin_id = settings.ADMIN_ID_TEMPORAL
        # password_hash no se usa para nada todavía (no hay login), pero la
        # columna es NOT NULL: se guarda un valor que deja claro que no es
        # una contraseña real y que no debe usarse para autenticar a nadie.
        placeholder = hashlib.sha256(b"sin-autenticacion-temporal").hexdigest()

        administrador, creado = Administrador.objects.get_or_create(
            id=admin_id,
            defaults={
                "usuario": "admin_temporal",
                "password_hash": placeholder,
                "activo": True,
            },
        )

        if creado:
            self.stdout.write(
                self.style.SUCCESS(f"Administrador temporal creado: {administrador.id}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Administrador temporal ya existía: {administrador.id}")
            )
