from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from fastapi import (
    HTTPException,
    status,
)

from app.core.enum.enum_department import DepartmentEnum
from app.core import (
    constants,
    message
)

class MyPageResponse(BaseModel) : 
    name : str
    email : str
    department : DepartmentEnum
    gender : str
    phone_number : str
    role : str

    model_config = ConfigDict(from_attributes = True)

class MyPageUpdateInfoRequest(BaseModel) : 
    department : DepartmentEnum = Field(
        default = ...,
    )
    phone_number : str = Field(
        default = ...,
        pattern = constants.PHONE_NUMBER_REGEX,
    )

class MyPageUpdatePasswordRequest(BaseModel) : 
    password : str = Field(
        ...,
    )
    new_password : str = Field(
        ...,
        pattern = constants.PASSWORD_REGEX,
        min_length = constants.PASSWORD_MIN_LEN,
        max_length = constants.PASSWORD_MAX_LEN,
    )
    new_password_confirm : str = Field(
        ...,
        pattern = constants.PASSWORD_REGEX,
        min_length = constants.PASSWORD_MIN_LEN,
        max_length = constants.PASSWORD_MAX_LEN,
    )

    @model_validator(mode = "after")
    def check_password_match(self) : 
        if self.new_password != self.new_password_confirm : 
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = message.ERROR_MESSAGE_NEW_PASSWORD,
            )

        if self.password == self.new_password : 
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = message.ERROR_MESSAGE_CURRENT_PASSWORD,
            )

        return self