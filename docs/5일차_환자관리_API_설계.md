# 5일차 환자관리 API 설계 문서

본 문서는 환자 정보 삭제 및 연관된 진료기록(X-Ray 이미지 포함) 등록을 처리하는 API 명세서입니다.

---

## 1. 환자 정보 삭제 API

### 기본 정보
- **Method / Path:** `DELETE /practice_api/patients/{patient_id}`
- **설명:** 시스템에서 특정 환자의 정보를 삭제합니다. 삭제 시 해당 환자와 연계된 모든 진료기록 및 업로드된 X-Ray 이미지 파일이 함께 연쇄 삭제(Cascade Delete)됩니다.
- **권한:** 의료인 (의사/간호사 역할군만 접근 가능)

### Path Parameters

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :--- | :--- |
| `patient_id` | Integer | 필수 | 삭제할 환자의 고유 식별 번호 |

### Response
#### 🟢 200 OK (성공)
```json
{
  "status": "success",
  "message": "환자 정보 및 연관 데이터가 성공적으로 삭제되었습니다.",
  "data": {
    "patient_id": 123
  }
}
```

#### 🔴 404 Not Found (실패: 대상 없음)
```json
{
  "status": "error",
  "code": "PATIENT_NOT_FOUND",
  "message": "해당 ID를 가진 환자를 찾을 수 없습니다."
}
```

---

## 2. 환자 진료기록 및 X-Ray 등록 API

### 기본 정보
- **Method / Path:** `POST /practice_api/patients/{patient_id}/medical-records`
- **Content-Type:** `multipart/form-data`
- **설명:** 특정 환자의 새로운 진료기록 텍스트 데이터와 X-Ray 이미지 파일을 함께 업로드하여 저장합니다. 데이터베이스 저장에 실패할 경우 파일 업로드도 함께 롤백됩니다.

### Path Parameters

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :--- | :--- |
| `patient_id` | Integer | 필수 | 진료기록을 등록할 환자의 고유 식별 번호 |

### Request Body (Multipart/Form-Data)

| 필드명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :--- | :--- |
| `chart_number` | String | 필수 | 고유 차트 번호 (중복 불가) |
| `diagnosis` | String | 필수 | 의사 진단 소견 및 메모 |
| `treatment_plan`| String | 선택 | 향후 치료 계획 |
| `xray_image` | File | 필수 | X-Ray 이미지 파일 (지원 포맷: JPG, PNG) |

### Response
#### 🟢 201 Created (성공)
```json
{
  "status": "success",
  "message": "진료기록 및 X-Ray 이미지가 성공적으로 등록되었습니다.",
  "data": {
    "record_id": 456,
    "patient_id": 123,
    "chart_number": "CHART-2026-001",
    "xray_url": "/static/uploads/xray/20261027_123.png"
  }
}
```

#### 🔴 404 Not Found (실패: 환자 없음)
```json
{
  "status": "error",
  "code": "PATIENT_NOT_FOUND",
  "message": "진료기록을 등록하려는 환자가 존재하지 않습니다."
}
```

#### 🔴 409 Conflict (실패: 차트 번호 중복)
```json
{
  "status": "error",
  "code": "DUPLICATE_CHART_NUMBER",
  "message": "이미 존재하는 차트 번호입니다. 다른 번호를 입력해 주세요."
}
```
