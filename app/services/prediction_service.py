from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserModel
from app.models.patients import PatientModel
from app.models.medical_records import MedicalRecordModel
from app.models.xray_images import XrayImagesModel
from app.models.ai_analysis_results import AnalysisResultModel
from app.core.enum.enum_role import RoleEnum
from app.schemas.predictions import (
    PatientXrayAnalysisItem,
    PatientXrayAnalysisListResponse,
)
from worker.model import predictor

async def save_prediction_pre_check(
    db : AsyncSession,
    record_id : int,
    current_user : UserModel,
    ai_model : str,
) -> AnalysisResultModel : 
    # 권한 검증 : 승인 대기자 접근 차단
    if current_user.role == RoleEnum.PENDING : 
        raise HTTPException(
            status_code = status.HTTO_403_FORBIDDEN,
            detail = "승인 대기 중인 사용자는 조회가 불가능합니다."
        )

    # 진료 기록 확인
    record_stmt = select(MedicalRecordModel).where(
        MedicalRecordModel.id == record_id,
        MedicalRecordModel.is_deleted.is_(False),
    )
    record_result = await db.execute(record_stmt)
    record = record_result.scalar_one_or_none()

    if record is None : 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "의료 레코드를 찾을 수 없습니다."
        )
    
    # 기존 예측 결과 확인
    prediction_stmt = select(AnalysisResultModel).where(
        AnalysisResultModel.record_id == record_id,
        AnalysisResultModel.ai_model == ai_model,
        AnalysisResultModel.is_deleted.is_(False),
    )
    prediction_result = await db.execute(prediction_stmt)
    prediction = prediction_result.scalar_one_or_none()

    return prediction

async def prediction(
    record_id : int
) -> dict : 
    # X-ray 이미지 확인
    xray_stmt = select(XrayImagesModel).where(
        XrayImagesModel.record_id == record_id,
        XrayImagesModel.is_deleted.is_(False),
    )
    xray_result = await db.execute(xray_stmt)
    xray = xray_result.scalar_one_or_none()

    if xray is None : 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "X-ray 레코드를 찾을 수 없습니다."
        )

    # X-ray 경로 확인
    image_path = Path(xray.image_url)

    if not image_path.exists() : 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "X-ray 이미지 파일을 찾을 수 없습니다."
        )

    # X-ray 이미지 불러오기
    try : 
        image_bytes = image_path.read_bytes()
    except OSError : 
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "X-ray 이미지를 읽을 수 없습니다."
        )

    # AI모델 예측
    try : 
        return predictor.predict(image_bytes)
    except Exception as e : 
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"폐렴 AI 예측 중 오류가 발생했습니다. : ¥n{str(e)}"
        )


async def save_prediction_post(
    db : AsyncSession,
    record_id : int,
    prediction : dict,
) : 
    # DB 저장
    insert_stmt = insert(AnalysisResultModel).values(
        record_id = record_id,
        is_pneumonia = prediction["is_pneumonia"],
        confidence = prediction["confidence"],
        heatmap_url = prediction["heatmap_url"],
        ai_model = prediction["model_name"],
    )

    await db.execute(insert_stmt)
    await db.commit()