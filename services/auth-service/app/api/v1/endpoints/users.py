import math

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse

logger = structlog.get_logger()
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> UserListResponse:
    offset = (page - 1) * page_size

    count_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    total = count_result.scalar_one()

    users_result = await db.execute(
        select(User)
        .where(User.is_active.is_(True))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    users = list(users_result.scalars().all())

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )
