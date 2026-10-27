from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.schemas.medical_record import (
    MedicalRecordListResponse,
    MedicalRecordResponse,
)
from app.services import medical_record_service


router = APIRouter(
    tags=["Medical Records"],
)


@router.get(
    "/api/v1/patients/{patient_id}/medical-records",
    response_model=MedicalRecordListResponse,
)
async def get_medical_records(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
):
    records = await medical_record_service.get_medical_records_by_patient(
        db=db,
        patient_id=patient_id,
    )

    if records is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다.",
        )

    return {
        "medical_records": records
    }


@router.get(
    "/api/v1/medical-records/{record_id}",
    response_model=MedicalRecordResponse,
)
async def get_medical_record(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
):
    record = await medical_record_service.get_medical_record(
        db=db,
        record_id=record_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="진료기록을 찾을 수 없습니다.",
        )

    return record