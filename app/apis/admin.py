from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import require_admin
from app.models.users import UserModel
from app.core.enum.enum_department import DepartmentEnum
from app.schemas.admin import AdminUserListResponse, AdminUserResponse, AdminRoleUpdateRequest
from app.services import admin_service


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


def _to_admin_user_response(u: UserModel) -> AdminUserResponse:
    dept = u.department.value if hasattr(u.department, "value") else str(u.department)
    gender = u.gender.value if hasattr(u.gender, "value") else str(u.gender)
    role = (u.role.value if hasattr(u.role, "value") else str(u.role)).lower()
    return AdminUserResponse(
        id=u.id,
        email=u.email,
        name=u.name,
        department=dept,
        gender=gender,
        phone_number=u.phone_number,
        role=role,
        is_active=u.is_active,
    )


@router.get(
    "/users",
    response_model=AdminUserListResponse,
)
async def get_users(
    search: str | None = None,
    department: DepartmentEnum | None = None,
    db: AsyncSession = Depends(async_get_db),
    admin_user: UserModel = Depends(require_admin),
):
    users = await admin_service.get_users(
        db=db,
        search=search,
        department=department,
    )

    return {
        "users": [_to_admin_user_response(u) for u in users]
    }


@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
)
async def update_user_role(
    user_id: int,
    request: AdminRoleUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
    admin_user: UserModel = Depends(require_admin),
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

    return _to_admin_user_response(user)


@router.patch(
    "/users/role",
    response_model=AdminUserResponse,
    summary="회원 권한 변경 (바디 내 user_id 포함 호환용)",
)
async def update_user_role_body(
    request: AdminRoleUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
    admin_user: UserModel = Depends(require_admin),
):
    if request.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id가 필요합니다.",
        )
    user = await admin_service.update_user_role(
        db=db,
        user_id=request.user_id,
        role=request.role,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )
    return _to_admin_user_response(user)
