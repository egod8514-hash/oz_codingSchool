# FastAPI와 Docker 기반 헬스케어 웹서비스 배포 3일차 학습 정리

## 1. Docker Compose 기반 다중 컨테이너 아키텍처 구축

* **4대 핵심 서비스 역할 분리**
  * **API 서버 (FastAPI)**: 클라이언트의 HTTP 요청 수신, 비동기(Async) 처리 및 작업 할당 담당.
  * **데이터베이스 (DB)**: 서비스 영구 데이터 저장 담당.
  * **Redis**: API 서버와 LLM 워커 간의 비동기 작업 대기열(Task Queue) 및 Pub/Sub 채널 역할.
  * **LLM 워커 (Llama C++)**: 무거운 AI 추론 연산을 독립적으로 수행하는 백그라운드 워커.

---

## 2. 비동기 API와 동기 LLM 워커 간 메시지 통신 구조

* **구독 우선 규칙 (Subscribe-First)**
  * API 서버는 요청을 받으면 고유 채널 ID(UUID)를 생성한 후 **Pub/Sub 채널을 먼저 구독(Subscribe)**합니다.
  * 워커가 먼저 답변 토큰을 발행(Publish)할 경우 메시지가 손실될 수 있으므로, 수신 대기 상태를 최우선으로 확보합니다.

* **Task Queue 기반 작업 전달**
  * 요청 데이터와 생성된 채널 ID를 JSON 형식으로 패키징하여 Redis 리스트에 `LPUSH`합니다.

* **Blocking RPOP (`BRPOP`)을 활용한 부하 최적화**
  * LLM 워커는 무한 루프 내에서 Blocking 팝(`BRPOP`)을 사용하여 Redis 큐에 새 작업이 들어올 때까지 대기합니다.
  * 주기적으로 큐를 확인하는 폴링(Polling) 방식 대비 CPU 자원 낭비를 방지합니다.

* **LLM 연산의 동기식(Sync) 처리 이유**
  * LLM 추론 연산은 CPU/GPU 집약적인 계산 작업이므로 비동기 이벤트 루프 내에서 실행 시 심각한 오버헤드가 발생할 수 있습니다.
  * 워커 컨테이너 내부에서는 1번에 1개의 작업만 동기식으로 확실하게 처리하여 연산 안정성을 확보합니다.

---

## 3. 의존성 관리 및 수평 확장 (Scale-Out)

* **서비스 실행 순서 보장 (`depends_on`)**
  * DB 및 Redis 인프라 컨테이너가 정상적으로 실행된 후 API 서버 및 LLM 워커가 켜지도록 Docker Compose 세팅을 구성합니다.

* **LLM 워커 컨테이너 수평 확장**
  * `docker-compose up -d --scale llm=2` 명령어를 사용하여 워커 컨테이너 수를 유연하게 확장합니다.
  * 다수의 동시 요청이 들어올 때 여러 워커가 Redis Task Queue를 병렬로 나누어 처리합니다.

---

## 4. LLM 실시간 스트리밍 응답 (Streaming Response) 구현

* **토큰 단위 Redis `PUBLISH` 전송**
  * 라마 모델에서 토큰이 생성되는 즉시 Redis Pub/Sub 채널로 단일 토큰을 퍼블리시합니다.

* **종료 신호 (Stop Sign) 메커니즘**
  * 모델의 텍스트 생성이 완료되면 미리 약속된 특수 문자열(예: `[DONE]`)을 퍼블리시하여 작업 완료를 명시적으로 알립니다.

* **FastAPI `StreamingResponse` 연동**
  * FastAPI 백엔드는 `text/event-stream` 미디어 타입과 비동기 제너레이터(Async Generator)를 사용하여 클라이언트로 토큰을 실시간 전송합니다.
  * 종료 신호(`[DONE]`) 감지 시 비동기 루프를 탈출하고, `finally` 블록에서 Redis 채널 구독 해제(`unsubscribe`) 및 연결 정리(`aclose`)를 수행하여 메모리 누수를 방지합니다.

---

## 5. Docker 이미지 빌드 최적화 및 용량 감축

* **문제 분석**
  * 800MB 이상의 GGUF 대용량 모델 파일이 Docker 이미지 빌드 콘텍스트에 포함되어 빌드 시간이 증가하고 컨테이너 용량이 비대해지는 문제 발생 (약 2.21GB).

