from typing import Optional, Any
from pydantic import BaseModel, model_validator
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.core.enum.enum_role import RoleEnum


class AdminUserResponse(BaseModel):
    id: int
    email: str
    name: str
    department: str
    gender: str
    phone_number: str
    role: str
    is_active: bool


class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]


class AdminRoleUpdateRequest(BaseModel):
    user_id: Optional[int] = None
    role: Optional[RoleEnum] = None
    new_role: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_role(cls, values: Any) -> Any:
        if isinstance(values, dict):
            raw_role = values.get("role") or values.get("new_role")
            if raw_role is not None:
                if isinstance(raw_role, RoleEnum):
                    values["role"] = raw_role
                else:
                    role_str = str(raw_role).strip().upper()
                    if role_str in RoleEnum.__members__:
                        values["role"] = RoleEnum[role_str]
                    elif role_str in {"STAFF", "일반회원"}:
                        values["role"] = RoleEnum.STAFF
                    elif role_str in {"ADMIN", "관리자"}:
                        values["role"] = RoleEnum.ADMIN
                    elif role_str in {"PENDING", "승인대기"}:
                        values["role"] = RoleEnum.PENDING
        return values
