from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy import (
    BigInteger,
    DateTime,
    func,
)
import sqlalchemy as sa
from app.core.db.databases import Base

class BaseModel(Base) : 
    __abstract__ = True

    # 각 테이블의 PK
    id : Mapped[int] = mapped_column(
        BigInteger,
        primary_key = True,
        autoincrement = True
    )

    # 레코드 삭제 플래그
    is_deleted : Mapped[bool] = mapped_column(
        # Boolean, # 생략 가능
        default = False,
        server_default = sa.text("0"),
        nullable = False,
    )

    # 레코드 작성 일시
    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False,
    )

    # 레코드 수정 일시
    updated_at : Mapped[datetime | None] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = True,
    )

    # 레코드 삭제 일시
    delete_at : Mapped[datetime | None] = mapped_column(
        DateTime(timezone = True),
        default = None,
        nullable = True,
    )