* **.dockerignore 활용**
  * `.dockerignore` 파일에 `models/` 경로를 추가하여 빌드 시 모델 파일이 포함되지 않도록 제외합니다.

* **Volume Mount를 통한 성능 최적화**
  * `docker-compose.yml`에서 호스트 시스템의 모델 디렉토리와 컨테이너 내부 디렉토리를 **Volume Mount** 방식으로 연결합니다.
  * 이미지 용량을 1.41GB 수준으로 획기적으로 감축하고 빌드 속도를 대폭 향상시킵니다.

---

## 6. 헬스케어 위험 예측 프로젝트 (Risk Predict) 초기 구조 구축

* **도메인 기반 디렉토리 구조 설계**
  * 사용자 관리(`user/`) 및 건강 위험 예측(`prediction/`) 도메인별로 라우팅, 서비스, ORM 모델을 독립 분리합니다.

* **`APIRouter` 모듈화 통합**
  * 각 도메인 내부에서 `APIRouter`를 작성한 후 메인 애플리케이션(`main.py`)에 `include_router` 방식으로 통합 관리합니다.

* **보안 및 환경변수 관리**
  * `pydantic-settings` 라이브러리와 `.env` 파일을 활용하여 DB 접속 정보 및 API Key 등 민감한 정보를 안전하게 분리 관리합니다.

* **SQLAlchemy 비동기 ORM 기반 DB 모델링**
  * `aiosqlite` 비동기 드라이버를 연동하고 `User` 모델(`id`, `email`, `password_hash`, `created_at`)을 정의하여 비동기 데이터베이스 커넥션을 구축합니다.

---

## 7. 주요 실습 예제 코드

### 7.1 LLM Worker Blocking 팝 및 추론 루프 (`LLM/main.py`)

```python
import json
import redis
from llama_cpp import Llama

# 동기식 Redis 클라이언트 생성 (타임아웃 해제)
redis_client = redis.from_url(
    "redis://redis:6379", decode_responses=True, socket_timeout=None
)

# LLM 모델 로드
llm = Llama(model_path="./models/llama-model.gguf", n_ctx=4096, n_threads=2)


def run():
    while True:
        # BRPOP으로 작업이 들어올 때까지 대기 (CPU 부하 방지)
        _, task_raw = redis_client.brpop("task_queue")
        task_data = json.loads(task_raw)

        channel = task_data["channel"]
        user_input = task_data["user_input"]

        # LLM 스트리밍 추론 실행
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": user_input}],
            max_tokens=512,
            stream=True,
        )

        for chunk in response:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                redis_client.publish(channel, token)  # 토큰 단위 전송

        # 생성 완료 신호 전송
        redis_client.publish(channel, "[DONE]")


if __name__ == "__main__":
    run()
```

### 7.2 FastAPI 스트리밍 핸들러 및 리소스 정리 (`API/main.py`)

```python
import json
import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis

app = FastAPI()
redis_client = aioredis.from_url("redis://redis:6379")


@app.post("/generate")
async def generate_answer(user_input: str):
    channel_id = f"channel_{uuid.uuid4()}"
    pubsub = redis_client.pubsub()

    # 메시지 손실 방지를 위해 수신 구독을 먼저 실행
    await pubsub.subscribe(channel_id)

    # Task Queue에 작업 푸시
    task = json.dumps({"channel": channel_id, "user_input": user_input})
    await redis_client.lpush("task_queue", task)

    async def event_generator():
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    if data == "[DONE]":  # 종료 신호 감지
                        break
                    yield data
        finally:
            # 구독 해제 및 PubSub 연결 정리
            await pubsub.unsubscribe(channel_id)
            await pubsub.aclose()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 7.3 빌드 최적화 및 의존성 설정 (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  db:
    image: sqlite:latest

  redis:
    image: redis:alpine

  api:
    build: ./API
    ports:
      - "9000:9000"
    depends_on:
      - db
      - redis

  llm:
    build: ./LLM
    depends_on:
      - redis
    volumes:
      - ./LLM/models:/app/models  # 모델 파일 호스트 볼륨 바인딩
```

### 7.4 신규 프로젝트 비동기 User ORM 모델 (`database/models.py`)

```python
from datetime import datetime
from database.orm import Base
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(256), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```
