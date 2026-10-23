from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    List,
)

from app.models.base import BaseModel
from app.core import constants
from app.core.enum.enum_gender import GenderEnum

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    SmallInteger,
    String,
)
import sqlalchemy as sa

# 관계 선언용 import
if TYPE_CHECKING : 
    from app.models.medical_records import MedicalRecordModel

# 환자 모델
class PatientModel(BaseModel) : 
    __tablename__ = constants.TABLE_NAME_PATIENTS

    # 이름
    name : Mapped[str] = mapped_column(
        String(30),
        nullable = False,
    )

    # 나이
    age : Mapped[int] = mapped_column(
        SmallInteger,
        nullable = False,
    )

    # 성별
    gender : Mapped[GenderEnum] = mapped_column(
        sa.Enum(
            GenderEnum,
            values_callable = lambda x : [e.value for e in x]
        ),
        nullable = False,
    )

    # 전화번호
    phone : Mapped[str] = mapped_column(
        String(20),
        nullable = False,
    )

    # 관계 선언
    # 환자의 진료 기록 목록(1:N)
    medical_records : Mapped[List[MedicalRecordModel]] = relationship(
        back_populates = "patient",
        cascade = constants.RELATION_CASCADE,
    )