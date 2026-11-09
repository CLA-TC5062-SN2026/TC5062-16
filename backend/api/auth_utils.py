"""Utilidades de autenticación JWT y bcrypt para LaundryDesk."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from django.conf import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(administrador):
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(seconds=settings.JWT_EXPIRATION)
    payload = {
        "sub": str(administrador.id),
        "usuario": administrador.usuario,
        "email": administrador.email,
        "iat": now,
        "exp": expiration,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token, settings.JWT_EXPIRATION
