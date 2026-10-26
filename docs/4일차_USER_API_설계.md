# 4일차: USER API 명세서

본 문서는 사내 흉부 X-Ray AI 진단 서비스의 사용자 및 인증 도메인 요구사항을 바탕으로 설계된 REST API 명세서입니다.

---

## 1. 공통 보안 및 인가 정책 (NFR 규격)

### 1.1 JWT 토큰 정책 (NFR-USER-001)
* **Access Token**:
  * 유효기간: 30분
  * 페이로드(Payload): 최소 식별 정보인 `user_id`만 포함
  * 전달 방식: HTTP Request Header `Authorization: Bearer <access_token>`
* **Refresh Token**:
  * 유효기간: 7일
  * 전달 방식: 보안 강화를 위해 클라이언트 스크립트(JS) 접근이 불가한 `HttpOnly`, `Secure`, `SameSite=Lax` 쿠키로 전달 (`Set-Cookie`)
* **토큰 재발급**:
  * Access Token 만료 시 Refresh Token을 검증하여 새로운 Access Token 재발급
  * Refresh Token까지 만료된 경우 401 Unauthorized 반환 후 재로그인 유도

### 1.2 권한 체계 (Role)
* `PENDING` (대기자): 마이페이지 외 모든 진단 및 내부 서비스 접근 불가
* `STAFF` (스태프): 흉부 X-Ray 관련 모든 읽기/쓰기/수정 작업 가능
* `ADMIN` (어드민): 시스템 관리자, 모든 항목에 대한 데이터 액세스 및 회원 관리/권한 변경 가능

---

## 2. API 엔드포인트 목록

| 요구사항 ID | 기능 | Method | Endpoint | 접근 권한 |
| :--- | :--- | :---: | :--- | :---: |
| **REQ-USER-001** | 회원가입 | `POST` | `/api/v1/auth/signup` | Public |
| **REQ-USER-002** | 로그인 | `POST` | `/api/v1/auth/login` | Public |
| **NFR-USER-001** | 토큰 재발급 | `POST` | `/api/v1/auth/refresh` | Refresh Cookie 보유자 |
| **REQ-USER-003** | 로그아웃 | `POST` | `/api/v1/auth/logout` | Authenticated |
| **REQ-USER-006** | 마이페이지 조회 | `GET` | `/api/v1/users/me` | Authenticated |
| **REQ-USER-007** | 회원 정보 부분 수정 | `PATCH` | `/api/v1/users/me` | Authenticated |
| **REQ-USER-008** | 비밀번호 변경 | `PATCH` | `/api/v1/users/me/password` | Authenticated |
| **REQ-USER-009** | 회원 탈퇴 | `DELETE` | `/api/v1/users/me` | Authenticated |
| **REQ-USER-004** | 회원 목록 조회 | `GET` | `/api/v1/admin/users` | `ADMIN` |
| **REQ-USER-005** | 회원 권한 변경 | `PATCH` | `/api/v1/admin/users/{user_id}/role` | `ADMIN` |

---

## 3. 엔드포인트별 상세 규격

### 3.1 [REQ-USER-001] 회원가입
* **Endpoint**: `POST /api/v1/auth/signup`
* **설명**: 사내 의료진, 개발 실무진 등의 신규 계정을 등록합니다. 가입 시 기본 권한은 `PENDING`(대기자)으로 생성됩니다.
* **Request Body**:
  ```json
  {
    "email": "doctor@hospital.com",
    "password": "SecurePassword123!",
    "name": "홍길동",
    "department": "의료", // "연구" | "의료" | "개발"
    "gender": "M",        // "M" | "F"
    "phone": "010-1234-5678"
  }
  ```
* **Responses**:
  * `201 Created`:
    ```json
    {
      "message": "회원가입이 완료되었습니다. 관리자 승인 후 서비스 이용이 가능합니다.",
      "user_id": 1
    }
    ```
  * `400 Bad Request`: 입력값 유효성 검증 실패 (이메일 정규식, 비밀번호 규칙 위반 등)
  * `409 Conflict`: 이미 사용 중인 이메일인 경우

---

### 3.2 [REQ-USER-002] 로그인
* **Endpoint**: `POST /api/v1/auth/login`
* **설명**: 이메일과 비밀번호를 검증하고 Access Token(응답 Body)과 Refresh Token(`HttpOnly` 쿠키)을 발급합니다.
* **Request Body**:
  ```json
  {
    "email": "doctor@hospital.com",
    "password": "SecurePassword123!"
  }
  ```
* **Responses**:
  * `200 OK`:
    * **Response Header**: `Set-Cookie: refresh_token=eyJ...; Path=/api/v1/auth; HttpOnly; Secure; SameSite=Lax; Max-Age=604800`
    * **Response Body**:
      ```json
      {
        "access_token": "eyJhbGciOi...",
        "token_type": "bearer",
        "expires_in": 1800
      }
      ```
  * `401 Unauthorized`: 이메일 미존재 또는 비밀번호 불일치

---

