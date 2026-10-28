# 4일차 작업일지

## 오늘 진행한 작업

### 관리자 회원 관리 API 구현

관리자 기능 중 다음 두 가지 API를 담당하여 구현했다.

- `GET /api/v1/admin/users`
  - 전체 회원 목록 조회
  - 이메일/이름 검색 기능
  - 부서별 필터링 기능

- `PATCH /api/v1/admin/users/{user_id}/role`
  - 특정 회원의 권한 변경
  - `PENDING`, `STAFF`, `ADMIN` 권한 처리
  - 존재하지 않는 회원 요청 시 `404 Not Found` 처리

### 코드 구조

기능별 역할을 분리하여 다음 구조로 구현했다.

- `app/apis/admin.py`
  - API Endpoint 처리
- `app/services/admin_service.py`
  - 회원 조회 및 권한 변경 로직
- `app/schemas/admin.py`
  - Request / Response Schema 정의

### 테스트

Swagger를 이용하여 다음 기능을 테스트했다.

- 전체 회원 조회
- 이름/이메일 검색
- 부서 필터링
- 회원 권한 변경
- 존재하지 않는 회원 조회 시 404 처리

---

## Git 작업

기능 브랜치를 생성하여 작업했다.

`feature/admin-user-api`

구현 완료 후 Commit → Push → Pull Request를 생성하여 `main` 브랜치에 병합했다.

---

## 문제 및 해결

최신 `main`을 pull한 후 서버 실행 과정에서 `security.py`가 `passlib`을 사용하고 있었지만 프로젝트 의존성에는 `bcrypt`만 등록되어 있어 서버가 실행되지 않는 문제가 발생했다.

`security.py`의 비밀번호 해싱 방식을 프로젝트에서 사용 중인 `bcrypt` 방식으로 수정한 후 Uvicorn 및 Swagger가 정상적으로 실행되는 것을 확인했다.

---

## 오늘 배운 점

- API / Service / Schema를 분리하여 기능을 구현하는 방법
- SQLAlchemy를 이용한 회원 검색 및 필터링
- Enum을 이용한 회원 권한 변경
- Swagger를 이용한 API 테스트
- GitHub Flow 방식의 기능 브랜치 → PR → Merge 과정
- Git Merge가 성공해도 실제 서버 실행 과정에서 의존성이나 코드 충돌 문제가 발생할 수 있으므로 Merge 후 로컬 실행 테스트가 필요하다는 점