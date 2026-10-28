from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.users import UserModel
from app.models.patients import PatientModel
from app.models.medical_records import MedicalRecordModel
from app.models.xray_images import XrayImagesModel
from app.schemas.medical_record import (
    MedicalRecordListResponse,
    MedicalRecordResponse,
    MedicalRecordCreateForm,
)
from app.services import medical_record_service

router = APIRouter(tags=["Medical Records"])

UPLOAD_DIR = Path("media") / "xray"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}


async def _save_medical_record(
    patient_id: int,
    chart_number: str,
    symptoms: str,
    xray_image: UploadFile,
    db: AsyncSession,
    current_user: UserModel,
) -> MedicalRecordResponse:
    form = MedicalRecordCreateForm(
        chart_number=chart_number,
        symptoms=symptoms,
    )

    if xray_image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JPG 또는 PNG 이미지만 업로드할 수 있습니다.",
        )

    patient_result = await db.execute(
        select(PatientModel).where(PatientModel.id == patient_id)
    )
    patient = patient_result.scalar_one_or_none()

    if patient is None or patient.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 환자를 찾을 수 없습니다.",
        )

    duplicate_result = await db.execute(
        select(MedicalRecordModel).where(
            MedicalRecordModel.chart_number == form.chart_number
        )
    )
    if duplicate_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 차트 번호입니다.",
        )

    suffix = Path(xray_image.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        suffix = ".jpg" if xray_image.content_type == "image/jpeg" else ".png"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"

    try:
        stored_path.write_bytes(await xray_image.read())

        record = MedicalRecordModel(
            patient_id=patient_id,
            chart_number=form.chart_number,
            symptoms=form.symptoms,
        )
        db.add(record)
        await db.flush()

        image = XrayImagesModel(
            record_id=record.id,
            uploader_id=current_user.id,
            image_url=str(stored_path).replace("\\", "/"),
        )
        db.add(image)

        await db.commit()
        await db.refresh(record)
        await db.refresh(image)

    except IntegrityError:
        await db.rollback()
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="차트 번호가 이미 존재하거나 DB 제약조건을 위반했습니다.",
        )
    except Exception:
        await db.rollback()
        stored_path.unlink(missing_ok=True)
        raise

    return MedicalRecordResponse(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        created_at=record.created_at,
        xray_image_path=image.image_url,
    )


@router.post(
    "/api/v1/patients/{patient_id}/medical-records",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환자 진료기록 및 X-Ray 등록 (경로 매개변수)",
)
async def create_patient_medical_record(
    patient_id: int,
    chart_number: str = Form(..., min_length=1, max_length=50),
    symptoms: str = Form(..., min_length=1),
    xray_image: UploadFile = File(...),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
) -> MedicalRecordResponse:
    return await _save_medical_record(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
        xray_image=xray_image,
        db=db,
        current_user=current_user,
    )


@router.post(
    "/api/v1/medical-records",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환자 진료기록 및 X-Ray 등록 (폼 필드)",
)
async def create_medical_record(
    patient_id: int = Form(...),
    chart_number: str = Form(..., min_length=1, max_length=50),
    symptoms: str = Form(..., min_length=1),
    xray_image: UploadFile = File(...),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
) -> MedicalRecordResponse:
    return await _save_medical_record(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms,
        xray_image=xray_image,
        db=db,
        current_user=current_user,
    )


@router.get(
    "/api/v1/patients/{patient_id}/medical-records",
    response_model=MedicalRecordListResponse,
    summary="환자별 진료기록 목록 조회",
)
async def get_medical_records(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
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

    items = []
    for r in records:
        img_path = r.xray_images[0].image_url if r.xray_images else None
        items.append(
            MedicalRecordResponse(
                id=r.id,
                patient_id=r.patient_id,
                chart_number=r.chart_number,
                symptoms=r.symptoms,
                created_at=r.created_at,
                xray_image_path=img_path,
            )
        )

    return {
        "medical_records": items
    }


@router.get(
    "/api/v1/medical-records/{record_id}",
    response_model=MedicalRecordResponse,
    summary="진료기록 상세 정보 단건 조회",
)
async def get_medical_record(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
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

    img_path = record.xray_images[0].image_url if record.xray_images else None
    return MedicalRecordResponse(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        created_at=record.created_at,
        xray_image_path=img_path,
    )
