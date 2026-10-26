from pydantic import BaseModel

from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.core.enum.enum_role import RoleEnum


class AdminUserResponse(BaseModel):
    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: str
    role: RoleEnum
    is_active: bool


class AdminUserListResponse(BaseModel):
    users: list[AdminUserResponse]


class AdminRoleUpdateRequest(BaseModel):
    role: RoleEnum