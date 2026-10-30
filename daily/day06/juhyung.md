# 6일차 작업일지 - 안주형

## 오늘 진행한 작업

### 1. 폐렴 AI 예측 기능 연동

- X-Ray 이미지를 이용한 폐렴 AI 예측 기능 확인
- `PneumoniaModel-v1` 모델과 FastAPI 예측 API 연동
- 진료기록에 등록된 X-Ray 이미지를 AI 모델에 전달하도록 연결
- AI 예측 결과를 DB에 저장하고 조회할 수 있도록 기능 확인

### 2. AI 예측 API 확인

다음 API의 동작을 확인하였다.

- `POST /api/v1/medical-records/{record_id}/predictions`
- `GET /api/v1/patients/{patient_id}/predictions`

### 3. 프론트엔드와 API 연결 작업

- 기존 FastAPI API와 `static` 프론트엔드 연결
- 환자 및 진료기록 관련 화면에서 API를 호출할 수 있도록 연결 상태 확인
- AI 예측 결과를 프론트엔드에서 확인할 수 있도록 기능 통합

## 작업 중 확인한 내용

- 환자 정보와 진료기록을 기반으로 AI 예측 API를 호출하는 구조 확인
- X-Ray 이미지 경로와 AI 모델 입력 데이터 연결 과정 확인
- AI 예측 결과와 기존 진료기록의 연결 구조 확인

## 작업 결과

폐렴 AI 모델과 기존 환자/진료기록 API를 연결하고 프론트엔드에서 사용할 수 있도록 통합하였다.