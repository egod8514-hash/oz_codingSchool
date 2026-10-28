# 5일차 환자 관리 및 진료기록 API 설계

## 1. API 역할 분담

| 담당 | 요구사항 | 기능 | Method | Endpoint |
|---|---|---|---|---|
| 팀원 1 | REQ-PTNT-001 | 환자 정보 등록 | POST | `/api/v1/patients` |
| 팀원 1 | REQ-PTNT-002 | 환자 목록 조회 | GET | `/api/v1/patients` |
| 팀원 2 | REQ-PTNT-003 | 환자 상세 조회 | GET | `/api/v1/patients/{patient_id}` |
| 팀원 2 | REQ-PTNT-004 | 환자 정보 수정 | PATCH | `/api/v1/patients/{patient_id}` |
| 팀원 3 | REQ-PTNT-005 | 환자 정보 삭제 | DELETE | `/api/v1/patients/{patient_id}` |
| 팀원 3 | REQ-MDR-001 | 진료기록 등록 | POST | `/api/v1/patients/{patient_id}/medical-records` |
| **팀원 4** | **REQ-MDR-002** | **진료기록 목록 조회** | **GET** | `/api/v1/patients/{patient_id}/medical-records` |
| **팀원 4** | **REQ-MDR-003** | **진료기록 상세 조회** | **GET** | `/api/v1/medical-records/{record_id}` |

---

# 2. 브랜치

```text
팀원 1 : feature/patient-create-list
팀원 2 : feature/patient-detail-update
팀원 3 : feature/patient-delete-record-create
팀원 4 : feature/medical-record-read
```

---

# 3. 팀원 4 담당 기능

## REQ-MDR-002 진료기록 목록 조회

특정 환자의 진료기록 전체 목록을 조회한다.

### Method / Endpoint

```text
GET /api/v1/patients/{patient_id}/medical-records
```

### Path Parameter

- `patient_id` : 환자 고유 ID

### Response 예시

```json
{
  "medical_records": [
    {
      "id": 1,
      "patient_id": 1,
      "chart_number": "CHART-0001",
      "symptoms": "기침 및 흉통"
    },
    {
      "id": 2,
      "patient_id": 1,
      "chart_number": "CHART-0002",
      "symptoms": "호흡곤란"
    }
  ]
}
```

### 처리

- 환자가 존재하는지 확인
- 해당 환자의 진료기록 조회
- 진료기록이 여러 개면 목록으로 반환
- 환자가 존재하지 않으면 `404 Not Found`

---

## REQ-MDR-003 진료기록 상세 조회

진료기록 ID를 이용하여 특정 진료기록의 상세 정보를 조회한다.

### Method / Endpoint

```text
GET /api/v1/medical-records/{record_id}
```

### Path Parameter

- `record_id` : 진료기록 고유 ID

### Response 예시

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-0001",
  "symptoms": "기침 및 흉통"
}
```

### 처리

- `record_id`로 진료기록 조회
- 존재하면 상세 정보 반환
- 존재하지 않으면 `404 Not Found`

---

# 4. 공통 파일 구조

```text
app/
├── apis/
│   ├── patients.py
│   └── medical_records.py
│
├── schemas/
│   ├── patient.py
│   └── medical_record.py
│
└── services/
    ├── patient_service.py
    └── medical_record_service.py
```

팀원 4은 주로 다음 파일을 사용한다.

```text
app/apis/medical_records.py
app/schemas/medical_record.py
app/services/medical_record_service.py
```

기존 MedicalRecord 관련 Model이 존재하면 해당 Model을 사용한다.

---

# 5. 작업 순서

```text
최신 main pull
    ↓
feature/medical-record-read 브랜치 생성
    ↓
기존 MedicalRecord Model 확인
    ↓
Schema 작성
    ↓
Service 작성
    ↓
API 작성
    ↓
Swagger 테스트
    ↓
Commit / Push
    ↓
Pull Request
```

## Swagger 테스트

### 진료기록 목록

```text
GET /api/v1/patients/1/medical-records
```

확인:
- 정상 목록 조회
- 진료기록이 없는 경우
- 존재하지 않는 환자

### 진료기록 상세

```text
GET /api/v1/medical-records/1
```

확인:
- 정상 상세 조회
- 존재하지 않는 진료기록