### 3.3 [NFR-USER-001] 토큰 재발급 (Refresh)
* **Endpoint**: `POST /api/v1/auth/refresh`
* **설명**: `HttpOnly` 쿠키의 Refresh Token을 확인하여 만료된 Access Token을 새로 발급합니다.
* **Request**: 쿠키(`refresh_token`) 포함
* **Responses**:
  * `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 1800
    }
    ```
  * `401 Unauthorized`: Refresh Token 유효성 만료 (재로그인 필요)

---

### 3.4 [REQ-USER-003] 로그아웃
* **Endpoint**: `POST /api/v1/auth/logout`
* **설명**: 사용자의 세션을 종료하고 브라우저의 Refresh Token 쿠키를 만료 처리합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Responses**:
  * `200 OK`:
    * **Response Header**: `Set-Cookie: refresh_token=; Path=/api/v1/auth; Max-Age=0`
    * **Response Body**:
      ```json
      {
        "message": "로그아웃되었습니다."
      }
      ```

---

### 3.5 [REQ-USER-006] 마이페이지 조회
* **Endpoint**: `GET /api/v1/users/me`
* **설명**: 현재 로그인한 사용자의 프로필 정보를 조회합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Responses**:
  * `200 OK`:
    ```json
    {
      "name": "홍길동",
      "email": "doctor@hospital.com",
      "department": "의료",
      "gender": "M",
      "phone": "010-1234-5678",
      "role": "스태프" // "대기자" | "스태프" | "어드민"
    }
    ```
  * `401 Unauthorized`: 인증 토큰 유효하지 않음

---

### 3.6 [REQ-USER-007] 회원 정보 부분 수정 (Partial Update)
* **Endpoint**: `PATCH /api/v1/users/me`
* **설명**: 로그인한 본인의 부서 또는 휴대폰 번호를 부분 수정합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Request Body** (선택 전달 가능):
  ```json
  {
    "department": "연구",
    "phone": "010-9876-5432"
  }
  ```
* **Responses**:
  * `200 OK`:
    ```json
    {
      "message": "회원 정보가 성공적으로 수정되었습니다.",
      "updated_fields": {
        "department": "연구",
        "phone": "010-9876-5432"
      }
    }
    ```
  * `400 Bad Request`: 부서명 허용 범위 초과 또는 유효하지 않은 전화번호 규격

---

### 3.7 [REQ-USER-008] 비밀번호 변경
* **Endpoint**: `PATCH /api/v1/users/me/password`
* **설명**: 기존 비밀번호를 검증한 후, 새 비밀번호로 교체합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Request Body**:
  ```json
  {
    "current_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456@"
  }
  ```
* **Responses**:
  * `200 OK`:
    ```json
    {
      "message": "비밀번호가 성공적으로 변경되었습니다."
    }
    ```
  * `400 Bad Request`: 새 비밀번호 제약조건 불만족 또는 현재 비밀번호 불일치

---

### 3.8 [REQ-USER-009] 회원 탈퇴
* **Endpoint**: `DELETE /api/v1/users/me`
* **설명**: 본인 계정을 탈퇴하며 요구사항에 따라 데이터베이스에서 관련 데이터를 즉시 물리 삭제(Hard Delete)합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Responses**:
  * `200 OK`:
    * **Response Header**: `Set-Cookie: refresh_token=; Path=/api/v1/auth; Max-Age=0`
    * **Response Body**:
      ```json
      {
        "message": "회원 탈퇴 및 정보 삭제가 정상 완료되었습니다."
      }
      ```

---

### 3.9 [REQ-USER-004] 회원 목록 조회 (관리자 전용)
* **Endpoint**: `GET /api/v1/admin/users`
* **설명**: 관리자 권한(`ADMIN`)으로 전체 회원 목록을 조회합니다. 검색(이메일/이름) 및 부서별 필터링을 지원합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Query Parameters**:
  * `search` (Optional): 검색어 (이메일 또는 이름)
  * `department` (Optional): 부서 필터 (`"연구"` | `"의료"` | `"개발"`)
* **Responses**:
  * `200 OK`:
    ```json
    {
      "items": [
        {
          "id": 1,
          "email": "doctor@hospital.com",
          "name": "홍길동",
          "department": "의료",
          "gender": "M",
          "phone": "010-1234-5678",
          "is_active": true
        }
      ],
      "total": 1
    }
    ```
  * `403 Forbidden`: 관리자 권한이 아닌 계정으로 접근 시

---

### 3.10 [REQ-USER-005] 회원 권한 변경 (관리자 전용)
* **Endpoint**: `PATCH /api/v1/admin/users/{user_id}/role`
* **설명**: 관리자 권한(`ADMIN`)으로 특정 회원의 인가 등급을 변경합니다.
* **Request Header**: `Authorization: Bearer <access_token>`
* **Path Variable**: `user_id` (int) - 대상 사용자 식별자
* **Request Body**:
  ```json
  {
    "role": "스태프" // "대기자" | "스태프" | "어드민"
  }
  ```
* **Responses**:
  * `200 OK`:
    ```json
    {
      "message": "회원 권한이 성공적으로 변경되었습니다.",
      "user_id": 1,
      "updated_role": "스태프"
    }
    ```
  * `400 Bad Request`: 지원하지 않는 권한 명칭 입력 시
  * `403 Forbidden`: 관리자가 아닌 경우
  * `404 Not Found`: 대상 `user_id`가 존재하지 않는 경우