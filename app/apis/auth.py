from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/signup",
    summary="[REQ-USER-001] 회원가입",
    description="신규 직원의 계정을 등록합니다. 가입 시 기본 권한은 PENDING(대기자)으로 설정됩니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=SignupResponse,
)
async def signup(
    data: SignupRequest,
    db: AsyncSession = Depends(async_get_db),
):
    return await auth_service.register_user(db, data)


@router.post(
    "/login",
    summary="[REQ-USER-002] 로그인",
    description="이메일과 비밀번호를 검증하여 DB 일치 여부를 확인하고 사용자 기본 정보를 반환합니다. (JSON 및 Form-Data 모두 지원)",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def login(
    request: Request,
    db: AsyncSession = Depends(async_get_db),
):
    return await auth_service.login_request_handler(request, db)
