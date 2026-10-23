from fastapi import status

from app.core import (
    constants,
    message,
    temporary_db
)
from app.schemas.user import User

# 유저 ID 유효성 검사
async def validate_user_id(user_id:int) : 
    if await temporary_db.get_user(user_id) is None : 
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_404_NOT_FOUND,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_ID_RANGE
        }

# 유저 정보 수정 전용 검사
def validate_update_user(new_data:User) : 
    if (new_data.age is None 
            or new_data.email is None
            or new_data.password is None) :
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_400_BAD_REQUEST,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_E0010
        }

# 나이 유효성 검사
def validate_age(age:int) :
    # 나이 구간 검사
    if not constants.MIN_AGE <= age : 
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_400_BAD_REQUEST,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_AGE_RANGE
        }

# 이메일 유효성 검사
def validate_email(email:str) : 
    # 이메일 정규표현 검사
    if not constants.EMAIL_REGEX.match(email) : 
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_400_BAD_REQUEST,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_EMAIL_REGEX
        }

    # 이메일 자리수 검사
    if not len(email) <= constants.EMAIL_MAX_LEN : 
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_400_BAD_REQUEST,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_EMAIL_LEN
        }

# 패스워드 유효성 검사
def validate_password(password:str) : 
    # 패스워드 정규표현 검사
    if not constants.PASSWORD_REGEX.match(password) : 
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_400_BAD_REQUEST,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_PASSWORD_REGEX
        }

    # 패스워드 자리수 검사
    if not (constants.PASSWORD_MIN_LEN <= len(password) <= constants.PASSWORD_MAX_LEN) : 
        return {
            constants.PARAM_NAME_STATUS_CODE : status.HTTP_400_BAD_REQUEST,
            constants.PARAM_NAME_DETAIL : message.MESSAGE_PASSWORD_LEN
        }