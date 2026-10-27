from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Body,
    Depends,
)

from app.schemas.user import User
from app.services import update_user_service as service
from app.core.dependencies import get_current_user, require_admin
from app.core.db.databases import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import UserModel
from sqlalchemy import select

router = APIRouter()

@router.patch("/me")
async def update_my_profile(
    current_user: User = Depends(get_current_user),  # <-- 임시 인증 주입 (Swagger 헤더 자동 생성)
    db: AsyncSession = Depends(async_get_db)
):
    # current_user.id, current_user.email 등 DB에서 조회된 ORM 객체 바로 사용 가능
    stmt = select(UserModel).where(UserModel.id == current_user.id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return {
        "status": "success",
        "user_id": current_user.id,
        "department" : user.department,
        "message": f"{current_user.name}님의 정보 수정 완료"
    }