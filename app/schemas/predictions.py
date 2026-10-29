from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PredictionResponse(BaseModel):
    """
    진료기록별 폐렴 예측 결과 응답
    """
    record_id: int = Field(..., description="진료기록 ID")
    is_pneumonia: bool = Field(
        ...,
        description="폐렴 여부 (True: 폐렴, False: 정상)",
    )
    confidence: float = Field(
        ...,
        description="AI 모델 예측 신뢰도",
    )
    ai_model: str = Field(
        ...,
        description="분석에 사용된 AI 모델명",
    )
    heatmap_url: Optional[str] = Field(
        None,
        description="폐렴 활성화 영역 히트맵 이미지 URL",
    )
    created_at: Optional[datetime] = Field(
        None,
        description="예측 결과 생성 일시",
    )

    model_config = ConfigDict(from_attributes=True)


class PatientXrayAnalysisItem(BaseModel):
    """
    환자별 X-ray 및 AI 예측 결과 항목
    """
    record_id: int = Field(..., description="진료기록 ID")
    chart_number: str = Field(..., description="차트 번호")
    symptoms: Optional[str] = Field(None, description="증상")

    xray_id: Optional[int] = Field(
        None,
        description="X-ray 이미지 ID",
    )
    xray_image_url: Optional[str] = Field(
        None,
        description="X-ray 이미지 경로/URL",
    )
    shooting_datetime: Optional[datetime] = Field(
        None,
        description="X-ray 촬영 일시",
    )

    prediction_id: Optional[int] = Field(
        None,
        description="AI 예측 결과 ID",
    )
    is_pneumonia: Optional[bool] = Field(
        None,
        description="폐렴 여부",
    )
    confidence: Optional[float] = Field(
        None,
        description="AI 모델 예측 신뢰도",
    )
    heatmap_url: Optional[str] = Field(
        None,
        description="히트맵 이미지 URL",
    )
    ai_model: Optional[str] = Field(
        None,
        description="사용된 AI 모델명",
    )
    analyzed_at: Optional[datetime] = Field(
        None,
        description="AI 분석 일시",
    )

    model_config = ConfigDict(from_attributes=True)


class PatientXrayAnalysisListResponse(BaseModel):
    """
    환자별 X-ray + AI 예측 결과 목록 응답
    """
    patient_id: int = Field(..., description="환자 ID")
    patient_name: str = Field(..., description="환자 이름")
    total_count: int = Field(..., description="전체 항목 개수")

    predictions: List[PatientXrayAnalysisItem] = Field(
        default_factory=list,
        description="X-ray 및 AI 예측 결과 목록",
    )

    model_config = ConfigDict(from_attributes=True)