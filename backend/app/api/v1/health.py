"""
健康检查 API

用于检查服务运行状态。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import get_db

router = APIRouter()


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    健康检查接口

    检查：
    - 服务运行状态
    - 数据库连接状态
    """
    # 检查数据库连接
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "service": "1yuanssl-backend",
        "version": "0.1.0",
        "database": db_status,
        "mode": "mvp",
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    就绪检查接口（Kubernetes /readiness）

    检查服务是否已准备好接收请求。
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}