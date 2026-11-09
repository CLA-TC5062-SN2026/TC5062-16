"""Autenticación Bearer JWT para Django REST Framework."""

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from .models import Administrador


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if header[0].decode("utf-8").lower() != self.keyword.lower():
            return None
        if len(header) != 2:
            raise AuthenticationFailed("Token Bearer inválido.")

        token = header[1].decode("utf-8")
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("El token expiró.") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationFailed("El token es inválido.") from exc

        admin_id = payload.get("sub")
        if not admin_id:
            raise AuthenticationFailed("El token no contiene un sujeto válido.")

        try:
            administrador = Administrador.objects.get(id=admin_id, activo=True)
        except (Administrador.DoesNotExist, ValueError) as exc:
            raise AuthenticationFailed("El token no corresponde a una cuenta activa.") from exc

        return administrador, payload

    def authenticate_header(self, request):
        return self.keyword
