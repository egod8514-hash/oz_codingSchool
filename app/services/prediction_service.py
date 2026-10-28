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

async def save_prediction_pre_check(
    db : AsyncSession,
    record_id : int,
    current_user : UserModel,
    ai_model : str,
) : 
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

    # 조기 종료를 위한 ai예측 데이터 반환
    yield prediction

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

    yield xray

async def save_prediction_post(
    db : AsyncSession,
    record_id : int,
    # TODO : ai예측 모델
    prediction_model : None,
) : 
    # DB 저장
    insert_stmt = insert(AnalysisResultModel).values(
        record_id = record_id,
        # TODO : ai모델 예측 정보
        is_pneumonia = None,
        confidence = 0.0,
        heatmap_url = None,
        ai_model = "PneumoniaModel-v1",
    )

    await db.execute(insert_stmt)
    await db.commit()