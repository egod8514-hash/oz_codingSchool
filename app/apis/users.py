from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Body,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserModel
from app.schemas.users import (
    MyPageResponse,
    MyPageUpdateInfoRequest,
    MyPageUpdatePasswordRequest
)
from app.core import (
    constants,
    security,
    message
)
from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user

router = APIRouter(prefix = "/me")

@router.get("/",
            status_code = status.HTTP_200_OK,
            response_model = MyPageResponse)
async def get_my_info(
        current_user : UserModel = Depends(get_current_user),
    ) : 

    # 화면에 보여지는 필드로 자동 매핑
    return current_user

@router.patch("/",
              status_code = status.HTTP_200_OK)
async def update_info(
        current_user : UserModel = Depends(get_current_user),
        body : MyPageUpdateInfoRequest = Body(
            ...,
        ),
        db : AsyncSession = Depends(async_get_db),
    ) : 

    # dict로 변환
    update_data = body.model_dump(exclude_unset = True)

    # 기존 모델에 덮어쓰기
    for field, value in update_data.items() : 
        setattr(current_user, field, value)

    # DB에 반영
    await db.commit()
    await db.refresh(current_user)

    return {
        "message" : message.INFO_MESSAGE_USER_INFO_UPDATE
    }

# @router.patch("/password",
#               status_code = status.HTTP_200_OK)
# async def update_password(
#         current_user : UserModel = Depends(get_current_user),
#         body : MyPageUpdatePasswordRequest = Body(
#             ...,
#         ),
#         db : AsyncSession = Depends(async_get_db),
#     ) : 

#     # 현재 비밀번호가 DB에 저장된 비밀번호와 같은지 확인
#     if not security.verify_password(body.password, current_user.hashed_password) : 
#         raise HTTPException(
#             status_code = status.HTTP_400_BAD_REQUEST,
#             detail = message.ERROR_MESSAGE_CURRENT_PASSWORD,
#         )

#     # 새 비밀번호의 해시 코드를 생성
#     current_user.hashed_password = security.get_password_hash(body.new_password)

#     # DB에 반영
#     await db.commit()
#     await db.refresh(current_user)

#     return {
#         "message" : message.INFO_MESSAGE_PASSWORD_UPDATE
#     }

# @router.delete("/",
#                status_code = status.HTTP_204_NO_CONTENT)
# async def delete_account(
#         current_user : UserModel = Depends(get_current_user),
#         db : AsyncSession = Depends(async_get_db),
#     ) : 

#     # DB에 반영
#     db.delete(current_user)
#     db.commit()

#     return {
#         "message" : message.INFO_MESSAGE_ACCOUNT_DELETE
#     }