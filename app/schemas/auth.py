import re
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.core.enum.enum_role import RoleEnum


DEPARTMENT_MAP = {
    # DEV
    "개발": DepartmentEnum.DEV,
    "개발팀": DepartmentEnum.DEV,
    "DEV": DepartmentEnum.DEV,
    "DEVELOPER": DepartmentEnum.DEV,
    "DEVELOPMENT": DepartmentEnum.DEV,
    # MEDICAL
    "의료": DepartmentEnum.MEDICAL,
    "의료진": DepartmentEnum.MEDICAL,
    "의료팀": DepartmentEnum.MEDICAL,
    "MEDICAL": DepartmentEnum.MEDICAL,
    "MEDICAL TEAM": DepartmentEnum.MEDICAL,
    "DOCTOR": DepartmentEnum.MEDICAL,
    # RESEARCH
    "연구": DepartmentEnum.RESEARCH,
    "연구원": DepartmentEnum.RESEARCH,
    "연구진": DepartmentEnum.RESEARCH,
    "연구팀": DepartmentEnum.RESEARCH,
    "RESEARCH": DepartmentEnum.RESEARCH,
    "RESEARCHER": DepartmentEnum.RESEARCH,
}

GENDER_MAP = {
    "M": GenderEnum.MALE,
    "MALE": GenderEnum.MALE,
    "남": GenderEnum.MALE,
    "남성": GenderEnum.MALE,
    "F": GenderEnum.FEMALE,
    "FEMALE": GenderEnum.FEMALE,
    "여": GenderEnum.FEMALE,
    "여성": GenderEnum.FEMALE,
}


class SignupRequest(BaseModel):
    email: str = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, description="비밀번호 (8자 이상, 대소문자/특수문자 포함)")
    name: str = Field(..., min_length=2, max_length=20, description="이름")
    department: str = Field(..., description="부서 (의료, 개발, 연구)")
    gender: str = Field(..., description="성별 (M, F, 남성, 여성)")
    phone: Optional[str] = Field(None, description="연락처 (예: 010-1234-5678)")
    phone_number: Optional[str] = Field(None, description="연락처 (호환용)")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            phone_val = values.get("phone") or values.get("phone_number")
            if not phone_val:
                raise ValueError("전화번호는 필수 입력 항목입니다.")

            digits = re.sub(r"[^\d]", "", str(phone_val))
            if len(digits) == 11:
                formatted_phone = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
            elif len(digits) == 10:
                if digits.startswith("02"):
                    formatted_phone = f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
                else:
                    formatted_phone = f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            else:
                formatted_phone = str(phone_val).strip()

            values["phone"] = formatted_phone
            values["phone_number"] = formatted_phone
        return values

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

    @field_validator("department", mode="before")
    @classmethod
    def validate_department(cls, v: Any) -> str:
        if isinstance(v, DepartmentEnum):
            return v.value
        s = str(v).strip()
        upper = s.upper()
        if upper in DEPARTMENT_MAP:
            return DEPARTMENT_MAP[upper].value
        if s in DEPARTMENT_MAP:
            return DEPARTMENT_MAP[s].value
        raise ValueError("부서는 '의료', '개발', '연구' (또는 'MEDICAL', 'DEV', 'RESEARCH') 중 하나여야 합니다.")

    @field_validator("gender", mode="before")
    @classmethod
    def validate_gender(cls, v: Any) -> str:
        if isinstance(v, GenderEnum):
            return v.value
        s = str(v).strip()
        upper = s.upper()
        if upper in GENDER_MAP:
            return GENDER_MAP[upper].value
        if s in GENDER_MAP:
            return GENDER_MAP[s].value
        raise ValueError("성별은 'M' 또는 'F' (또는 남성/여성)이어야 합니다.")

    @field_validator("phone", "phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        pattern = r"^(01[0-9]|02|0[3-9][0-9])-([0-9]{3,4})-([0-9]{4})$"
        if not re.match(pattern, v.strip()):
            raise ValueError("올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)")
        return v.strip()


class SignupResponse(BaseModel):
    message: str = "회원가입이 완료되었습니다. 관리자 승인 후 서비스 이용이 가능합니다."
    user_id: int


class LoginRequest(BaseModel):
    email: str = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")


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
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
