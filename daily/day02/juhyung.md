# Day 02 작업일지 - 안주형

## 1. Git Branch 전략 학습

- Git Flow와 GitHub Flow의 차이 학습
- 팀원들과 Branch 전략 논의
- 우리 팀의 Branch 전략으로 `GitHub Flow` 선택
- 기능별 Branch에서 작업 후 PR과 Review를 거쳐 `main`에 병합하는 방식으로 진행

## 2. 공통 API 구조 작성

- `app/apis/practice_apis.py` 생성
- `APIRouter` 설정
- 과제에서 사용할 기본 `user_list` 작성
- `app/schemas/user.py`에 기본 User 모델 작성
- `app/main.py`에 `practice_router` 연결
- 공통 코드를 `main` 브랜치에 반영

## 3. 회원 조회 API 담당

담당 기능: GET 회원 조회

- 전체 회원 조회 API 구현
  - `GET /practice_api/users`
- 특정 회원 조회 API 구현
  - `GET /practice_api/users/{user_id}`
- 회원 조회 시 비밀번호를 제외하고 반환
  - `id`
  - `name`
  - `age`
  - `email`
- 존재하지 않는 회원 ID 조회 시 `404` 예외 처리
- `HTTPException` 추가

## 4. GitHub Flow 실습

GET 기능을 별도의 기능 Branch에서 작업하였다.

```bash
git switch -c feature/get-users