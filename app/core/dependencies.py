# app/core/dependencies.py
from fastapi import (
    Header,
    Path,
    HTTPException,
    Depends,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# 실제 프로젝트 경로에 맞춰 import
from app.core import message
from app.core.db.databases import async_get_db
from app.models.users import UserModel
from app.models.patients import PatientModel
from app.core.enum.enum_role import RoleEnum

# 탈퇴하지 않은 유저 검증
async def get_current_user(
    user_id: int = Header(
        ..., 
        alias="X-User-Id", 
        description="테스트용 유저 ID (1: 어드민, 2: 스태프, 3: 대기자)"
    ),
    db: AsyncSession = Depends(async_get_db)
) -> UserModel:
    """
    1. 헤더의 X-User-Id 값을 수신
    2. DB에서 해당 ID 및 탈퇴 여부(is_deleted) 검증
    3. 계정이 없으면 404/401 에러, 존재하면 User 객체 반환
    """
    # 비동기 쿼리 실행
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # DB에 계정이 존재하지 않는 경우
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message.ERROR_MESSAGE_NONE_USER_INFO.format(
                x_user_id = user_id
            )
        )

    # 탈퇴 처리된 계정인 경우
    if getattr(user, "is_deleted", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message.ERROR_MESSAGE_DELETE_USER
        )

    return user


# admin 권한 검증
async def require_admin(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    get_current_user로 조회된 사용자가 '어드민' 권한인지 확인
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message.ERROR_MESSAGE_REQUIRED_ADMIN_ROLE
        )
    return current_user

# 비대기자 유저 검증
async def get_current_user_active(
    current_user: UserModel = Depends(get_current_user)
) : 

    if current_user.role == RoleEnum.PENDING : 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message.ERROR_MESSAGE_PENDING_ROLE
        )

# 삭제되지 않은 환자 검증
async def get_patient_info_dep(
    patient_id : int = Path(
        ...,
        ge = 1,
    ),
    db: AsyncSession = Depends(async_get_db)
) -> PatientModel : 
    # 비동기 쿼리 실행
    stmt = select(PatientModel).where(PatientModel.id == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    # DB에 계정이 존재하지 않는 경우
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message.ERROR_MESSAGE_NONE_USER_INFO.format(
                x_patient_id = patient_id
            )
        )

    # 환자가 없어진 경우
    if getattr(patient, "is_deleted", False):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message.ERROR_MESSAGE_NONE_USER_INFO.format(
                x_patient_id = patient_id
            )
        )

    return patient