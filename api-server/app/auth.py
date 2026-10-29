"""Autenticação JWT da Viangola Interprovincial.

- Access token: JWT assinado, curto (30 min), claims ``sub``/``role``/``type``.
- Refresh token: JWT com ``jti`` persistido na tabela ``refresh_tokens``,
  permitindo revogação (logout) e rotação a cada refresh.
- Passwords: apenas bcrypt (nunca texto plano).
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated, Callable

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import RefreshToken, User

# Em produção defina JWT_SECRET no ambiente. O valor abaixo é apenas para
# desenvolvimento local (os tokens deixam de ser válidos a cada reinício).
JWT_SECRET = os.environ.get("JWT_SECRET") or "viangola-local-dev-secret-do-not-use-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = timedelta(minutes=30)
REFRESH_TOKEN_TTL = timedelta(days=14)
MIN_PASSWORD_LENGTH = 8

_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    """SQLite devolve datetimes sem timezone — normaliza para UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def create_access_token(user: User) -> tuple[str, int]:
    expires_at = _now() + ACCESS_TOKEN_TTL
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "type": "access",
        "jti": secrets.token_urlsafe(12),
        "exp": expires_at,
        "iat": _now(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, int(ACCESS_TOKEN_TTL.total_seconds())


def issue_refresh_token(db: Session, user: User) -> str:
    jti = secrets.token_urlsafe(24)
    expires_at = _now() + REFRESH_TOKEN_TTL
    db.add(RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at))
    db.flush()
    payload = {"sub": str(user.id), "jti": jti, "type": "refresh", "exp": expires_at, "iat": _now()}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def _decode(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise _unauthorized("Token inválido ou expirado")
    if payload.get("type") != expected_type:
        raise _unauthorized("Tipo de token inválido")
    return payload


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise _unauthorized("Credenciais em falta")
    payload = _decode(credentials.credentials, "access")
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise _unauthorized("Utilizador não encontrado")
    if not user.is_active:
        raise _unauthorized("Conta desativada")
    return user


def require_roles(*roles: str) -> Callable[..., User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Sem permissões para esta operação")
        return user

    return dependency


def validate_refresh_token(db: Session, token: str) -> tuple[User, str]:
    """Valida o refresh token e devolve (utilizador, jti) para rotação."""
    payload = _decode(token, "refresh")
    row = db.scalar(select(RefreshToken).where(RefreshToken.jti == payload.get("jti")))
    if row is None or row.revoked_at is not None:
        raise _unauthorized("Sessão inválida ou terminada")
    if _as_utc(row.expires_at) <= _now():
        raise _unauthorized("Sessão expirada")
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise _unauthorized("Conta desativada")
    return user, row.jti


def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoga o refresh token apresentado. Devolve True se algo foi revogado."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False},
        )
    except jwt.PyJWTError:
        return False
    if payload.get("type") != "refresh":
        return False
    row = db.scalar(select(RefreshToken).where(RefreshToken.jti == payload.get("jti")))
    if row is None or row.revoked_at is not None:
        return False
    row.revoked_at = _now()
    db.add(row)
    return True
