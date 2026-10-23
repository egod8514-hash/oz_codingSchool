from __future__ import annotations
from decimal import Decimal

from app.models.base import BaseModel
from app.core import constants
from app.models.medical_records import MedicalRecordModel

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    BigInteger,
    # Boolean,
    String,
    DECIMAL,
    ForeignKey,
)

# AI 분석 결과 모델
class AnalysisResultModel(BaseModel) : 
    __tablename__ = constants.TABLE_NAME_AI_RESULTS

    # 진료 기록 ID
    record_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            MedicalRecordModel.id,
            ondelete = "CASCADE",        
        ),
        nullable = False,
    )

    # 폐렴 진단 여부
    is_pneumonia : Mapped[bool] = mapped_column(
        # Boolean, # 생략 가능
        nullable = False
    )

    # 예측 신뢰도
    confidence : Mapped[Decimal] = mapped_column(
        DECIMAL(
            precision = 5,
            scale = 2
        ),
        nullable = False
    )

    # 병변 표시 사진 URL
    heatmap_url : Mapped[str] = mapped_column(
        String(255),
        nullable = False,
    )

    # AI 모델명
    ai_model : Mapped[str] = mapped_column(
        String(50),
        nullable = False,
    )

    # 관계 선언
    # 진료 기록 역참조(N:1)
    medical_record : Mapped[MedicalRecordModel] = relationship(
        back_populates = "analysis_results",
    )