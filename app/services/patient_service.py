from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.patients import PatientModel
from app.models.users import UserModel
from app.core.enum.enum_role import RoleEnum
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.schemas.patients import (
    PatientCreateRequest,
    PatientResponse,
    GENDER_MAP,
)


async def create_patient(
    db: AsyncSession,
    data: PatientCreateRequest,
    current_user: UserModel,
) -> PatientResponse:
    """
    [REQ-PTNT-001] 환자 정보 등록
    - 권한: 사내 의료진(MEDICAL) 또는 시스템 관리자(ADMIN)만 등록 가능
    - 대기자(PENDING) 또는 비의료 직군은 403 Forbidden
    """
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 환자를 등록할 수 없습니다."
        )

    # 사내 의료인 또는 관리자 권한 확인
    if current_user.department != DepartmentEnum.MEDICAL and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="환자 정보 등록은 사내 의료진 또는 관리자만 가능합니다."
        )

    # 환자 엔티티 생성
    new_patient = PatientModel(
        name=data.name,
        age=data.age,
        gender=GenderEnum(data.gender),
        phone=data.phone,
        is_deleted=False,
    )

    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)

    return PatientResponse.model_validate(new_patient)


async def get_patients(
    db: AsyncSession,
    current_user: UserModel,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
) -> List[PatientResponse]:
    """
    [REQ-PTNT-002] 환자 목록 조회
    - 권한: 로그인된 사내 개발진, 의료 실무진, 연구진 (PENDING 제외)
    - 이름 검색(부분 일치) 및 성별/나이 범위 필터링 제공
    """
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 환자 목록을 조회할 수 없습니다."
        )

    # 기본 쿼리 (삭제되지 않은 환자만 조회)
    stmt = select(PatientModel).where(PatientModel.is_deleted == False)

    # 1. 이름 검색 (부분 일치)
    if name and name.strip():
        stmt = stmt.where(PatientModel.name.contains(name.strip()))

    # 2. 성별 필터링
    if gender and gender.strip():
        clean_gender = gender.strip().upper()
        if clean_gender in GENDER_MAP:
            target_gender = GENDER_MAP[clean_gender]
            stmt = stmt.where(PatientModel.gender == target_gender)
        elif gender.strip() in GENDER_MAP:
            target_gender = GENDER_MAP[gender.strip()]
            stmt = stmt.where(PatientModel.gender == target_gender)

    # 3. 나이 범위 필터링
    if min_age is not None:
        stmt = stmt.where(PatientModel.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(PatientModel.age <= max_age)

    # 최신 등록순 정렬
    stmt = stmt.order_by(PatientModel.id.desc())

    result = await db.execute(stmt)
    patients = result.scalars().all()

    return [PatientResponse.model_validate(p) for p in patients]
