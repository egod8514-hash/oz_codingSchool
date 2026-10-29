from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user
from app.models.users import UserModel
from app.models.medical_records import MedicalRecordModel
from app.models.xray_images import XrayImagesModel
from app.schemas.prediction import PredictionExecuteResponse




router = APIRouter(
    prefix="/api/v1",
    tags=["Pneumonia Prediction"],
)


@router.post(
    "/medical-records/{record_id}/predictions",
    response_model=PredictionExecuteResponse,
    status_code=status.HTTP_200_OK,
    summary="폐렴 AI 예측 실행",
)
async def execute_pneumonia_prediction(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    current_user: UserModel = Depends(get_current_user),
):
    # 1. 진료기록 확인
    record_result = await db.execute(
        select(MedicalRecordModel).where(
            MedicalRecordModel.id == record_id,
            MedicalRecordModel.is_deleted.is_(False),
        )
    )

    record = record_result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="진료기록을 찾을 수 없습니다.",
        )

    # 2. 해당 진료기록의 X-ray 이미지 조회
    xray_result = await db.execute(
        select(XrayImagesModel)
        .where(
            XrayImagesModel.record_id == record_id,
            XrayImagesModel.is_deleted.is_(False),
        )
        .order_by(XrayImagesModel.id.desc())
    )

    xray = xray_result.scalars().first()

    if xray is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 X-ray 이미지가 없습니다.",
        )

    # 3. 실제 X-ray 파일 경로 확인
    image_path = Path(xray.image_url)

    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="X-ray 이미지 파일을 찾을 수 없습니다.",
        )

    # 4. X-ray 이미지를 bytes로 읽기
    try:
        image_bytes = image_path.read_bytes()
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="X-ray 이미지 파일을 읽을 수 없습니다.",
        )

    # 5. AI 모델로 폐렴 예측
    try:
         from worker.model import predictor

         prediction = predictor.predict(image_bytes)

    except Exception as e:
        raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"폐렴 AI 예측 중 오류가 발생했습니다: {str(e)}",
    )
   
    # 6. 예측 결과 반환
    return PredictionExecuteResponse(
        record_id=record_id,
        is_pneumonia=prediction["is_pneumonia"],
        confidence=prediction["confidence"],
        pneumonia_probability=prediction["pneumonia_probability"],
        model_name=prediction["model_name"],
    )