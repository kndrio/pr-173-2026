import uuid
from dataclasses import dataclass

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

logger = structlog.get_logger()

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@dataclass
class UserPayload:
    """Minimal user info extracted from JWT — orders service never queries the users table."""

    id: uuid.UUID
    email: str
    role: str = "operator"


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> UserPayload:
    """
    Validate JWT signed by auth-service using the shared secret.
    Returns UserPayload extracted from claims. No DB call to auth-service.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return UserPayload(
            id=uuid.UUID(sub),
            email=payload.get("email", ""),
            role=payload.get("role", "operator"),
        )
    except (JWTError, ValueError):
        logger.warning("invalid_jwt_token")
        raise credentials_exception
