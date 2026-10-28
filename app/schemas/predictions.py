from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    """
    진료기록별 폐렴 예측 결과 응답 스키마
    """
    record_id: int
    is_pneumonia: bool
    confidence: float
    ai_model: str
    heatmap_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
