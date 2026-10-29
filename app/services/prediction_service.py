from pathlib import Path
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum.enum_role import RoleEnum
from app.models.ai_analysis_results import AnalysisResultModel
from app.models.medical_records import MedicalRecordModel
from app.models.patients import PatientModel
from app.models.users import UserModel
from app.models.xray_images import XrayImagesModel
from app.schemas.predictions import (
    PatientXrayAnalysisItem,
    PatientXrayAnalysisListResponse,
    PredictionResponse,
)


# =========================================================
# 공통 권한 확인
# =========================================================
def check_prediction_permission(current_user: UserModel) -> None:
    if current_user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 AI 예측 기능을 사용할 수 없습니다.",
        )


# =========================================================
# 진료기록 존재 여부 확인
# =========================================================
async def get_medical_record(
    db: AsyncSession,
    record_id: int,
) -> MedicalRecordModel:

    stmt = select(MedicalRecordModel).where(
        MedicalRecordModel.id == record_id,
        MedicalRecordModel.is_deleted.is_(False),
    )

    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="진료기록을 찾을 수 없습니다.",
        )

    return record


# =========================================================
# 같은 진료기록 + 같은 모델의 기존 예측 결과 확인
# =========================================================
async def get_existing_prediction(
    db: AsyncSession,
    record_id: int,
    ai_model: str,
):
    stmt = (
        select(AnalysisResultModel)
        .where(
            AnalysisResultModel.record_id == record_id,
            AnalysisResultModel.ai_model == ai_model,
            AnalysisResultModel.is_deleted.is_(False),
        )
        .order_by(AnalysisResultModel.id.desc())
    )

    result = await db.execute(stmt)

    return result.scalars().first()


# =========================================================
# 실제 AI 폐렴 예측
# =========================================================
async def run_prediction(
    db: AsyncSession,
    record_id: int,
) -> dict:

    # 가장 최근 X-ray 조회
    stmt = (
        select(XrayImagesModel)
        .where(
            XrayImagesModel.record_id == record_id,
            XrayImagesModel.is_deleted.is_(False),
        )
        .order_by(XrayImagesModel.id.desc())
    )

    result = await db.execute(stmt)
    xray = result.scalars().first()

    if xray is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 X-ray 이미지가 없습니다.",
        )

    # X-ray 파일 경로 확인 (앞에 '/'가 붙어있어도 로컬 상대 경로로 탐색)
    raw_url = xray.image_url.lstrip("/")
    image_path = Path(raw_url)

    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="X-ray 이미지 파일을 찾을 수 없습니다.",
        )

    # 이미지 bytes 읽기
    try:
        image_bytes = image_path.read_bytes()

    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="X-ray 이미지 파일을 읽을 수 없습니다.",
        )

    # 실제 AI 모델 실행
    try:
        from worker.model import predictor

        prediction = predictor.predict(image_bytes)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"폐렴 AI 예측 중 오류가 발생했습니다: {str(e)}",
        )

    return prediction


# =========================================================
# AI 예측 결과 DB 저장
# =========================================================
async def save_prediction(
    db: AsyncSession,
    record_id: int,
    prediction: dict,
) -> AnalysisResultModel:

    analysis_result = AnalysisResultModel(
        record_id=record_id,
        is_pneumonia=prediction["is_pneumonia"],
        confidence=prediction["confidence"],
        heatmap_url=prediction.get("heatmap_url") or "",
        ai_model=prediction["model_name"],
    )

    db.add(analysis_result)

    await db.commit()
    await db.refresh(analysis_result)

    return analysis_result


# =========================================================
# POST 전체 처리
# =========================================================
async def execute_prediction(
    db: AsyncSession,
    record_id: int,
    current_user: UserModel,
) -> PredictionResponse:

    check_prediction_permission(current_user)

    # 진료기록 존재 여부 확인
    await get_medical_record(
        db=db,
        record_id=record_id,
    )

    ai_model = "PneumoniaModel-v1"

    # 같은 진료기록 + 같은 모델 결과가 이미 있는지 확인
    existing_prediction = await get_existing_prediction(
        db=db,
        record_id=record_id,
        ai_model=ai_model,
    )

    # 이미 존재하면 AI를 다시 실행하지 않는다.
    if existing_prediction is not None:
        return make_prediction_response(existing_prediction)

    # 실제 AI 예측 실행
    prediction_result = await run_prediction(
        db=db,
        record_id=record_id,
    )

    ai_model = prediction_result["model_name"]

    existing_prediction = await get_existing_prediction(
        db=db,
        record_id=record_id,
        ai_model=ai_model,
    )

    if existing_prediction is not None:
        return make_prediction_response(existing_prediction)

    # DB 저장
    saved_prediction = await save_prediction(
        db=db,
        record_id=record_id,
        prediction=prediction_result,
    )

    return make_prediction_response(saved_prediction)


