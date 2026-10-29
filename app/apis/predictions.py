from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.users import UserModel
from app.schemas.predictions import (
    PredictionResponse,
    PatientXrayAnalysisListResponse,
)
from app.services import prediction_service


router = APIRouter(
    prefix="/api/v1",
    tags=["Pneumonia Prediction"],
)


# =========================================================
# 1. 폐렴 AI 예측 실행
# =========================================================
@router.post(
    "/medical-records/{record_id}/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="폐렴 AI 예측 실행",
)
async def execute_pneumonia_prediction(
    record_id: int = Path(..., ge=1, description="진료기록 ID"),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    진료기록에 등록된 X-ray 이미지를 이용해 폐렴 AI 예측을 실행합니다.

    같은 진료기록에 같은 AI 모델의 예측 결과가 이미 존재하면
    AI 모델을 다시 실행하지 않고 기존 DB 결과를 반환합니다.
    """

    prediction = await prediction_service.execute_prediction(
        db=db,
        record_id=record_id,
        current_user=current_user,
    )

    return prediction


# =========================================================
# 2. 진료기록별 폐렴 예측 결과 조회
# =========================================================
@router.get(
    "/medical-records/{record_id}/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="진료기록별 폐렴 예측 결과 조회",
)
async def get_prediction_result(
    record_id: int = Path(..., ge=1, description="진료기록 ID"),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    해당 진료기록에 저장되어 있는 폐렴 AI 예측 결과를 조회합니다.

    이 API에서는 AI 모델을 다시 실행하지 않습니다.
    DB에 저장된 결과만 반환합니다.
    """

    prediction = await prediction_service.get_prediction_result(
        db=db,
        record_id=record_id,
        current_user=current_user,
    )

    return prediction


# =========================================================
# 3. 환자별 X-ray + AI 예측 결과 목록 조회
# =========================================================
@router.get(
    "/patients/{patient_id}/predictions",
    response_model=PatientXrayAnalysisListResponse,
    status_code=status.HTTP_200_OK,
    summary="환자별 X-ray 및 AI 예측 결과 목록 조회",
)
async def get_patient_prediction_list(
    patient_id: int = Path(..., ge=1, description="환자 ID"),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="조회할 최대 항목 수",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="조회 시작 위치",
    ),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    선택한 환자의 진료기록을 기준으로
    X-ray 이미지와 폐렴 AI 예측 결과 목록을 조회합니다.
    """

    result = await prediction_service.get_patient_xray_analysis_list(
        db=db,
        patient_id=patient_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )

    return result