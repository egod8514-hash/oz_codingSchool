from fastapi import (
    APIRouter,
    HTTPException,
    Path,
    Body,
    status,
)

from app.schemas.user import User
from app.core import constants
from app.apis.practice_apis import user_list

router = APIRouter()

@router.put("/users/{user_id}")
async def update_user(user_id:int = Path(
                default = ...
                ),
        update_data:User = Body(
                default = ...
        )) : 

    # TODO : DB에서 await로 기다리게 하기

    update_user_model = None

    # 유저ID가 있는지 확인
    for user in user_list : 
        if user_id == user[constants.COL_NAME_ID] : 
            update_user_model = user
            break

    # 유저 유효성 검사
    if update_user_model is None : 
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "유효한 유저 ID가 아닙니다."
        )

    # 데이터 확인
    if (update_data.age is None 
            or update_data.email is None
            or update_data.password is None) :
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "수정할 데이터(age, email, password)를 전부 입력해주세요."
        )

    # 나이 검사
    if not update_data.age >= constants.MIN_AGE : 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"나이는 {constants.LOWER_AGE}세 이상으로 입력해주세요."
        )

    # 패스워드 유효성 검사
    if not constants.PASSWORD_REGEX.match(update_data.password) : 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "비밀번호는 영문대문자, 영문소문자, 특수문자가 각각 1개이상 포함시켜 입력해주세요."
        )

    # 패스워드 길이 검사
    if not (constants.PASSWORD_MIN_LEN <= len(update_data.password) <= constants.PASSWORD_MAX_LEN) : 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"비밀번호는 {constants.PASSWORD_MIN_LEN}자리 이상, {constants.PASSWORD_MAX_LEN}자리 이하로 입력해주세요."
        )

    # 이메일 유효성 검사
    if not constants.EMAIL_REGEX.match(update_data.email) : 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "이메일 주소는 이메일 형식에 맞게 입력해주세요."
        )

    # 이메일 길이 검사
    if not (len(update_data.email) <= constants.EMAIL_MAX_LEN) : 
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"이메일 주소는 {constants.EMAIL_MAX_LEN}자리 이하로 입력해주세요."
        )

    # 정보 수정
    update_user_model[constants.COL_NAME_AGE] = update_data.age
    update_user_model[constants.COL_NAME_EMAIL] = update_data.email
    update_user_model[constants.COL_NAME_PASSWORD] = update_data.password

    return {
        constants.COL_NAME_ID : update_user_model[constants.COL_NAME_ID],
        constants.COL_NAME_NAME : update_user_model[constants.COL_NAME_NAME],
        constants.COL_NAME_AGE : update_user_model[constants.COL_NAME_AGE],
        constants.COL_NAME_EMAIL : update_user_model[constants.COL_NAME_EMAIL]
    }