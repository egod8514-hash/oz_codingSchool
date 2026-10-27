from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    age: int
    email: str
    password: str


# 서비스 사용자의 회원 비밀번호 변경 REQ-USER-008, 회원 탈퇴 REQ-USER-009 (신혜원 담당)

import re
from pydantic import BaseModel, Field, field_validator

class PasswordChangeRequest(BaseModel):
    """[REQ-USER-008] 비밀번호 변경 요청 스키마"""
    current_password: str = Field(..., description="기존 비밀번호")
    new_password: str = Field(
        ...,
        min_length=8,
        description="새 비밀번호 (8자 이상, 영문자와 숫자 최소 1자 포함)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("새 비밀번호는 영문자와 숫자를 최소 1자 이상 포함해야 합니다.")
        return v
