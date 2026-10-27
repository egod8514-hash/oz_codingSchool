계정 보안 및 회원 탈퇴 기능 구현 & 서순 가이드

본 문서는 사내 흉부 X-Ray AI 진단 서비스 프로젝트 (계정 보안 및  회원 탈퇴) 담당 기능인 **비밀번호 변경(REQ-USER-008)**과 **회원 탈퇴(REQ-USER-009)**의 구현 코드, 

동작 서순 및 Swagger UI 테스트 절차를 정리한 문서입니다.

---

## 1. 개요 및 담당 역할

* **담당자**: 팀원 3
* **주력 도메인**: 계정 보안 및 회원 탈퇴
* **구현 API 목록**:
  1. `PATCH /api/v1/users/me/password`: 기존 비밀번호 검증 후 새 비밀번호 단방향 암호화 적용 (`REQ-USER-008`)
  2. `DELETE /api/v1/users/me`: 데이터베이스 물리 삭제(Hard Delete) 및 Refresh Token 쿠키 만료 처리 (`REQ-USER-009`)
* **패키지 분리 규칙**:
  - `app/schemas/user.py`: 입력값 검증 DTO 정의
  - `app/routers/users.py`: API 엔드포인트 및 비즈니스 로직 구현

---

## 2. Pydantic 스키마 (app/schemas/user.py)

클라이언트 요청 본문의 유효성을 사전 검증하며, 비밀번호 복잡도(8자 이상, 영문자와 숫자 최소 1자 포함) 규칙을 적용합니다.

```python
import re
from pydantic import BaseModel, Field, field_validator

class PasswordChangeRequest(BaseModel):
    """[REQ-USER-008] 비밀번호 변경 요청 DTO"""
    current_password: str = Field(..., description="기존 비밀번호")
    new_password: str = Field(
        ...,
        min_length=8,
        description="새 비밀번호 (8자 이상, 영문자와 숫자 최소 1자 포함)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("새 비밀번호는 영문자와 숫자를 최소 1자 이상 포함해야 합니다.")
        return v
              
3. 라우터 구현 (app/routers/users.py)
              
공통 인증 의존성인 get_current_user를 주입받아 로그인된 본인 계정에 대한 검증 및 데이터베이스 트랜잭션을 실행합니다.

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.core.dependencies import get_current_user  # 임시 인증(X-User-Id) 및 향후 JWT 연동
from app.models.user import User
from app.schemas.user import PasswordChangeRequest

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# [REQ-USER-008] 비밀번호 변경
  
@router.patch("/me/password", status_code=status.HTTP_200_OK)
def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. 현재 비밀번호 일치 검증
    2. 기존 비밀번호와 동일한 새 비밀번호 사용 차단
    3. 새 비밀번호 단방향 해싱 후 DB 영구 반영
    """
    # 1. 기존 비밀번호 검증
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다."
        )

    # 2. 동일 비밀번호 재사용 방지
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호는 기존 비밀번호와 동일할 수 없습니다."
        )

    # 3. 해싱 및 DB 반영
    current_user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


# [REQ-USER-009] 회원 탈퇴
@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    1. DB에서 사용자 데이터 물리적 완전 삭제 (Hard Delete)
    2. Refresh Token 쿠키 만료(Max-Age=0) 처리
    """
    # 1. DB 물리 삭제
    db.delete(current_user)
    db.commit()

    # 2. 쿠키 만료 처리
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth"
    )

    return {"message": "회원 탈퇴 및 정보 삭제가 정상 완료되었습니다."}

4. 비즈니스 로직 동작 서순
  
(1) 비밀번호 변경 서순 (PATCH /api/v1/users/me/password)
  
인증 주입 및 사용자 식별: Depends(get_current_user)를 통해 요청 헤더(X-User-Id 또는 JWT)에서 사용자 ID를 추출하고 DB에서 활성 유저 객체(current_user)를 조회합니다.
기존 비밀번호 일치 검증: 단방향 암호화 특성에 따라 유저가 입력한 current_password를 솔트(Salt) 기반 검증 함수(verify_password)로 대조합니다. 불일치 시 400 Bad Request 에러를 반환합니다.
새 비밀번호 중복 방지: 새 비밀번호가 기존 비밀번호와 같을 경우 변경을 차단합니다.
단방향 해싱 및 커밋: 안전한 해시 함수(hash_password)로 새 비밀번호를 암호화하여 DB에 반영(commit)하고 200 OK 응답을 전달합니다.
  
(2) 회원 탈퇴 서순 (DELETE /api/v1/users/me)
  
로그인 상태 확인: get_current_user 의존성을 통과한 정상 세션의 사용자 객체를 가져옵니다.
물리 삭제(Hard Delete): 명세서의 요구사항에 따라 db.delete(current_user)를 호출하여 DB 테이블에서 해당 회원 레코드를 즉시 완전 삭제합니다.
인증 쿠키 파기: response.delete_cookie(key="refresh_token", path="/api/v1/auth")를 적용해 브라우저에 남아 있는 인증 쿠키를 즉시 만료시키고 200 OK 응답을 반환합니다.
  
5. Swagger UI (/docs) 테스트 절차
  
로컬 서버 기동:
uvicorn app.main:app --reload
Swagger 문서 접속: 웹 브라우저에서 [suspicious link removed] 접속
  
비밀번호 변경 테스트 (PATCH /api/v1/users/me/password):
x-user-id 헤더에 일반 스태프 계정 ID(예: 2) 입력
틀린 current_password 입력 후 [Execute] 실행 시 400 Bad Request 반환 확인
정상 current_password와 조건을 충족하는 new_password 입력 후 [Execute] 실행 시 200 OK 반환 확인
  
회원 탈퇴 테스트 (DELETE /api/v1/users/me):
x-user-id 헤더에 탈퇴 대상 계정 ID(예: 2) 입력 후 [Execute] 실행 시 200 OK 반환 확인
Response Header의 Set-Cookie 속성 중 refresh_token=; Max-Age=0 만료 확인
탈퇴 완료 후 동일한 ID로 재요청 시 404 Not Found 또는 인증 실패 반환 확인
