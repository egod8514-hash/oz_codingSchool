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

@router.get("/users/test/{user_id}")
async def test(user_id:int = Path(
                default = ...
        ),
            current_user : User = Depends(
                get_current_user
        )) : 
    return {
        "a" : current_user.id,
        "b" : user_id
    }

@router.get("/users/test2/{user_id}")
async def test(user_id:int = Path(
                default = ...
        ),
            current_user : User = Depends(
                require_admin
        )) : 
    return {
        "a" : current_user.id,
        "b" : user_id
    }

@router.put("/users/{user_id}")
async def update_user(user_id:int = Path(
                default = ...
                ),
        update_data:User = Body(
                default = ...
        ),
        current_user : User = Depends(
            get_current_user
        )) : 

    # 유효성 검사
    if not (msg := await service.validation(user_id, update_data)) is None : 
        raise HTTPException(**msg)

    # 정보 수정
    return await service.update_user(user_id, update_data)

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