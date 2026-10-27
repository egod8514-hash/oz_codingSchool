import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.core.enum.enum_role import RoleEnum


DEPARTMENT_MAP = {
    "개발": DepartmentEnum.DEV,
    "DEV": DepartmentEnum.DEV,
    "의료": DepartmentEnum.MEDICAL,
    "MEDICAL": DepartmentEnum.MEDICAL,
    "연구": DepartmentEnum.RESEARCH,
    "RESEARCH": DepartmentEnum.RESEARCH,
}


class SignupRequest(BaseModel):
    email: str = Field(..., description="이메일 주소", example="doctor@hospital.com")
    password: str = Field(..., min_length=8, description="비밀번호 (8자 이상, 대소문자/특수문자 포함)", example="SecurePassword123!")
    name: str = Field(..., min_length=2, max_length=20, description="이름", example="홍길동")
    department: str = Field(..., description="부서 (의료, 개발, 연구)", example="의료")
    gender: str = Field(..., description="성별 (M, F)", example="M")
    phone: str = Field(..., description="연락처 (예: 010-1234-5678)", example="010-1234-5678")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("비밀번호에 대문자가 최소 1개 이상 포함되어야 합니다.")
        if not re.search(r"[a-z]", v):
            raise ValueError("비밀번호에 소문자가 최소 1개 이상 포함되어야 합니다.")
        if not re.search(r"[!@#$%^&*()-_=+\[\]{}|;:'\",.<>?/`~]", v):
            raise ValueError("비밀번호에 특수문자가 최소 1개 이상 포함되어야 합니다.")
        return v

    @field_validator("department")
    @classmethod
    def validate_department(cls, v: str) -> str:
        clean = v.strip().upper()
        if v.strip() in DEPARTMENT_MAP:
            return DEPARTMENT_MAP[v.strip()].value
        if clean in DEPARTMENT_MAP:
            return DEPARTMENT_MAP[clean].value
        raise ValueError("부서는 '의료', '개발', '연구' (또는 'MEDICAL', 'DEV', 'RESEARCH') 중 하나여야 합니다.")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in ["M", "F"]:
            raise ValueError("성별은 'M' 또는 'F'여야 합니다.")
        return clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        pattern = r"^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$"
        if not re.match(pattern, v.strip()):
            raise ValueError("올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)")
        return v.strip()


class SignupResponse(BaseModel):
    message: str = "회원가입이 완료되었습니다. 관리자 승인 후 서비스 이용이 가능합니다."
    user_id: int


class LoginRequest(BaseModel):
    email: str = Field(..., description="이메일", example="doctor@hospital.com")
    password: str = Field(..., description="비밀번호", example="SecurePassword123!")


class UserInfo(BaseModel):
    id: int
    email: str
    name: str
    department: str
    gender: str
    phone_number: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str = "로그인에 성공했습니다."
    user: UserInfo
