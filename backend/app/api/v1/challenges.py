"""
HTTP-01 ACME 验证路由

特殊路由：/.well-known/acme-challenge/{token}

用于响应 Let's Encrypt HTTP-01 验证请求。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.challenge_service import ChallengeService

# 创建单独的 router（不包含在 /api/v1 前缀）
http01_router = APIRouter()


@http01_router.get(
    "/.well-known/acme-challenge/{token}",
    response_class=str,
    summary="HTTP-01 ACME 验证"
)
async def http01_challenge_response(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    HTTP-01 ACME 验证路由

    Let's Encrypt 会访问：
    http://domain/.well-known/acme-challenge/{token}

    返回格式：{token}.{thumbprint}

    安全说明：
    - 不打印完整 key_authorization（日志脱敏）
    - 只验证 token 是否存在
    """
    service = ChallengeService(db)
    challenge = await service.get_challenge_by_token(token)

    if not challenge:
        raise HTTPException(
            status_code=404,
            detail=f"Challenge token not found: {token[:8]}..."
        )

    # 返回 key_authorization
    # 格式：{token}.{account-key-thumbprint}
    key_authorization = challenge.key_authorization

    # 注意：key_authorization 包含敏感信息
    # 日志中只打印 token 和状态
    from app.core.logging import SecureLogger
    logger = SecureLogger("api.http01")
    logger.info(
        "HTTP-01 challenge responded",
        token_prefix=token[:8],
        order_id=challenge.order_id,
        status=challenge.status
    )

    return key_authorization