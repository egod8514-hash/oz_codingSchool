from sqlalchemy import BigInteger, String, Enum, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.models.enums import Gender
from app.core.db.models import TimestampMixin

class Patient(TimestampMixin, Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(
        BigInteger, 
        primary_key=True
        )
    
    name: Mapped[str] = mapped_column(
        String(30), 
        nullable=False
        )
    
    age: Mapped[int] = mapped_column(
        SmallInteger, 
        nullable=False
        )
    
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender), 
        nullable=False
        )
    
    phone: Mapped[str] = mapped_column(
        String(11), 
        nullable=False
        )