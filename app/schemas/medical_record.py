from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicalRecordListResponse(BaseModel):
    medical_records: list[MedicalRecordResponse]