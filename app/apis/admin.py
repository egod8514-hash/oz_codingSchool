from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.enum.enum_department import DepartmentEnum
from app.schemas.admin import AdminUserListResponse, AdminUserResponse, AdminRoleUpdateRequest
from app.services import admin_service


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.get(
    "/users",
    response_model=AdminUserListResponse,
)
async def get_users(
    search: str | None = None,
    department: DepartmentEnum | None = None,
    db: AsyncSession = Depends(async_get_db),
):
    users = await admin_service.get_users(
        db=db,
        search=search,
        department=department,
    )

    return {
        "users": users
    }

@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
)
async def update_user_role(
    user_id: int,
    request: AdminRoleUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
):
    user = await admin_service.update_user_role(
        db=db,
        user_id=user_id,
        role=request.role,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    return user