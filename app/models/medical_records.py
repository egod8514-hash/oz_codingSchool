from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    List,
)

from app.models.base import BaseModel
from app.models.patients import PatientModel
from app.core import constants

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    BigInteger,
    String,
    Text,
    ForeignKey,
)

# 관계 선언용 import
if TYPE_CHECKING : 
    from app.models.xray_images import XrayImagesModel
    from app.models.ai_analysis_results import AnalysisResultModel

# 진료 기록 모델
class MedicalRecordModel(BaseModel) : 
    __tablename__ = constants.TABLE_NAME_MEDICAL

    # 환자 ID
    patient_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            PatientModel.id,
            ondelete = "CASCADE",
        ),
        nullable = False,
    )

    # 차트 번호
    chart_number : Mapped[str] = mapped_column(
        String(50),
        unique = True,
        nullable = False,
    )

    # 환자 증상 기록
    symptoms : Mapped[str] = mapped_column(
        Text,
        nullable = False,
    )

    # 관계 선언
    # 환자 역참조(N:1)
    patient : Mapped[PatientModel] = relationship(
        back_populates = "medical_records",
    )

    # 엑스레이 사진 목록(1:N)
    xray_images : Mapped[List[XrayImagesModel]] = relationship(
        back_populates = "medical_record",
        cascade = constants.RELATION_CASCADE,
    )

    # AI 분석 결과 목록(1:N)
    analysis_results : Mapped[List[AnalysisResultModel]] = relationship(
        back_populates = "medical_record",
        cascade = constants.RELATION_CASCADE,
    )