# 🗄️ Day03 DB 모델 작성과 마이그레이션

## 1. 사용 환경 및 기술 스택

| 항목 | 내용 |
|---|---|
| Database | MySQL Community Server 8.4 LTS / 9.x (`ai_health` 스키마, `utf8mb4`) |
| ORM | SQLAlchemy 2.0 (비동기, `asyncmy` 드라이버) |
| 마이그레이션 도구 | Alembic |
| DB GUI Viewer | DBeaver Community / VS Code Database Client |

---

## 2. 도메인 모델 설계

의료 데이터의 일관성 및 무결성을 보장하기 위해 5개의 핵심 도메인 모델을 설계하고 `app/models/` 경로에 각각 모듈화하여 배치했습니다.

| 테이블 | 파일 경로 | 주요 컬럼 및 역할 |
|---|---|---|
| `users` | `app/models/users.py` | 병원 관계자(의료진, 개발, 연구진) 계정, 권한(`role`), 상태(`is_active`) |
| `patients` | `app/models/patients.py` | 환자 기본 인적사항 (성명, 나이, 성별, 연락처 등) |
| `medical_records` | `app/models/medical_records.py` | 환자별 진료 기록 및 증상 메모 (`patient_id` FK 참조) |
| `xray_images` | `app/models/xray_images.py` | 흉부 X-ray 원본 이미지 메타데이터 (`record_id`, `uploader_id` FK) |
| `ai_analysis_results` | `app/models/ai_analysis_results.py` | AI 폐렴 판독 결과, 확신도(confidence), 히트맵 URL (`record_id` FK) |

- **공통 속성 관리**: `created_at`, `updated_at`, `is_deleted`, `deleted_at`(Soft Delete) 필드를 공통 적용하여 데이터 보존성 확보
- **Alembic 인식**: `alembic/env.py`에서 전체 모델의 `Base.metadata`를 추적할 수 있도록 `app/models/__init__.py`에 모든 엔터티를 등록

---

## 3. 데이터베이스 적용 결과 (DBeaver)

`alembic upgrade head` 명령을 통해 총 5개 비즈니스 엔터티와 버전 관리 테이블(`alembic_version`)이 정상적으로 구축되었으며, DBeaver의 자동 ERD 기능을 통해 외래키(FK) 참조 관계가 연결된 것을 검증했습니다.

![DBeaver ER Diagram](./images/migration_erd.png)

> **확인된 스키마 특징:**
> - `patients` (1) ── (N) `medical_records`
> - `medical_records` (1) ── (N) `xray_images`
> - `medical_records` (1) ── (N) `ai_analysis_results`
> - `users` (1) ── (N) `xray_images`

---

## 4. 트러블슈팅 (Troubleshooting)

### 1) MySQL `is_active` 불리언 기본값 타입 구문 오류 (Error 1067)
- **문제**: `alembic upgrade head` 실행 중 `users` 테이블 생성 단계에서 `asyncmy.errors.OperationalError: (1067, "Invalid default value for 'is_active'")` 오류 발생
- **원인**: MySQL에서 `BOOLEAN` 타입은 내부적으로 `TINYINT(1)`로 변환됩니다. 마이그레이션 생성 시 `server_default='true'`처럼 문자열로 지정되면서 MySQL 파서가 이를 유효하지 않은 기본값으로 판단했습니다.
- **해결**: 파이썬 모델의 기본값을 `default=True` 및 `server_default=sa.text("1")`로 보정하고, 마이그레이션 파일 내의 컬럼 정의를 `sa.text('1')`로 변경하여 해결했습니다.

