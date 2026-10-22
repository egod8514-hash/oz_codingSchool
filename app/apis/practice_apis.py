from fastapi import APIRouter
from fastapi import HTTPException

router = APIRouter(prefix="/practice_api", tags=["Practice API"])


user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!"
    },
    {
        "id": 2,
        "name": "홍둘둘",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!"
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "IwsPAssword12@"
    }
]

회원 정보 삭제 API 부분 (신혜원 작업)

@router.delete(
    "/users/{user_id}",
    summary="회원 삭제 API",
)
async def delete_user_handler(user_id: int):
    global user_list
    
    # user_list 안에서 삭제할 대상이 되는 회원을 검색
    
    for idx, user in enumerate(user_list):
        if user["id"] == user_id:
            
    # 해당 회원을 찾은 경우 목록(user_list)에서 영구 제거.
            
            user_list.pop(idx)
            return {"message": f"성공적으로 ID {user_id}번 회원의 모든 정보를 삭제했습니다."}

    # 전체 검색에도 삭제하려는 회원 id를 찾지 못한 경우의 처리
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="해당 회원을 찾을 수 없습니다.",
    )

        detail="해당 회원을 찾을 수 없습니다."
    )
