from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
    AliasChoices,
)

from fastapi import (
    HTTPException,
    status,
)

from app.core.enum.enum_gender import GenderEnum
from app.core import (
    constants,
    message
)

class PatientInfoPageResponse(BaseModel) : 
    name : str
    gender : GenderEnum
    phone : str
    age : int

    model_config = ConfigDict(from_attributes = True)

class PatientInfoUpdateRequest(BaseModel) : 
    name : str = Field(
        default = ...,
    )
    phone : str = Field(
        default = ...,
        pattern = constants.PHONE_NUMBER_REGEX
    )