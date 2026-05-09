"""
FastAPI 主应用

Let's Encrypt 证书申请管理系统 - 后端 API
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_router
from app.api.v1.challenges import http01_router
from app.db import init_db
from app.core.logging import setup_logging
from app.core.middleware import LoginRateLimitMiddleware, SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时：
    - 初始化数据库
    - 启动后台任务调度器

    关闭时：
    - 关闭调度器
    """
    # 配置日志
    setup_logging()

    # 启动时初始化
    print("🚀 启动 1yuanssl 后端服务...")
    print(f"   环境: {settings.APP_ENV}")
    print(f"   ACME 模式: {settings.ACME_MODE}")
    print(f"   API 文档: http://localhost:7000/docs")

    # 初始化数据库
    await init_db()
    print("✅ 数据库初始化完成")

    from app.tasks.scheduler import start_scheduler
    start_scheduler()

    yield

    # 关闭时清理
    print("🛑 关闭服务...")
    from app.tasks.scheduler import shutdown_scheduler
    shutdown_scheduler()


# 创建 FastAPI 应用
app = FastAPI(
    title="1yuanssl - Let's Encrypt Certificate Manager",
    description="傻瓜化的 SSL 证书申请与部署辅助系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全响应头和基础限流
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoginRateLimitMiddleware)

# 注册 API v1 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 注册 HTTP-01 验证路由（特殊路径，不包含 /api/v1 前缀）
app.include_router(http01_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "1yuanssl",
        "version": "0.1.0",
        "description": "Let's Encrypt Certificate Management System",
        "docs": "/docs",
        "api": settings.API_V1_STR,
        "mode": "mvp",
        "acme_mode": settings.ACME_MODE,
    }


# 主入口
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
