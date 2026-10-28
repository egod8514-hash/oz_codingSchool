from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionResponse(BaseModel):
    """
    진료기록별 폐렴 예측 결과 응답 스키마
    """
    record_id: int = Field(..., description="연관된 진료기록(Medical Record) ID")
    is_pneumonia: bool = Field(..., description="폐렴 여부 (True: 폐렴, False: 정상)")
    confidence: float = Field(..., description="AI 모델의 예측 신뢰도/확률 (0.0 ~ 1.0)")
    ai_model: str = Field(..., description="분석에 사용된 AI 모델 명칭 및 버전")
    heatmap_url: Optional[str] = Field(None, description="폐렴 활성화 영역 히트맵 이미지 URL")
    created_at: datetime = Field(..., description="예측 결과 생성 일시")  # 필수 필드로 수정 [3, 6]

    # Pydantic v2 ORM 매핑 설정 [6]
    model_config = ConfigDict(from_attributes=True)