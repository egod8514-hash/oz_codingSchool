from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MedicalRecordCreateForm(BaseModel):
    """진료기록 텍스트 필드 검증용 스키마.

    실제 multipart/form-data에서는 FastAPI의 Form(...)으로 값을 받은 뒤
    이 스키마로 한 번 더 검증한다.
    """

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

from pydantic import BaseModel, ConfigDict


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    created_at: datetime
    xray_image_path: str


class DeletePatientResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)


class MedicalRecordListResponse(BaseModel):
    medical_records: list[MedicalRecordResponse]
