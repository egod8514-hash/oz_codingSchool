from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from app.models.base import BaseModel
from app.models.users import UserModel
from app.models.medical_records import MedicalRecordModel
from app.core import constants

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    func,
    ForeignKey,
)

# 엑스레이 사진 모델
class XrayImagesModel(BaseModel) : 
    __tablename__ = constants.TABLE_NAME_XRAY

    # 의료 레코드 ID
    record_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            MedicalRecordModel.id,
            ondelete = "CASCADE",        
        ),
        nullable = False,
    )

    # 업로드 계정 ID
    uploader_id : Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            UserModel.id,
            ondelete = "CASCADE",
        ),
        nullable = False,
    )

    # 사진 URL
    image_url : Mapped[str] = mapped_column(
        String(255),
        nullable = False,
    )

    # 촬영 일시
    shooting_datetime : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False,
    )

    # 관계 선언
    # 업로드 직원 역참조(N:1)
    uploader : Mapped[UserModel] = relationship(
        back_populates = "uploaded_xrays",
    )

    # 진료 기록 역참조(N:1)
    medical_record : Mapped[MedicalRecordModel] = relationship(
        back_populates = "xray_images",
    )