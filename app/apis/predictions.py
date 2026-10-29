from worker import model
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

@router.post(
    "/medical-records/{record_id}/predictions"
)
async def save_prediction(
    record_id : int,
    db : AsyncSession = Depends(async_get_db),
    current_user : UserModel = Depends(get_current_user),
) : 
    # 전처리 : 권한 여부, 데이터 유무 확인
    prediction = prediction_service.save_prediction_pre(
        db,
        record_id,
        current_user,
        model.MODEL_NAME,
    )

    if not prediction is None : 
        return {
            "record_id" : prediction.record_id,
            "is_pneumonia" : prediction.is_pneumonia,
            "confidence" : prediction.confidence,
            "ai_model" : prediction.ai_model,
        }

    # AI예측
    # TODO : 병변 히트맵 이미지 URL
    prediction = prediction_service.prediction()

    # 후처리 : AnalysisResultModel 결과 저장
    prediction_service.save_prediction_post(
        db,
        record_id,
        prediction,
    )

    # 예측 결과 반환
    return {
        "is_pneumonia" : prediction["is_pneumonia"],
        "confidence" : prediction["confidence"],
        "heatmap_url" : prediction["heatmap_url"],
    }
