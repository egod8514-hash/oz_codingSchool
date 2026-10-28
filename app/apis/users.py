from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.core.security import verify_password, hash_password
from app.models.users import UserModel
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginResponse,
)
from app.services import auth_service
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# =========================================================
# 프론트엔드 호환용 Auth 엔드포인트
# =========================================================
@router.post(
    "/signup",
    summary="회원가입 (프론트엔드 호환)",
    status_code=status.HTTP_201_CREATED,
    response_model=SignupResponse,
)
async def user_signup(
    data: SignupRequest,
    db: AsyncSession = Depends(async_get_db),
):
    return await auth_service.register_user(db, data)


@router.post(
    "/login",
    summary="로그인 (프론트엔드 호환)",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def user_login(
    request: Request,
    db: AsyncSession = Depends(async_get_db),
):
    return await auth_service.login_request_handler(request, db)


@router.post("/logout", summary="로그아웃")
async def user_logout():
    return {"message": "로그아웃되었습니다."}


# =========================================================
# 마이페이지 및 내 정보 관리
# =========================================================
class UserProfileResponse(BaseModel):
    id: int
    email: str
    name: str
    department: str
    gender: str
    phone_number: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    department: Optional[str] = None
    phone_number: Optional[str] = None
    phone: Optional[str] = None


class UserPasswordChangeRequest(BaseModel):
    current_password: Optional[str] = None
    password: Optional[str] = None
    new_password: str = Field(..., min_length=8)


@router.get(
    "/me",
    summary="[REQ-USER-006] 내 정보 조회",
    response_model=UserProfileResponse,
)
async def get_my_profile(
    current_user: UserModel = Depends(get_current_user),
):
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        department=current_user.department.value if hasattr(current_user.department, "value") else str(current_user.department),
        gender=current_user.gender.value if hasattr(current_user.gender, "value") else str(current_user.gender),
        phone_number=current_user.phone_number,
        role=(current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)).lower(),
        is_active=current_user.is_active,
    )


@router.patch(
    "/me",
    summary="[REQ-USER-007] 내 정보 수정",
)
async def update_my_profile(
    body: UserProfileUpdateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    from app.core.enum.enum_department import DepartmentEnum
    if body.department:
        clean_dept = body.department.strip().upper()
        dept_map = {
            "의료": DepartmentEnum.MEDICAL,
            "MEDICAL": DepartmentEnum.MEDICAL,
            "개발": DepartmentEnum.DEV,
            "DEV": DepartmentEnum.DEV,
            "연구": DepartmentEnum.RESEARCH,
            "RESEARCH": DepartmentEnum.RESEARCH,
        }
        if body.department.strip() in dept_map:
            current_user.department = dept_map[body.department.strip()]
        elif clean_dept in dept_map:
            current_user.department = dept_map[clean_dept]

    new_phone = body.phone_number or body.phone
    if new_phone:
        current_user.phone_number = new_phone.strip()

    await db.commit()
    await db.refresh(current_user)
    return {"message": "회원 정보가 성공적으로 수정되었습니다."}


@router.patch(
    "/me/password",
    summary="[REQ-USER-008] 비밀번호 변경",
)
async def change_my_password(
    body: UserPasswordChangeRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    old_password = body.current_password or body.password
    if not old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호를 입력해주세요."
        )

    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다."
        )

    if verify_password(body.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호는 기존 비밀번호와 동일할 수 없습니다."
        )

    current_user.hashed_password = hash_password(body.new_password)
    await db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


@router.delete(
    "/me",
    summary="[REQ-USER-009] 회원 탈퇴",
)
async def delete_my_account(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    current_user.is_deleted = True
    current_user.delete_at = func.now()
    await db.commit()
    return {"message": "회원 탈퇴 및 정보 삭제가 정상 완료되었습니다."}
