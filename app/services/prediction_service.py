from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserModel
from app.models.patients import PatientModel
from app.models.medical_records import MedicalRecordModel
from app.core.enum.enum_role import RoleEnum
from app.schemas.predictions import (
    PatientXrayAnalysisItem,
    PatientXrayAnalysisListResponse,
)


async def get_patient_xray_analysis_list(
    db: AsyncSession,
    patient_id: int,
    current_user: UserModel,
    only_analyzed: bool = False,
) -> PatientXrayAnalysisListResponse:
    """
    [팀원 4] 환자별 X-ray + 예측 결과 목록 GET 조회
    - 환자 존재 여부 검증 (없을 시 404)
    - 권한 확인 (PENDING 권한 차단)
    - 환자의 진료기록, X-ray 이미지, AI 분석 결과를 함께 조회하여 매핑
    """
    # 1. 권한 검증: 승인 대기자(PENDING) 접근 차단
    if getattr(current_user, "role", None) == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="승인 대기 중인 사용자는 조회가 불가능합니다.",
        )

    # 2. 환자 존재 여부 확인
    patient_stmt = select(PatientModel).where(
        PatientModel.id == patient_id,
        PatientModel.is_deleted.is_(False),
    )
    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 환자를 찾을 수 없습니다.",
        )

    # 3. 환자의 진료기록, X-ray 이미지, 예측 분석 결과 목록 조회 (Eager loading)
    records_stmt = (
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
    records_result = await db.execute(records_stmt)
    records = records_result.scalars().all()

    # 4. X-ray + 예측 결과 리스트 구성
    items: List[PatientXrayAnalysisItem] = []

    for record in records:
        # 진료기록에 등록된 X-ray 이미지 정보 확인
        xray = record.xray_images[0] if record.xray_images else None
        xray_id = xray.id if xray else None
        xray_url = xray.image_url if xray else None
        shooting_dt = xray.shooting_datetime if xray else None

        # 유효한(삭제되지 않은) 예측 결과 필터링
        analyses = [
            a for a in (record.analysis_results or [])
            if not getattr(a, "is_deleted", False)
        ]

        if analyses:
            for analysis in analyses:
                confidence_val = (
                    float(analysis.confidence)
                    if analysis.confidence is not None
                    else None
                )
                items.append(
                    PatientXrayAnalysisItem(
                        record_id=record.id,
                        chart_number=record.chart_number,
                        symptoms=record.symptoms,
                        xray_id=xray_id,
                        xray_image_url=xray_url,
                        shooting_datetime=shooting_dt,
                        prediction_id=analysis.id,
                        is_pneumonia=analysis.is_pneumonia,
                        confidence=confidence_val,
                        heatmap_url=analysis.heatmap_url,
                        ai_model=analysis.ai_model,
                        analyzed_at=analysis.created_at,
                    )
                )
        elif not only_analyzed:
            # 예측 결과가 아직 없더라도 X-ray가 등록되어 있으면 목록에 포함
            items.append(
                PatientXrayAnalysisItem(
                    record_id=record.id,
                    chart_number=record.chart_number,
                    symptoms=record.symptoms,
                    xray_id=xray_id,
                    xray_image_url=xray_url,
                    shooting_datetime=shooting_dt,
                    prediction_id=None,
                    is_pneumonia=None,
                    confidence=None,
                    heatmap_url=None,
                    ai_model=None,
                    analyzed_at=None,
                )
            )

    return PatientXrayAnalysisListResponse(
        patient_id=patient.id,
        patient_name=patient.name,
        total_count=len(items),
        predictions=items,
        items=items,
    )
