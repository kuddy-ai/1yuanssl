"""
API v1 路由聚合

所有 v1 版本的 API 路由都在这里聚合。
"""

from fastapi import APIRouter, Depends

from app.api.v1 import auth, health, certificates, challenges
from app.core.auth import require_admin

api_router = APIRouter()

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 注册健康检查路由
api_router.include_router(health.router, prefix="/health", tags=["health"])

# 注册证书路由
api_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["certificates"],
    dependencies=[Depends(require_admin)],
)

# HTTP-01 验证路由需要在主应用中单独注册（特殊路径）
# 不包含在 /api/v1 前缀下
