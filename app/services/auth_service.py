from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import UserModel
from app.core.enum.enum_role import RoleEnum
from app.core.enum.enum_department import DepartmentEnum
from app.core.enum.enum_gender import GenderEnum
from app.core.security import hash_password, verify_password
from app.schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse, UserInfo


async def register_user(db: AsyncSession, data: SignupRequest) -> SignupResponse:
    """
    REQ-USER-001: 신규 사용자 회원가입
    1. 이메일 중복 체크 (409 Conflict)
    2. 전화번호 중복 체크 (409 Conflict)
    3. 비밀번호 bcrypt 해싱
    4. UserModel 생성 (기본 권한: PENDING, 활성 상태: True)
    5. DB 커밋 및 신규 유저 ID 반환
    """
    # 1. 이메일 중복 체크
    stmt_email = select(UserModel).where(UserModel.email == data.email)
    existing_user_email = (await db.execute(stmt_email)).scalar_one_or_none()
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다."
        )

    # 2. 전화번호 중복 체크
    stmt_phone = select(UserModel).where(UserModel.phone_number == data.phone)
    existing_user_phone = (await db.execute(stmt_phone)).scalar_one_or_none()
    if existing_user_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 전화번호입니다."
        )

    # 3. 비밀번호 해싱
    hashed_pwd = hash_password(data.password)

    # 4. 엔티티 생성
    new_user = UserModel(
        email=data.email,
        hashed_password=hashed_pwd,
        name=data.name,
        phone_number=data.phone,
        department=DepartmentEnum(data.department),
        gender=GenderEnum(data.gender),
        role=RoleEnum.PENDING,
        is_active=True,
        is_deleted=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return SignupResponse(
        message="회원가입이 완료되었습니다. 관리자 승인 후 서비스 이용이 가능합니다.",
        user_id=new_user.id
    )


async def authenticate_user(db: AsyncSession, data: LoginRequest) -> LoginResponse:
    """
    REQ-USER-002: 로그인 기본 로직
    1. 이메일로 사용자 조회
    2. 사용자 미존재 또는 탈퇴 계정(is_deleted) 검증
    3. bcrypt 비밀번호 일치 검증
    4. 일치 시 로그인 성공 및 사용자 정보 반환
    """
    stmt = select(UserModel).where(UserModel.email == data.email)
    user = (await db.execute(stmt)).scalar_one_or_none()

    # 계정이 없거나 탈퇴한 회원인 경우 (보안을 위해 동일한 401 메시지 반환)
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다."
        )

    # 비밀번호 검증
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다."
        )

    return LoginResponse(
        message="로그인에 성공했습니다.",
        user=UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            department=user.department.value if hasattr(user.department, "value") else str(user.department),
            gender=user.gender.value if hasattr(user.gender, "value") else str(user.gender),
            phone_number=user.phone_number,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            is_active=user.is_active,
        )
    )
