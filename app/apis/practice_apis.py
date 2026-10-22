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

@router.get("/users")
async def get_users():
    return [
        {
            "id": user["id"],
            "name": user["name"],
            "age": user["age"],
            "email": user["email"]
        }
        for user in user_list
    ]

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "name": user["name"],
                "age": user["age"],
                "email": user["email"]
            }

    raise HTTPException(
        status_code=404,
        detail="해당 회원을 찾을 수 없습니다."
    )