from app.schemas import User

from app.core import (
    constants,
    validation as valid,
    temporary_db,
)

# 유효성 검사
async def validation(user_id:int, new_data:User) : 

    # 유저 정보 수정 시의 필요한 유효성 검사
    messages = (
        await valid.validate_user_id(user_id),
        valid.validate_update_user(new_data),
        valid.validate_age(new_data[constants.COL_NAME_AGE]),
        valid.validate_email(new_data[constants.COL_NAME_EMAIL]),
        valid.validate_password(new_data[constants.COL_NAME_PASSWORD])
    )

    # 유효성 검사 중 
    return next((msg for msg in messages if msg is not None), None)

async def update_user(user_id:int, new_data:User) : 

    user_model = await temporary_db.get_user(user_id)

    user_model[constants.COL_NAME_AGE] = new_data.age
    user_model[constants.COL_NAME_EMAIL] = new_data.email
    user_model[constants.COL_NAME_PASSWORD] = new_data.password

    return {
        constants.COL_NAME_ID : user_model[constants.COL_NAME_ID],
        constants.COL_NAME_NAME : user_model[constants.COL_NAME_NAME],
        constants.COL_NAME_AGE : user_model[constants.COL_NAME_AGE],
        constants.COL_NAME_EMAIL : user_model[constants.COL_NAME_EMAIL]
    }