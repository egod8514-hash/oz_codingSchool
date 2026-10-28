# 환자 관리 및 진료기록(의료기록) API 기능명세서

## 1. 개요 및 공통 정책

### 1.1 공통 헤더 및 인증 정책
* **인증 방식:** 임시 인증 헤더 `X-User-Id: {user_id}` 사용 (향후 JWT Bearer 토큰으로 전환 예정)
* **공통 응답 규격:** 기본 JSON 포맷 (단, 진료기록 및 X-Ray 등록 시 `multipart/form-data`)
* **직무 권한 (`RoleEnum`):**
  * `MEDICAL` (의료 실무진): 환자 정보 등록, 진료기록 등록을 포함한 모든 조회/수정/삭제 권한 보유
  * `DEVELOPER` (개발진), `RESEARCHER` (연구진): 환자 목록/상세 조회, 정보 수정/삭제, 진료기록 목록/상세 조회 가능 (등록 기능은 제한)

### 1.2 공통 에러 응답 규격
```json
{
  "detail": "에러 상세 설명 메시지"
}
```

---

## 2. 요구사항별 API 상세 명세

### [REQ-PTNT-001] 환자 정보 등록
* **기능 요약:** 사내 의료인 역할을 가진 유저가 모달을 통해 환자 정보를 등록한다.
* **접근 권한:** `MEDICAL` (의료 실무진 전용)
* **메서드 및 엔드포인트:** `POST /api/v1/patients`

#### 요청 스키마 (`PatientCreateRequest`)
| 필드명 | 타입 | 필수 여부 | 제약조건 / 설명 |
| :--- | :--- | :---: | :--- |
| `name` | string | O | 1~50자 (환자 이름) |
| `age` | integer | O | 0 이상 150 이하 양의 정수 (나이) |
| `gender` | string (Enum) | O | `MALE` / `FEMALE` (성별) |
| `phone_number` | string | O | 정규식 패턴 `^(010\|02\|0[3-9][0-9])-([0-9]{3,4})-([0-9]{4})$` |

#### 요청 예시 (JSON)
```json
{
  "name": "홍길동",
  "age": 45,
  "gender": "MALE",
  "phone_number": "010-1234-5678"
}
```

#### 응답 스키마 (`PatientDetailResponse`)
* **상태 코드:** `201 Created`
```json
{
  "id": 1,
  "name": "홍길동",
  "age": 45,
  "gender": "MALE",
  "phone_number": "010-1234-5678",
  "created_at": "2026-10-27T15:00:00",
  "updated_at": "2026-10-27T15:00:00"
}
```

#### 비즈니스 로직 및 예외 처리
* 호출자의 직무가 `MEDICAL`가 아닌 경우 `403 Forbidden` ("의료 실무진만 환자 등록이 가능합니다.")
* 이미 존재하는 전화번호일 경우 `409 Conflict` ("이미 등록된 연락처입니다.")

---

### [REQ-PTNT-002] 환자 목록 조회
* **기능 요약:** 로그인된 사내 개발진, 의료 실무진, 연구진이 등록된 환자 목록을 검색 및 필터링하여 조회한다.
* **접근 권한:** `MEDICAL`, `DEVELOPER`, `RESEARCHER`
* **메서드 및 엔드포인트:** `GET /api/v1/patients`

#### 쿼리 파라미터 (Query Parameters)
| 파라미터명 | 타입 | 필수 여부 | 기본값 | 설명 |
| :--- | :--- | :---: | :---: | :--- |
| `name` | string | X | null | 환자 이름 검색 (부분 일치 검색) |
| `gender` | string (Enum) | X | null | 성별 필터 (`MALE`, `FEMALE`) |
| `min_age` | integer | X | null | 최소 나이 범위 조건 |
| `max_age` | integer | X | null | 최대 나이 범위 조건 |
| `page` | integer | X | 1 | 페이지 번호 (1부터 시작) |
| `size` | integer | X | 10 | 페이지당 출력 건수 |

