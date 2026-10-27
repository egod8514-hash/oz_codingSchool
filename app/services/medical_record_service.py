from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patients import PatientModel
from app.models.medical_records import MedicalRecordModel


async def get_medical_records_by_patient(
    db: AsyncSession,
    patient_id: int,
):
    # 환자 존재 여부 확인
    patient_query = select(PatientModel).where(
        PatientModel.id == patient_id,
        PatientModel.is_deleted.is_(False),
    )

    patient_result = await db.execute(patient_query)
    patient = patient_result.scalar_one_or_none()

    if patient is None:
        return None

    # 해당 환자의 진료기록 목록 조회
    record_query = select(MedicalRecordModel).where(
        MedicalRecordModel.patient_id == patient_id,
        MedicalRecordModel.is_deleted.is_(False),
    )

    record_result = await db.execute(record_query)

    return record_result.scalars().all()


async def get_medical_record(
    db: AsyncSession,
    record_id: int,
):
    query = select(MedicalRecordModel).where(
        MedicalRecordModel.id == record_id,
        MedicalRecordModel.is_deleted.is_(False),
    )

    result = await db.execute(query)

    return result.scalar_one_or_none()