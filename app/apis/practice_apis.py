from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel


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


# =========================================================
# 회원 추가 API (구민준 작업)
# =========================================================

class CreateUserRequest(BaseModel):
    name: str
    age: int
    email: str
    password: str


@router.post(
    "/users",
    summary="회원 추가 API",
    status_code=status.HTTP_201_CREATED,
)
def create_user_handler(
    body: CreateUserRequest = Body(...),
):
    # 이름 길이 제한 (최소 2글자, 최대 10글자)
    if len(body.name) < 2 or len(body.name) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 2글자, 최대 10글자",
        )

    # 나이 제한 (최소 14세 이상)
    if body.age < 14:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 14세 이상",
        )

    # 이메일 최대 30자 제한
    if len(body.email) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최대 30자",
        )

    # 이메일 형식 확인 (@, . 포함 여부)
    if "@" not in body.email or "." not in body.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 이메일 형식이 아님",
        )

    # 이메일 중복 검사
    for user in user_list:
        if user["email"] == body.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 이메일",
            )

    # 비밀번호 길이 제한 (8자 이상, 20자 이하)
    if len(body.password) < 8 or len(body.password) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 8자, 최대 20자",
        )

    # 대문자, 소문자, 특수문자 포함 여부 확인
    has_upper = False
    has_lower = False
    has_special = False

    special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"

    for char in body.password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char in special_characters:
            has_special = True

    if not has_upper:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="대문자 최소 1개 포함",
        )

    if not has_lower:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="소문자 최소 1개 포함",
        )

    if not has_special:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="특수문자가 최소 1개 포함",
        )

    # 새로운 회원 ID 생성
    new_id = 1

    if len(user_list) > 0:
        max_id = 0

        for user in user_list:
            if user["id"] > max_id:
                max_id = user["id"]

        new_id = max_id + 1

    # 새로운 회원 정보 생성
    new_user = {
        "id": new_id,
        "name": body.name,
        "age": body.age,
        "email": body.email,
        "password": body.password,
    }

    # 회원 목록에 추가
    user_list.append(new_user)

    # 성공 응답
    return {
        "message": "회원이 성공적으로 등록되었습니다.",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "age": new_user["age"],
            "email": new_user["email"],
        },
    }


# =========================================================
# 전체 회원 조회 API (안주형 작업)
# =========================================================

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


# =========================================================
# 특정 회원 조회 API (안주형 작업)
# =========================================================

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