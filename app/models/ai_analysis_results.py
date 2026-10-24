from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin


class AIAnalysisResult(TimestampMixin, Base):
    __tablename__ = "ai_analysis_results"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medical_records.id"),
        nullable=False
    )

    is_pneumonia: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )

    heatmap_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    ai_model: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )