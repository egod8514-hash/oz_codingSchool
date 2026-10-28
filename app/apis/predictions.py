from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.predictions import PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(
    prefix="/api/v1/medical-records",
    tags=["Predictions"]
)


@router.get(
    "/{record_id}/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="진료기록별 폐렴 예측 결과 GET 조회"
)
def get_prediction_result(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 진료기록(record_id)의 저장된 폐렴 예측 결과를 DB에서 조회합니다.
    - GET 요청 시 AI 모델을 다시 실행하지 않고 DB 결과를 반환합니다.
    """
    service = PredictionService(db)
    return service.get_prediction_result(record_id)
