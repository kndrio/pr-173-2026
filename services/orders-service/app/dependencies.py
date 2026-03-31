import uuid

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

ALGORITHM = "HS256"


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> uuid.UUID:
    """
    Validate the JWT signed by auth-service using the shared JWT_SECRET.
    Returns the user UUID from the token 'sub' claim.
    No HTTP call to auth-service — shared secret validation only.
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
        return uuid.UUID(sub)
    except (JWTError, ValueError):
        logger.warning("invalid_token")
        raise credentials_exception
