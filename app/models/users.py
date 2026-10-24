from sqlalchemy import Integer, String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models.enums import Gender, Department, Role
from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
        )
    
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True
        )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255)
        )
    
    name: Mapped[str] = mapped_column(
        String(20)
        )
    
    phone_number: Mapped[str] = mapped_column(
        String(20), 
        unique=True
        )
    
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender), 
        nullable=False
        )
    
    department: Mapped[Department] = mapped_column(
        Enum(Department), 
        nullable=False
        )
    
    role: Mapped[Role] = mapped_column(
        Enum(Role), 
        nullable=False
        )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False
        )

