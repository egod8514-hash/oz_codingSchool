from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Body,
)

from app.schemas.user import User
from app.services import update_user_service as service

router = APIRouter()

@router.put("/users/{user_id}")
async def update_user(user_id:int = Path(
                default = ...
                ),
        update_data:User = Body(
                default = ...
        )) : 

    # 유효성 검사
    if not (msg := await service.validation(user_id, update_data)) is None : 
        raise HTTPException(**msg)

    # 정보 수정
    return await service.update_user(user_id, update_data)