#### 응답 스키마 (`PatientListResponse`)
* **상태 코드:** `200 OK`
```json
{
  "total": 1,
  "items": [
    {
      "id": 1,
      "name": "홍길동",
      "age": 45,
      "gender": "MALE",
      "phone_number": "010-1234-5678",
      "created_at": "2026-10-27T15:00:00",
      "updated_at": "2026-10-27T15:00:00"
    }
  ]
}
```

---

### [REQ-PTNT-003] 환자 정보 상세 조회
* **기능 요약:** 환자 목록에서 상세 정보를 확인하기 위해 특정 환자의 단건 정보를 조회한다.
* **접근 권한:** `MEDICAL`, `DEVELOPER`, `RESEARCHER`
* **메서드 및 엔드포인트:** `GET /api/v1/patients/{patient_id}`

#### Path Parameters
| 파라미터명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `patient_id` | integer | 조회 대상 환자 고유 ID |

#### 응답 스키마 (`PatientDetailResponse`)
* **상태 코드:** `200 OK`
```json
{
  "id": 1,
  "name": "홍길동",
  "age": 45,
  "gender": "MALE",
  "phone_number": "010-1234-5678",
  "created_at": "2026-10-27T15:00:00",
  "updated_at": "2026-10-27T15:00:00"
}
```

#### 비즈니스 로직 및 예외 처리
* 해당 ID의 환자가 존재하지 않거나 논리 삭제된 경우 `404 Not Found` ("존재하지 않는 환자 정보입니다.")

---

### [REQ-PTNT-004] 환자 정보 수정
* **기능 요약:** 환자 정보 상세 페이지 모달을 통해 환자의 이름 및 연락처를 수정한다.
* **접근 권한:** `MEDICAL`, `DEVELOPER`, `RESEARCHER`
* **메서드 및 엔드포인트:** `PATCH /api/v1/patients/{patient_id}`

#### 요청 스키마 (`PatientUpdateRequest`)
| 필드명 | 타입 | 필수 여부 | 제약조건 / 설명 |
| :--- | :--- | :---: | :--- |
| `name` | string | X | 1~50자 (변경 시에만 전달) |
| `phone_number` | string | X | 정규식 패턴 `^(010\|02\|0[3-9][0-9])-([0-9]{3,4})-([0-9]{4})$` |

#### 요청 예시 (JSON)
```json
{
  "name": "홍길순",
  "phone_number": "010-9876-5432"
}
```

#### 응답 스키마 (`PatientDetailResponse`)
* **상태 코드:** `200 OK`
```json
{
  "id": 1,
  "name": "홍길순",
  "age": 45,
  "gender": "MALE",
  "phone_number": "010-9876-5432",
  "created_at": "2026-10-27T15:00:00",
  "updated_at": "2026-10-27T15:30:00"
}
```

#### 비즈니스 로직 및 예외 처리
* 수정하려는 `phone_number`가 본인을 제외한 다른 환자에게 이미 등록되어 있는 경우 `409 Conflict`

---

### [REQ-PTNT-005] 환자 정보 삭제
* **기능 요약:** 환자 정보와 관련된 모든 진료기록 및 업로드된 X-Ray 파일을 영구 삭제한다.
* **접근 권한:** `MEDICAL`, `DEVELOPER`, `RESEARCHER`
* **메서드 및 엔드포인트:** `DELETE /api/v1/patients/{patient_id}`

#### Path Parameters
| 파라미터명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `patient_id` | integer | 삭제 대상 환자 고유 ID |

#### 응답 스키마
* **상태 코드:** `204 No Content` (별도 Body 없음)

#### 비즈니스 로직 및 예외 처리
* 대상 환자와 연관된 진료기록(Medical Records) 레코드 삭제
* 연관된 X-Ray 이미지 파일들을 서버 로컬 디스크 저장소에서 파일 시스템 삭제(`os.remove`)
* 환자 엔티티 영구 삭제 (`Hard Delete` 방식 적용)

