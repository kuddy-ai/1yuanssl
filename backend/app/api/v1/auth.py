"""管理员认证 API。"""

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.core.auth import verify_admin_credentials
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.common import SuccessResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    summary="管理员登录",
)
async def login(payload: LoginRequest):
    """校验管理员账号并返回 API Token。"""
    if not verify_admin_credentials(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return SuccessResponse(
        data=LoginResponse(access_token=settings.ADMIN_API_TOKEN),
        message="Login successful",
    )
