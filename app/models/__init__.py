from app.models import (
    base,
    users,
    patients,
    xray_images,
    medical_records,
    ai_analysis_results,
)

_models = (
    base.BaseModel,
    users.UserModel,
    patients.PatientModel,
    xray_images.XrayImagesModel,
    medical_records.MedicalRecordModel,
    ai_analysis_results.AnalysisResultModel,
)

__all__ = [model.__name__ for model in _models]