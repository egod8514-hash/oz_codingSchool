from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.patients import PatientModel
from app.models.users import UserModel
from app.models.medical_records import MedicalRecordModel
from app.core.enum.enum_role import RoleEnum
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.schemas.patients import (
    PatientCreateRequest,
    PatientUpdateRequest,
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
    """
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 환자를 등록할 수 없습니다."
        )

    if current_user.department != DepartmentEnum.MEDICAL and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="환자 정보 등록은 사내 의료진 또는 관리자만 가능합니다."
        )

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

    stmt = select(PatientModel).where(PatientModel.is_deleted == False)

    if name and name.strip():
        stmt = stmt.where(PatientModel.name.contains(name.strip()))

    if gender and gender.strip():
        clean_gender = gender.strip().upper()
        if clean_gender in GENDER_MAP:
            stmt = stmt.where(PatientModel.gender == GENDER_MAP[clean_gender])
        elif gender.strip() in GENDER_MAP:
            stmt = stmt.where(PatientModel.gender == GENDER_MAP[gender.strip()])

    if min_age is not None:
        stmt = stmt.where(PatientModel.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(PatientModel.age <= max_age)

    stmt = stmt.order_by(PatientModel.id.desc())

    result = await db.execute(stmt)
    patients = result.scalars().all()

    return [PatientResponse.model_validate(p) for p in patients]


async def get_patient_by_id(
    db: AsyncSession,
    patient_id: int,
    current_user: UserModel,
) -> PatientResponse:
    """
    [REQ-PTNT-003] 환자 정보 상세 단건 조회
    """
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 접근 권한이 없습니다."
        )

    stmt = select(PatientModel).where(
        PatientModel.id == patient_id,
        PatientModel.is_deleted == False
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 환자를 찾을 수 없습니다."
        )

    return PatientResponse.model_validate(patient)


async def update_patient(
    db: AsyncSession,
    patient_id: int,
    data: PatientUpdateRequest,
    current_user: UserModel,
) -> PatientResponse:
    """
    [REQ-PTNT-004] 특정 환자의 정보를 수정
    """
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 접근 권한이 없습니다."
        )

    stmt = select(PatientModel).where(
        PatientModel.id == patient_id,
        PatientModel.is_deleted == False
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 환자를 찾을 수 없습니다."
        )

    update_dict = data.model_dump(exclude_unset=True)
    if "name" in update_dict and update_dict["name"]:
        patient.name = update_dict["name"]
    if "age" in update_dict and update_dict["age"] is not None:
        patient.age = update_dict["age"]
    if "gender" in update_dict and update_dict["gender"]:
        g = update_dict["gender"].strip().upper()
        if g in GENDER_MAP:
            patient.gender = GENDER_MAP[g]
    if "phone" in update_dict and update_dict["phone"]:
        patient.phone = update_dict["phone"]

    await db.commit()
    await db.refresh(patient)

    return PatientResponse.model_validate(patient)


async def delete_patient(
    db: AsyncSession,
    patient_id: int,
    current_user: UserModel,
) -> dict:
    """
    [REQ-PTNT-005] 특정 환자 및 연관 진료기록/X-Ray 삭제
    """
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 환자를 삭제할 수 없습니다."
        )

    stmt = select(PatientModel).options(
        selectinload(PatientModel.medical_records).selectinload(
            MedicalRecordModel.xray_images
        )
    ).where(PatientModel.id == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()

    if not patient or patient.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 환자를 찾을 수 없습니다."
        )

    # 로컬 X-Ray 이미지 경로 수집
    image_paths = [
        Path(image.image_url)
        for record in patient.medical_records
        for image in record.xray_images
        if image.image_url
    ]

    try:
        await db.delete(patient)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    # 파일 삭제
    for p in image_paths:
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass

    return {"message": "환자와 관련된 진료기록 및 X-Ray가 삭제되었습니다."}
