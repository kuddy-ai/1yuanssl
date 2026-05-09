"""认证相关 schemas。"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """管理员登录请求。"""

    username: str = Field(description="管理员用户名")
    password: str = Field(description="管理员密码")


class LoginResponse(BaseModel):
    """管理员登录响应。"""

    access_token: str
    token_type: str = "bearer"
