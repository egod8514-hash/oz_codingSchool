# 5일차 환자 관리 및 진료기록 API 설계

## 1. 문서 목적

환자 삭제와 진료기록 등록 기능의 API 계약을 정의한다. 일반 사용자 API의 기존 경로 규칙에 맞춰 `/practice_api`를 사용한다.

>  담당 범위는 `REQ-PTNT-005` 환자 삭제와 `REQ-MDR-001` 진료기록 등록이다.

## 2. 담당 API 요약

| 요구사항 | Method | Endpoint | 설명 |
|---|---|---|---|
| REQ-PTNT-005 | DELETE | `/practice_api/patients/{patient_id}` | 환자와 연관된 진료기록 및 X-Ray 정보 삭제 |
| REQ-MDR-001 | POST | `/practice_api/patients/{patient_id}/medical-records` | 진료기록과 X-Ray 이미지 등록 |

## 3. DELETE 환자 삭제 API

### Endpoint

```http
DELETE /practice_api/patients/{patient_id}
```

### Path Parameter

| 이름 | 타입 | 필수 | 설명 |
|---|---|---:|---|
| `patient_id` | integer | 예 | 삭제할 환자 고유 ID |

### 권한

로그인한 사용자만 요청할 수 있으며, 실제 허용 role은 팀에서 정한 권한 정책을 적용한다. 요구사항상 개발진·의료 실무진·연구진이 환자 삭제를 수행할 수 있는지 최종 확인한다.

### 처리 흐름

1. 인증된 사용자와 권한을 확인한다.
2. `patient_id`로 환자를 조회한다.
3. 환자가 없으면 `404 Not Found`를 반환한다.
4. 환자에게 연결된 진료기록과 X-Ray 이미지 경로를 조회한다.
5. 환자, 진료기록, X-Ray 이미지 DB 정보를 연관관계 cascade 정책에 따라 삭제한다.
6. DB commit 성공 후 서버 로컬 저장소의 실제 X-Ray 파일을 삭제한다.
7. 성공 응답을 반환한다.

### 성공 응답

```http
204 No Content
```

응답 본문은 반환하지 않는다.

### 오류 응답

| 상태 코드 | 상황 |
|---:|---|
| `401` | 로그인 정보가 없음 |
| `403` | 삭제 권한이 없음 |
| `404` | 환자를 찾을 수 없음 |
| `500` | DB 또는 파일 처리 중 서버 오류 |

### 삭제 정책

```text
PatientModel
└── MedicalRecordModel
    └── XrayImagesModel
```

환자 삭제 시 관련 진료기록과 X-Ray 이미지 DB 정보도 삭제한다. X-Ray 이미지가 서버 로컬 파일로 저장되어 있으므로 DB 삭제와 별도로 실제 파일도 삭제한다.

## 4. POST 진료기록 등록 API

### Endpoint

```http
POST /practice_api/patients/{patient_id}/medical-records
```

### Content-Type

```http
multipart/form-data
```

진료기록 텍스트 필드와 X-Ray 파일을 함께 전송해야 하므로 JSON이 아닌 `multipart/form-data`를 사용한다.

### Path Parameter

| 이름 | 타입 | 필수 | 설명 |
|---|---|---:|---|
| `patient_id` | integer | 예 | 진료기록을 등록할 환자 ID |

### Form Data

| 이름 | 타입 | 필수 | 제약 및 설명 |
|---|---|---:|---|
| `chart_number` | string | 예 | 최대 50자, 중복 불가 |
| `symptoms` | string | 예 | 진료된 증상 |
| `xray_image` | file | 예 | JPG 또는 PNG 이미지 |

### 처리 흐름

1. 인증된 사용자와 의료인 권한을 확인한다.
2. `patient_id`로 환자 존재 여부를 확인한다.
3. 업로드 파일의 MIME type을 확인한다.
4. 서버 로컬 저장소 `media/xray/`에 UUID 기반 파일명으로 저장한다.
5. `MedicalRecordModel`을 생성한다.
6. 생성된 진료기록 ID와 업로더 ID를 사용하여 `XrayImagesModel`을 생성한다.
7. DB commit 후 생성 결과를 반환한다.
8. DB 처리 중 오류가 나면 rollback하고 저장된 파일도 삭제한다.

### 성공 요청 예시

```text
POST /practice_api/patients/1/medical-records
Content-Type: multipart/form-data

chart_number: CH-20261027-001
symptoms: 기침과 흉부 통증
xray_image: chest-xray.png
```

### 성공 응답

```http
201 Created
```

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CH-20261027-001",
  "symptoms": "기침과 흉부 통증",
  "xray_image_path": "media/xray/uuid-file.png",
  "created_at": "2026-10-27T17:00:00"
}
```

### 오류 응답

| 상태 코드 | 상황 |
|---:|---|
| `400` | JPG·PNG가 아닌 파일 업로드 |
| `401` | 로그인 정보가 없음 |
| `403` | 진료기록 등록 권한이 없음 |
| `404` | 환자를 찾을 수 없음 |
| `409` | 이미 존재하는 차트 번호 |
| `422` | 필수 Form field 누락 또는 형식 오류 |
| `500` | 파일 저장 또는 DB 처리 오류 |

## 5. 현재 프로젝트 모델과의 매핑

현재 `app/models/`에는 다음 파일이 있다.

```text
app/models/__init__.py
app/models/ai_analysis_results.py
app/models/base.py
app/models/medical_records.py
app/models/patients.py
app/models/users.py
app/models/xray_images.py
```

이번 API에서 사용하는 모델은 다음과 같다.

| 모델 | 역할 |
|---|---|
| `PatientModel` | 환자 정보와 진료기록 관계의 부모 |
| `MedicalRecordModel` | 환자 ID, 차트 번호, 증상 저장 |
| `XrayImagesModel` | 진료기록 ID, 업로더 ID, 이미지 경로 저장 |
| `UserModel` | 현재 로그인 사용자 및 업로더 식별 |

DB 세션은 현재 프로젝트 구조에 맞춰 `AsyncSession`과 `async_get_db`를 사용한다.

## 6. Swagger 검증 시나리오

### 진료기록 등록

1. 테스트 환자를 준비한다.
2. Swagger에서 `POST /practice_api/patients/{patient_id}/medical-records`를 연다.
3. `Try it out`을 클릭한다.
4. `patient_id`, `chart_number`, `symptoms`를 입력한다.
5. JPG 또는 PNG X-Ray 파일을 첨부한다.
6. `Execute`를 클릭한다.
7. `201 Created`와 저장 경로가 반환되는지 확인한다.

### 환자 삭제

1. 진료기록과 X-Ray가 있는 테스트 환자를 준비한다.
2. Swagger에서 `DELETE /practice_api/patients/{patient_id}`를 연다.
3. `Try it out`을 클릭한다.
4. 테스트 환자 ID를 입력하고 실행한다.
5. `204 No Content`를 확인한다.
6. 환자 조회, 진료기록 조회, X-Ray 파일이 모두 삭제되었는지 확인한다.

실제 운영 데이터에는 삭제 API를 실행하지 않고 반드시 테스트 데이터를 사용한다.

## 7. 성능 요구사항

`NFR-PTNT-001`, `NFR-MDR-001`에 따라 모든 API는 최대 3초 이내 응답을 목표로 한다. 파일 업로드 API는 파일 크기 제한과 저장 방식에 따라 처리 시간이 달라질 수 있으므로 테스트 시 응답 시간을 함께 확인한다.
