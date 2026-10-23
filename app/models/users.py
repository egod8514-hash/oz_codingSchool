from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    List,
)

from app.models.base import BaseModel
from app.core import constants
from app.core.enum.enum_gender import GenderEnum
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_role import RoleEnum

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    # Boolean,
    String,
)
import sqlalchemy as sa

# 관계 선언용 import
if TYPE_CHECKING : 
    from app.models.xray_images import XrayImagesModel

# 직원 모델
class UserModel(BaseModel) : 
    __tablename__ = constants.TABLE_NAME_USERS

    # 이메일
    email : Mapped[str] = mapped_column(
        String(255),
        unique = True,
        nullable = False,
    )

    # 비밀번호
    hashed_password : Mapped[str] = mapped_column(
        String(255),
        nullable = False,
    )

    # 이름
    name : Mapped[str] = mapped_column(
        String(20),
        nullable = False,
    )

    # 전화번호
    phone_number : Mapped[str] = mapped_column(
        String(20),
        unique = True,
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

    # 부서
    department : Mapped[DepartmentEnum] = mapped_column(
        sa.Enum(
            DepartmentEnum,
            values_callable = lambda x : [e.value for e in x]
        ),
        nullable = False,
    )

    # 권한
    role : Mapped[RoleEnum] = mapped_column(
        sa.Enum(
            RoleEnum,
            values_callable = lambda x : [e.value for e in x]
        ),
        nullable = False,
    )

    # 계정 활성화 여부
    is_active : Mapped[bool] = mapped_column(
        # Boolean, # 생략 가능
        default = True,
        server_default = sa.text("1"),
        nullable = False,
    )

    # 관계 선언
    # 직원이 업로드한 엑스레이 목록(1:N)
    uploaded_xrays : Mapped[List[XrayImagesModel]] = relationship(
        back_populates = "uploader",
        cascade = constants.RELATION_CASCADE,
    )