from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Body,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import UserModel
from app.models.patients import PatientModel
from app.schemas.patient import (
    PatientInfoUpdateRequest,
    PatientInfoPageResponse
)
from app.core import (
    constants,
    security,
    message
)
from app.core.db.databases import async_get_db
from app.core.dependencies import (
    get_current_user_active,
    get_patient_info_dep
)

router = APIRouter(prefix = "/patients")

@router.get("/{patient_id}",
            status_code = status.HTTP_200_OK,
            response_model = PatientInfoPageResponse
    )
async def get_patient_info(
        current_user : UserModel = Depends(get_current_user_active),
        patient_info : PatientModel = Depends(get_patient_info_dep),
    ) : 

    # 화면에 보여지는 필드로 자동 매핑
    return patient_info

@router.patch("/{patient_id}",
              status_code = status.HTTP_200_OK
    )
async def update_patient_info(
        current_user : UserModel = Depends(get_current_user_active),
        patient_info : PatientModel = Depends(get_patient_info_dep),
        body : PatientInfoUpdateRequest = Body(
            ...,
        ),
        db : AsyncSession = Depends(async_get_db),
    ) : 

    update_data = body.model_dump(exclude_unset = True)

    for field, value in update_data.items() :
        setattr(patient_info, field, value)

    await db.commit()
    await db.refresh(patient_info)

    return {
        "message" : message.INFO_MESSAGE_PATIENT_INFO_UPDATE
    }