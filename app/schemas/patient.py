# Backward-compatibility bridge
from app.schemas.patients import (
    PatientResponse,
    PatientUpdateRequest,
    PatientCreateRequest,
    PatientInfoPageResponse,
    PatientInfoUpdateRequest,
    GENDER_MAP,
)

__all__ = [
    "PatientResponse",
    "PatientUpdateRequest",
    "PatientCreateRequest",
    "PatientInfoPageResponse",
    "PatientInfoUpdateRequest",
    "GENDER_MAP",
]
