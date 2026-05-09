"""
最小管理员认证依赖。

MVP 使用环境变量配置的静态 Bearer Token。后续可替换为 JWT/用户表。
"""

from secrets import compare_digest

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


def verify_admin_credentials(username: str, password: str) -> bool:
    """校验管理员用户名和密码。"""
    return compare_digest(username, settings.ADMIN_USERNAME) and compare_digest(
        password,
        settings.ADMIN_PASSWORD,
    )


def verify_admin_token(token: str) -> bool:
    """校验管理员 API Token。"""
    return compare_digest(token, settings.ADMIN_API_TOKEN)


async def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    """要求请求携带有效管理员 Bearer Token。"""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_admin_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
