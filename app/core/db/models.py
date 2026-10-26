import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, text, Integer, String
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from uuid6 import uuid7
from enum import Enum


class UUIDMixin:
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        CHAR(36), primary_key=True, default=uuid7
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), server_default=text("current_timestamp(0)")
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=datetime.now(UTC), server_default=text("current_timestamp(0)")
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


# 구민준 작성

# Enum 상속
class Gender(str, Enum):
    M = "M"     # male
    F = "F"     # female


class Role(str, Enum):
    PENDING = "PENDING"     # 권한 부여 대기
    STAFF = "STAFF"     # 폐렴 추적 관련 데이터 CRUD 허용
    ADMIN = "ADMIN"     # 전체데이터 CRUD 허용


class Department(str, Enum):
    MEDICAL = "MEDICAL"     # 의료진
    DEV = "DEV"     # 개발팀
    RESEARCH = "RESEARCH"       # 연구진

# 테이블 정의 부모 클래스
class Base(DeclarativeBase):
    pass

# Item 테이블
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String(255),
        unique=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="평문 저장 x -> 해쉬화 된 비밀번호 저장",
    )
    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="유저 휴대폰 번호"
    )

    # Enum 컬럼들
    gender: Mapped[Gender] = mapped_column(
        SQLEnum(Gender), nullable=False, comment="성별 선택"
    )
    department: Mapped[Department] = mapped_column(
        SQLEnum(Department), nullable=False, comment="부서 선택"
    )
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role), nullable=False, comment="부여된 역할 권한"
    )

    # 상태 및 타임스탬프
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="계정 활성화 여부"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="유저 생성일시",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True, comment="유저 정보 수정 일시"
    )