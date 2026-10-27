
# 서비스 사용자의 회원 비밀번호 변경 REQ-USER-008, 회원 탈퇴 REQ-USER-009 라우터 (신혜원 담당)

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.core.dependencies import get_current_user
from app.models.users import User
from app.schemas.user import PasswordChangeRequest

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.patch("/me/password", status_code=status.HTTP_200_OK)
def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="현재 비밀번호가 일치하지 않습니다.")

    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="새 비밀번호는 기존 비밀번호와 동일할 수 없습니다.")

    current_user.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    return {"message": "회원 탈퇴 및 정보 삭제가 정상 완료되었습니다."}
