from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from utils.logger import LoggingMiddleware, set_project_name
# --- 修改導入 ---
from api.routers import product # 導入 url 和 新的 auth 路由
from api.database import MySQLManager

PROJECT_NAME = 'PRODUCT'
set_project_name(PROJECT_NAME)


# --- Create FastAPI App ---
app = FastAPI(
     title="產品服務 API",
    description="一個用於查詢以及修改產品 FastAPI 應用程式",
    version="1.0.0",
    # lifespan=lifespan # 此專案目前不需要 FastAPI lifespan 管理器
)


# --- 速率限制設定 ---
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter

# --- 自定義速率限制超過的處理器 ---
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": f"Rate limit exceeded. Please try again later. Reason: {exc.detail}"}
    )

# 註冊自定義的異常處理器
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)


# 將 Middleware 添加到應用程式
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(LoggingMiddleware)


# --- 所有 routers 集中在這邊進行管理 ---
app.include_router(product.router)


# --- Root ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Product Service API. Visit /docs for documentation"}

