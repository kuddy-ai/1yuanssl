"""应用级安全中间件。"""

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import settings
from app.core.rate_limit import FixedWindowRateLimiter

login_rate_limiter = FixedWindowRateLimiter(
    max_requests=settings.LOGIN_RATE_LIMIT_REQUESTS,
    window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """为所有响应添加基础浏览器安全响应头。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return response


class LoginRateLimitMiddleware(BaseHTTPMiddleware):
    """限制管理员登录接口的尝试频率。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == f"{settings.API_V1_STR}/auth/login":
            client_host = request.client.host if request.client else "unknown"
            key = f"login:{client_host}"
            if not login_rate_limiter.allow(key):
                return Response(
                    content='{"detail":"Too many login attempts"}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                )

        return await call_next(request)
