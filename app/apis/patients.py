from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.users import UserModel
from app.schemas.patients import PatientCreateRequest, PatientResponse
from app.services import patient_service

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])


@router.post(
    "",
    summary="[REQ-PTNT-001] 환자 정보 등록",
    description="사내 의료인 역할을 가진 유저가 신규 환자 정보를 등록합니다. (이름, 나이, 성별, 연락처)",
    status_code=status.HTTP_201_CREATED,
    response_model=PatientResponse,
)
async def create_patient_handler(
    data: PatientCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    return await patient_service.create_patient(
        db=db,
        data=data,
        current_user=current_user,
    )


@router.get(
    "",
    summary="[REQ-PTNT-002] 환자 목록 조회",
    description="로그인된 사내 사용자(개발, 의료, 연구진)가 등록된 환자 목록을 조회합니다. 이름 검색 및 성별/나이 범위 필터링을 지원합니다.",
    status_code=status.HTTP_200_OK,
    response_model=List[PatientResponse],
)
async def get_patients_handler(
    name: Optional[str] = Query(None, description="환자 이름 검색 (부분 일치)"),
    gender: Optional[str] = Query(None, description="성별 필터 (M, F, male, female, 남성, 여성)"),
    min_age: Optional[int] = Query(None, ge=0, description="최소 나이"),
    max_age: Optional[int] = Query(None, ge=0, description="최대 나이"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    return await patient_service.get_patients(
        db=db,
        current_user=current_user,
        name=name,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
    )