# =========================================================
# GET: 진료기록별 저장된 폐렴 예측 결과 단건 조회
# =========================================================
async def get_prediction_result(
    db: AsyncSession,
    record_id: int,
    current_user: UserModel,
) -> PredictionResponse:

    check_prediction_permission(current_user)

    # 진료기록 존재 여부 확인
    await get_medical_record(
        db=db,
        record_id=record_id,
    )

    stmt = (
        select(AnalysisResultModel)
        .where(
            AnalysisResultModel.record_id == record_id,
            AnalysisResultModel.is_deleted.is_(False),
        )
        .order_by(AnalysisResultModel.id.desc())
    )

    result = await db.execute(stmt)
    prediction = result.scalars().first()

    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="저장된 AI 예측 결과가 없습니다.",
        )

    return make_prediction_response(prediction)


# =========================================================
# GET: 진료기록별 저장된 폐렴 예측 결과 전체 목록 조회 (프론트 호환)
# =========================================================
async def get_prediction_result_list(
    db: AsyncSession,
    record_id: int,
    current_user: UserModel,
) -> List[PredictionResponse]:

    check_prediction_permission(current_user)

    await get_medical_record(
        db=db,
        record_id=record_id,
    )

    stmt = (
        select(AnalysisResultModel)
        .where(
            AnalysisResultModel.record_id == record_id,
            AnalysisResultModel.is_deleted.is_(False),
        )
        .order_by(AnalysisResultModel.id.desc())
    )

    result = await db.execute(stmt)
    predictions = result.scalars().all()

    return [make_prediction_response(p) for p in predictions]


# =========================================================
# AnalysisResultModel → PredictionResponse
# =========================================================
def make_prediction_response(
    prediction: AnalysisResultModel,
) -> PredictionResponse:

    return PredictionResponse(
        record_id=prediction.record_id,
        is_pneumonia=prediction.is_pneumonia,
        confidence=float(prediction.confidence),
        ai_model=prediction.ai_model,
        heatmap_url=prediction.heatmap_url or None,
        created_at=prediction.created_at,
    )


# =========================================================
# 환자별 X-ray + AI 예측 결과 목록
# =========================================================
async def get_patient_xray_analysis_list(
    db: AsyncSession,
    patient_id: int,
    current_user: UserModel,
    limit: int = 20,
    offset: int = 0,
) -> PatientXrayAnalysisListResponse:

    check_prediction_permission(current_user)

    # 환자 존재 여부 확인
    patient_stmt = select(PatientModel).where(
        PatientModel.id == patient_id,
        PatientModel.is_deleted.is_(False),
    )

    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="환자를 찾을 수 없습니다.",
        )

    # 환자의 진료기록 + X-ray + AI 결과 조회
    record_stmt = (
        select(MedicalRecordModel)
        .options(
            selectinload(MedicalRecordModel.xray_images),
            selectinload(MedicalRecordModel.analysis_results),
        )
        .where(
            MedicalRecordModel.patient_id == patient_id,
            MedicalRecordModel.is_deleted.is_(False),
        )
        .order_by(MedicalRecordModel.id.desc())
    )

    record_result = await db.execute(record_stmt)
    all_records = record_result.scalars().unique().all()

    total_count = len(all_records)
    records = all_records[offset : offset + limit]

    items = []

    for record in records:
        xrays = [
            xray
            for xray in record.xray_images
            if not xray.is_deleted
        ]
        latest_xray = (
            max(xrays, key=lambda x: x.id)
            if xrays
            else None
        )

        predictions = [
            prediction
            for prediction in record.analysis_results
            if not prediction.is_deleted
        ]
        latest_prediction = (
            max(predictions, key=lambda x: x.id)
            if predictions
            else None
        )

        raw_xray_url = latest_xray.image_url if latest_xray else None
        normalized_xray_url = (
            "/" + raw_xray_url.lstrip("/")
            if raw_xray_url
            else None
        )

        item = PatientXrayAnalysisItem(
            record_id=record.id,
            chart_number=record.chart_number,
            symptoms=record.symptoms,
            xray_id=latest_xray.id if latest_xray else None,
            xray_image_url=normalized_xray_url,
            shooting_datetime=latest_xray.shooting_datetime if latest_xray else None,
            prediction_id=latest_prediction.id if latest_prediction else None,
            is_pneumonia=latest_prediction.is_pneumonia if latest_prediction else None,
            confidence=float(latest_prediction.confidence) if latest_prediction else None,
            heatmap_url=(latest_prediction.heatmap_url or None) if latest_prediction else None,
            ai_model=latest_prediction.ai_model if latest_prediction else None,
            analyzed_at=latest_prediction.created_at if latest_prediction else None,
        )

        items.append(item)

    return PatientXrayAnalysisListResponse(
        patient_id=patient.id,
        patient_name=patient.name,
        total_count=total_count,
        predictions=items,
    )
