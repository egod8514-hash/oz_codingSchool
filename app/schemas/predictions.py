from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class PredictionResponse(BaseModel):
    """
    진료기록별 폐렴 예측 결과 단건 응답 스키마 (팀원 3 호환)
    """
    record_id: int
    is_pneumonia: bool
    confidence: float
    ai_model: str
    heatmap_url: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PatientXrayAnalysisItem(BaseModel):
    """
    환자별 X-ray 및 AI 예측 결과 항목 스키마 (팀원 4)
    """
    record_id: int = Field(..., description="진료기록 ID")
    chart_number: str = Field(..., description="차트 번호")
    symptoms: Optional[str] = Field(None, description="증상")
    xray_id: Optional[int] = Field(None, description="X-ray 이미지 ID")
    xray_image_url: Optional[str] = Field(None, description="X-ray 이미지 경로/URL")
    shooting_datetime: Optional[datetime] = Field(None, description="X-ray 촬영 일시")

    # AI 예측 결과 (AnalysisResultModel 매핑)
    prediction_id: Optional[int] = Field(None, description="예측 분석 ID")
    is_pneumonia: Optional[bool] = Field(None, description="폐렴 진단 여부 (True: 양성, False: 음성)")
    confidence: Optional[float] = Field(None, description="예측 신뢰도")
    heatmap_url: Optional[str] = Field(None, description="병변 표시 히트맵 이미지 경로/URL")
    ai_model: Optional[str] = Field(None, description="사용된 AI 모델명")
    analyzed_at: Optional[datetime] = Field(None, description="예측 분석 일시")

    model_config = ConfigDict(from_attributes=True)


class PatientXrayAnalysisListResponse(BaseModel):
    """
    환자별 X-ray + 예측 결과 목록 조회 응답 스키마 (팀원 4)
    """
    patient_id: int = Field(..., description="환자 ID")
    patient_name: str = Field(..., description="환자 이름")
    total_count: int = Field(..., description="전체 항목 개수")
    predictions: List[PatientXrayAnalysisItem] = Field(
        default_factory=list,
        description="X-ray 및 예측 결과 목록"
    )
    items: List[PatientXrayAnalysisItem] = Field(
        default_factory=list,
        description="호환용 목록"
    )

    model_config = ConfigDict(from_attributes=True)
