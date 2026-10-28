from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.medical_records import MedicalRecordModel
from app.models.patients import PatientModel
from app.models.users import UserModel
from app.models.xray_images import XrayImagesModel
from app.schemas.medical_record import (
    DeletePatientResponse,
    MedicalRecordCreateForm,
    MedicalRecordResponse,
)

router = APIRouter(
    prefix="/practice_api",
    tags=["Patients / Medical Records"],
)

UPLOAD_DIR = Path("media") / "xray"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}


@router.delete(
    "/patients/{patient_id}",
    response_model=DeletePatientResponse,
    status_code=status.HTTP_200_OK,
    summary="환자와 관련된 진료기록 및 X-Ray 삭제",
)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
) -> DeletePatientResponse:
    """환자와 연결된 DB 데이터 및 로컬 X-Ray 파일을 삭제한다.

    실제 프로젝트의 역할 권한은 팀 공통 dependency 또는 service에서
    추가로 확인해야 한다.
    """
    del current_user  # TODO: 팀의 role 권한 검사로 교체

    result = await db.execute(
        select(PatientModel)
        .options(
            selectinload(PatientModel.medical_records).selectinload(
                MedicalRecordModel.xray_images
            )
        )
        .where(PatientModel.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 환자를 찾을 수 없습니다.",
        )

    image_paths = [
        Path(image.image_url)
        for record in patient.medical_records
        for image in record.xray_images
    ]

    try:
        # PatientModel의 cascade 설정에 따라 연관 DB 데이터도 삭제된다.
        await db.delete(patient)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    # DB commit 성공 뒤 실제 로컬 파일을 정리한다.
    for image_path in image_paths:
        try:
            image_path.unlink(missing_ok=True)
        except OSError:
            # 실제 프로젝트에서는 logger로 기록할 것
            pass

    return DeletePatientResponse(
        message="환자와 관련된 진료기록 및 X-Ray가 삭제되었습니다."
    )


@router.post(
    "/patients/{patient_id}/medical-records",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환자 진료기록 및 X-Ray 등록",
)
async def create_medical_record(
    patient_id: int,
    chart_number: str = Form(..., min_length=1, max_length=50),
    symptoms: str = Form(..., min_length=1),
    xray_image: UploadFile = File(...),
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
) -> MedicalRecordResponse:
    """multipart/form-data로 진료기록과 X-Ray 한 장을 등록한다."""
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

    if patient is None:
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
        await db.flush()  # record.id 생성

        image = XrayImagesModel(
            record_id=record.id,
            uploader_id=current_user.id,
            image_url=str(stored_path),
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
