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

# 회원 삭제 API 부분 (신혜원 작업)

@router.delete(
    "/users/{user_id}",
    summary="회원 삭제 API",
)
async def delete_user_handler(user_id: int):
    global user_list
    
   
    for idx, user in enumerate(user_list):
        if user["id"] == user_id:
            user_list.pop(idx)
            return {"message": f"ID {user_id}번 회원의 정보를 삭제했습니다."}

   
    raise HTTPException(
        status_code=404,
        detail="해당 회원을 찾을 수 없습니다."
    )


     
