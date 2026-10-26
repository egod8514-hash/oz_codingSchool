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