---

### [REQ-MDR-001] 진료기록 등록
* **기능 요약:** 의료인 역할을 가진 유저가 X-Ray 이미지를 첨부하여 환자의 진료 정보를 등록한다.
* **접근 권한:** `MEDICAL` (의료 실무진 전용)
* **메서드 및 엔드포인트:** `POST /api/v1/patients/{patient_id}/records`
* **Content-Type:** `multipart/form-data`

#### 요청 스키마 (`Form Data`)
| 필드명 | 타입 | 필수 여부 | 제약조건 / 설명 |
| :--- | :--- | :---: | :--- |
| `chart_number` | string (Form) | O | 진료 차트 번호 (고유값/영숫자) |
| `symptom` | string (Form) | O | 진료된 증상 상세 기술 |
| `xray_image` | UploadFile (File) | O | 촬영된 흉부 X-ray 이미지 파일 (`image/png`, `image/jpeg` 등) |

#### 응답 스키마 (`MedicalRecordDetailResponse`)
* **상태 코드:** `201 Created`
```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHT-2026-0001",
  "symptom": "발열 및 기침 증상 지속, 흉부 통증 호소",
  "xray_image_url": "/static/xrays/20261027_uuid.png",
  "created_at": "2026-10-27T15:45:00"
}
```

#### 비즈니스 로직 및 비고사항
* **비고:** 업로드된 원본 이미지 파일은 서버가 실행되는 환경의 로컬 디렉토리(예: `uploads/xrays/`)에 고유 파일명(UUID 기반)으로 저장되고, DB에는 접근 경로(URL)를 기록
* 업로드 파일 확장자가 이미지 형식이 아닐 경우 `400 Bad Request` ("지원되지 않는 이미지 포맷입니다.")
* 환자가 존재하지 않을 경우 `404 Not Found`

---

### [REQ-MDR-002] 진료기록 목록 조회
* **기능 요약:** 특정 환자의 상세 정보 페이지 내에서 해당 환자에게 등록된 모든 진료기록 목록을 조회한다.
* **접근 권한:** `MEDICAL`, `DEVELOPER`, `RESEARCHER`
* **메서드 및 엔드포인트:** `GET /api/v1/patients/{patient_id}/records`

#### Path Parameters
| 파라미터명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `patient_id` | integer | 환자 고유 ID |

#### 응답 스키마 (`MedicalRecordListResponse`)
* **상태 코드:** `200 OK`
* **설명:** 증상(`symptom`) 필드는 100자 초과 시 뒷부분을 생략 부호(`...`) 형태로 축약하여 반환
```json
{
  "items": [
    {
      "id": 1,
      "chart_number": "CHT-2026-0001",
      "symptom": "발열 및 기침 증상 지속...",
      "created_at": "2026-10-27T15:45:00"
    }
  ]
}
```

---

### [REQ-MDR-003] 진료기록 상세 조회
* **기능 요약:** 진료기록 항목의 상세 정보를 확인하기 위해 차트 번호, 원본 증상 전문, 흉부 X-Ray 이미지를 조회한다.
* **접근 권한:** `MEDICAL`, `DEVELOPER`, `RESEARCHER`
* **메서드 및 엔드포인트:** `GET /api/v1/records/{record_id}`

#### Path Parameters
| 파라미터명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `record_id` | integer | 진료기록 고유 ID |

#### 응답 스키마 (`MedicalRecordDetailResponse`)
* **상태 코드:** `200 OK`
```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHT-2026-0001",
  "symptom": "발열 및 기침 증상 지속, 흉부 통증 호소 (전문 출력)",
  "xray_image_url": "/static/xrays/20261027_uuid.png",
  "created_at": "2026-10-27T15:45:00"
}
```

#### 비즈니스 로직 및 예외 처리
* 진료기록 ID가 일치하지 않는 경우 `404 Not Found` ("존재하지 않는 진료기록입니다.")