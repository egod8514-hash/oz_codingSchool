from datetime import datetime

from sqlalchemy import BigInteger, Integer, ForeignKey, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base


class XrayImage(Base):
    __tablename__ = "xray_images"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medical_records.id"),
        nullable=False
    )

    uploader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
        )
    
    image_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False
    )

    shooting_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("current_timestamp(0)")
    )