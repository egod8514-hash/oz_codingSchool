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
    gen = prediction_service.save_prediction_pre(
        db,
        record_id,
        current_user,
        "PneumoniaModel-v1", # TODO : ai모델명
    )
    
    # 전처리1
    prediction = await anext(gen)

    if not prediction is None : 
        return {
            "record_id" : prediction.record_id,
            "is_pneumonia" : prediction.is_pneumonia,
            "confidence" : prediction.confidence,
            "ai_model" : prediction.ai_model,
        }

    # 전처리2
    xray = await anext(gen)

    # TODO : AI모델 실행
    prediction_model = None

    # AnalysisResultModel 결과 저장
    prediction = prediction_service.save_prediction_post(
        db,
        record_id,
        prediction_model,
    )

    # 예측 결과 반환
    return {
        "record_id" : prediction.record_id,
        "is_pneumonia" : prediction.is_pneumonia,
        "confidence" : prediction.confidence,
        "ai_model" : prediction.ai_model,
    }
