from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class MedicalRecordCreateForm(BaseModel):
    """진료기록 텍스트 필드 검증용 스키마."""

    chart_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="진료 차트 번호",
    )
    symptoms: str = Field(
        ...,
        min_length=1,
        description="진료된 증상",
    )


class XrayImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    shooting_datetime: datetime


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    created_at: datetime
    xray_image_path: Optional[str] = None


class DeletePatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message: str


class MedicalRecordListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medical_records: List[MedicalRecordResponse]
