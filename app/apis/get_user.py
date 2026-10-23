from fastapi import APIRouter, HTTPException, status

from app.services import get_user_service as service


def create_router(user_list):
    router = APIRouter()

    # 전체 회원 조회 API
    @router.get("/users")
    async def get_users():
        return service.get_users(user_list)

    # 특정 회원 조회 API
    @router.get("/users/{user_id}")
    async def get_user(user_id: int):
        user = service.get_user_by_id(user_list, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 회원을 찾을 수 없습니다.",
            )

        return user

    return router