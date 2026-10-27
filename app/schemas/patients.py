from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.enum.enum_gender import GenderEnum


GENDER_MAP = {
    "M": GenderEnum.MALE,
    "MALE": GenderEnum.MALE,
    "남성": GenderEnum.MALE,
    "남": GenderEnum.MALE,
    "F": GenderEnum.FEMALE,
    "FEMALE": GenderEnum.FEMALE,
    "여성": GenderEnum.FEMALE,
    "여": GenderEnum.FEMALE,
}


class PatientCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=30, description="환자 이름", example="홍길동")
    age: int = Field(..., ge=0, le=150, description="환자 나이 (0~150세)", example=34)
    gender: str = Field(..., description="성별 (M, F, male, female, 남성, 여성)", example="M")
    phone: Optional[str] = Field(None, description="연락처 (예: 010-1234-5678 또는 01012345678)", example="010-1234-5678")
    phone_number: Optional[str] = Field(None, description="연락처 필드 별칭", example="010-1234-5678")

    @model_validator(mode="before")
    @classmethod
    def resolve_phone(cls, values: dict):
        if isinstance(values, dict):
            # phone과 phone_number 중 하나라도 들어오면 매핑
            p = values.get("phone") or values.get("phone_number")
            if not p:
                raise ValueError("연락처(phone 또는 phone_number)는 필수 입력 항목입니다.")
            values["phone"] = str(p).strip()
            values["phone_number"] = str(p).strip()
        return values

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean in GENDER_MAP:
            return GENDER_MAP[clean].value
        if v.strip() in GENDER_MAP:
            return GENDER_MAP[v.strip()].value
        raise ValueError("성별은 'M', 'F', 'male', 'female', '남성', '여성' 중 하나여야 합니다.")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # 숫자만 추출하거나 하이픈 포함 형식 검증
        digits = re.sub(r"[^\d]", "", v)
        if len(digits) < 9 or len(digits) > 12:
            raise ValueError("올바른 전화번호 형식이 아닙니다.")
        return v


class PatientResponse(BaseModel):
    id: int = Field(..., description="환자 고유 ID")
    name: str = Field(..., description="환자 이름")
    age: int = Field(..., description="환자 나이")
    gender: str = Field(..., description="성별 (M 또는 F)")
    phone: str = Field(..., description="연락처")
    phone_number: str = Field(..., description="연락처 (프론트 호환용)")
    created_at: datetime = Field(..., description="등록 일시")
    updated_at: Optional[datetime] = Field(None, description="수정 일시")

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def set_phone_number(cls, data):
        if hasattr(data, "phone") and not hasattr(data, "phone_number"):
            # ORM 객체인 경우
            gender_val = data.gender.value if hasattr(data.gender, "value") else str(data.gender)
            return {
                "id": data.id,
                "name": data.name,
                "age": data.age,
                "gender": gender_val,
                "phone": data.phone,
                "phone_number": data.phone,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data
