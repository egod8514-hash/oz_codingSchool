# 6일차 폐렴 예측 API 설계

## 1. 목적

저장된 진료기록의 X-ray 이미지를 AI 모델로 분석하여 폐렴 여부를 예측하고, 결과를 DB에 저장 및 조회한다.

### 전체 흐름

```text
MedicalRecord
    ↓
XrayImages
    ↓
worker/model.py
    ↓
폐렴 예측
    ↓
AnalysisResultModel
    ↓
DB 저장 / 결과 반환
```

---

## 2. 폐렴 예측 API

### POST `/api/v1/medical-records/{record_id}/predictions`

특정 진료기록의 X-ray 이미지로 폐렴 예측을 실행한다.

### 처리 과정

1. 진료기록 확인
2. X-ray 이미지 확인
3. 기존 예측 결과 확인
4. 기존 결과가 없으면 AI 모델 실행
5. `AnalysisResultModel`에 결과 저장
6. 예측 결과 반환

동일한 `record_id + ai_model`의 결과가 이미 존재하면 모델을 다시 실행하지 않고 기존 결과를 반환한다.

### 응답 예시

```json
{
  "record_id": 1,
  "is_pneumonia": true,
  "confidence": 0.9806,
  "ai_model": "PneumoniaModel-v1"
}
```

---

## 3. 예측 결과 조회 API

### GET `/api/v1/medical-records/{record_id}/predictions`

DB에 저장되어 있는 폐렴 예측 결과를 조회한다.

GET 요청에서는 AI 모델을 다시 실행하지 않는다.

---

## 4. 사용 데이터

### XrayImagesModel
- `record_id`
- `image_url`

### AnalysisResultModel
- `record_id`
- `is_pneumonia`
- `confidence`
- `heatmap_url`
- `ai_model`
- `created_at`

---

## 5. AI 모델

`worker/model.py`에서 `SimpleCNN` 구조를 생성하고 `model_state_dict.pth`의 학습된 가중치를 불러와 사용한다.

```text
X-ray
 ↓
128×128 Grayscale
 ↓
SimpleCNN
 ↓
NORMAL / PNEUMONIA
```

모델은 서버 실행 시 한 번 메모리에 로드하여 사용한다.

---

## 6. 예외 처리

- 진료기록 없음 → `404`
- X-ray 이미지 없음 → `404`
- 저장된 예측 결과 없음 → `404`
- 모델 실행 오류 → `500`

---

## 7. 역할 분담

- **AI 모델 담당**: `worker/model.py`
- **Service 담당**: AI 실행 및 DB 저장
- **API 담당**: POST / GET API 및 Schema
- **테스트 담당**: Swagger 테스트 및 문서 정리

---

## 8. 성능 목표

- Recall ≥ 0.90
- Accuracy ≥ 0.80
- API 응답 시간 ≤ 3초

폐렴 판정 threshold는 검증 결과를 확인한 후 최종 결정한다.