# 3일차 작업 내용

## 오늘 진행한 작업

### 1. 프로젝트 구조 분석
- 프로젝트의 전체 폴더 구조 확인
- `app/core`, `app/models`, `app/repositories`, `app/schemas`, `app/services`, `app/apis` 역할 확인
- `main.py`, `config.py`, `pyproject.toml`, `uv.lock` 역할 확인
- SQLAlchemy와 Alembic을 이용한 DB 연결 및 Migration 구조 확인
- 프로젝트 구조 분석 내용을 `docs/3일차_프로젝트_뜯어보기.md`로 정리

### 2. DB 모델 작성
- ERD를 기준으로 SQLAlchemy ORM Model 작성
- `User`
- `Patient`
- `MedicalRecord`
- `XrayImage`
- `AIAnalysisResult`
- `Gender`, `Department`, `Role` Enum 작성
- Primary Key / Foreign Key 관계 설정

### 3. MySQL DB 환경 구성
- MySQL Server 및 MySQL Workbench 설정
- `ai_health` Database 생성
- 프로젝트 `.env` DB 접속 정보 설정
- 프로젝트와 MySQL 연결 확인

### 4. Alembic Migration 진행
- 작성한 SQLAlchemy Model을 Alembic에서 인식하도록 Model 등록
- Alembic Migration 파일 생성
- `alembic upgrade head`를 이용하여 MySQL DB에 Schema 적용
- MySQL Workbench에서 생성된 Table 확인

### 5. Migration 오류 해결
- `users.id`와 `xray_images.uploader_id`의 데이터 타입 차이로 Foreign Key 오류 발생
- `xray_images.uploader_id` 타입을 `Integer`로 수정
- Migration 재생성 및 적용
- 최종적으로 DB Table이 정상 생성되는 것 확인

## 작업 결과

- SQLAlchemy ORM을 이용한 DB Model 작성 방법 학습
- Primary Key와 Foreign Key 관계 이해
- Alembic Migration 생성 및 적용 과정 학습
- MySQL과 프로젝트 연결 및 DB Schema 생성 확인
- Migration 과정에서 발생한 Foreign Key 타입 오류 해결