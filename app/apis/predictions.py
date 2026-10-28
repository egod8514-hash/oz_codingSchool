from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.users import UserModel
from app.schemas.predictions import PatientXrayAnalysisListResponse
from app.services import prediction_service


router = APIRouter(
    prefix="/api/v1",
    tags=["Predictions"],
)


@router.get(
    "/patients/{patient_id}/predictions",
    response_model=PatientXrayAnalysisListResponse,
    status_code=status.HTTP_200_OK,
    summary="[팀원 4] 환자별 X-ray + 예측 결과 목록 조회",
    description="특정 환자의 전체 진료기록에 등록된 X-ray 이미지 및 AI 폐렴 예측 결과 목록을 함께 조회합니다.",
)
@router.get(
    "/patients/{patient_id}/analyses",
    response_model=PatientXrayAnalysisListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
@router.get(
    "/patients/{patient_id}/xrays/predictions",
    response_model=PatientXrayAnalysisListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_patient_predictions(
    patient_id: int = Path(..., ge=1, description="환자 고유 ID"),
    only_analyzed: bool = Query(
        False,
        description="True인 경우 AI 예측 결과가 이미 존재하는 항목만 반환"
    ),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
) -> PatientXrayAnalysisListResponse:
    """
    [팀원 4 담당 기능]
    환자별 X-ray 이미지 및 폐렴 예측 결과 목록을 조회합니다.
    - 환자가 존재하지 않을 경우 404 Not Found
    - 승인 대기(PENDING) 계정일 경우 403 Forbidden
    """
    return await prediction_service.get_patient_xray_analysis_list(
        db=db,
        patient_id=patient_id,
        current_user=current_user,
        only_analyzed=only_analyzed,
    )
