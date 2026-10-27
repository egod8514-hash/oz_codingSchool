from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 작성 중인 practice_apis의 router 불러오기
from app.apis.practice_apis import router as practice_router
from app.apis.users import router as users_router

app = FastAPI(
    title="Hospital User Management API",
    description="사용자 관리 및 마이페이지/어드민 기능 테스트용 서버",
    version="0.1.0"
)

# 프론트엔드 연동 및 브라우저 fetch 테스트를 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 작성된 라우터 등록
app.include_router(practice_router)
app.include_router(users_router, prefix = "/api/v1/users")

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "FastAPI 서버가 정상 동작 중입니다.",
        "docs_url": "/docs"
    }