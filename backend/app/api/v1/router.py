"""
API v1 路由聚合

所有 v1 版本的 API 路由都在这里聚合。
"""

from fastapi import APIRouter

from app.api.v1 import health, certificates, challenges

api_router = APIRouter()

# 注册健康检查路由
api_router.include_router(health.router, prefix="/health", tags=["health"])

# 注册证书路由
api_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["certificates"]
)

# HTTP-01 验证路由需要在主应用中单独注册（特殊路径）
# 不包含在 /api/v1 前缀下