### 2) DDL 중단 후 재실행 시 "Table already exists" 충돌 (Error 1050)
- **문제**: 직전 에러 수정 후 재실행 시 `Table 'patients' already exists (1050)` 에러 발생
- **원인**: MySQL은 테이블 생성(DDL) 시 암시적 커밋(Implicit Commit)이 수행됩니다. 첫 번째 테이블인 `patients`가 먼저 커밋된 후 두 번째 `users`에서 에러가 발생했기 때문에 전체 롤백이 되지 않고 DB에 잔여 테이블이 남아있었습니다.
- **해결**: 개발 초기 단계이므로 `DROP DATABASE ai_health; CREATE DATABASE ai_health ...`를 통해 데이터베이스를 초기화한 후, 단일 리비전으로 깨끗하게 `alembic upgrade head`를 재적용하여 정합성을 맞췄습니다.

---

## 5. 팀원 로컬 환경 반영 가이드

다른 팀원은 마이그레이션 파일(`alembic revision`)을 다시 생성하지 않고, **아래 순서대로 pull 받아 DB에 적용만 진행**하면 됩니다.

### Step 1. 최신 코드 가져오기
```bash
git checkout develop
git pull origin develop
```

### Step 2. 로컬 MySQL DB 생성
터미널에서 MySQL에 접속해 `ai_health` DB를 생성합니다.
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS ai_health CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Step 3. 환경 변수(`.env`) 설정
프로젝트 루트의 `.env` 파일에 본인의 로컬 접속 정보를 작성합니다.
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=본인_MySQL_비밀번호
DB_NAME=ai_health
```

### Step 4. 가상환경 활성화 및 마이그레이션 적용
```bash
# Mac
source .venv/bin/activate

# Windows (PowerShell)
# .venv\Scripts\activate

# 마이그레이션 일괄 적용
alembic upgrade head
```

### Step 5. DBeaver 연결 확인
- 호스트: `localhost` (또는 `127.0.0.1`)
- 포트: `3306`
- 데이터베이스: `ai_health`
- 사용자/암호: 본인 설정값
- 테이블 6개(`ai_analysis_results`, `alembic_version`, `medical_records`, `patients`, `users`, `xray_images`) 및 다이어그램 생성 여부를 확인합니다.

## Step 6. 스키마 변경(컬럼 추가/수정) 표준 워크플로우

기존 데이터베이스에 신규 컬럼을 추가하거나 수정할 때 사용하는 표준 절차입니다.

---

### SQLAlchemy 모델 코드 수정
추가하려는 도메인 모델 클래스(또는 공통 Mixin)에 신규 필드를 정의합니다.

```python
# 예: 소프트 딜리트 컬럼 추가
is_deleted: Mapped[bool] = mapped_column(
    sa.Boolean,
    server_default=sa.text('0'),
    nullable=False
)
deleted_at: Mapped[datetime | None] = mapped_column(
    sa.DateTime(timezone=True),
    default=None,
    nullable=True
)
```

---

### 신규 리비전 파일 자동 생성
터미널에서 모델의 변경 사항을 감지하는 Alembic 명령어를 실행합니다. (`-m` 옵션 뒤에는 작업 내역을 자유롭게 작성)

```bash
alembic revision --autogenerate -m "Add soft delete columns"
```

---

### 생성된 마이그레이션 스크립트 검증
`alembic/versions/` 디렉터리에 새로 생긴 `.py` 파일을 열어 DDL 구문을 확인합니다.
* `upgrade()` 함수 내부에 `op.add_column(...)` 명령어가 의도대로 포함되었는지 확인
* MySQL 환경에 맞게 기본값(`server_default`) 구문이 적절히 지정되었는지 확인

---

### 데이터베이스에 변경 사항 반영
최신 리비전으로 데이터베이스 스키마를 갱신합니다.

```bash
alembic upgrade head
```

---

### DB Viewer (DBeaver) 반영 확인
1. DBeaver 좌측 네비게이터 트리에서 해당 테이블 우클릭 후 **[새로고침 (F5)]**
2. 테이블 `Properties` 탭의 컬럼 목록 또는 `Diagram` 탭에서 추가된 컬럼 및 타입 반영 확인