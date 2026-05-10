"""
Certificate Order Pydantic Schemas

用于 API 请求和响应验证。
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.certificate_order import CertificateType, ChallengeType, OrderStatus


class CertificateOrderCreate(BaseModel):
    """创建证书订单请求"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "domains": ["example.com"],
                "email": "admin@example.com",
                "cert_type": "single",
                "challenge_type": "http-01",
                "auto_renew": True,
            }
        }
    )

    domains: list[str] = Field(
        description="域名列表",
        min_length=1,
        max_length=100,
        examples=["example.com", "*.example.com"],
    )
    email: EmailStr = Field(description="联系邮箱")
    cert_type: CertificateType = Field(default=CertificateType.SINGLE, description="证书类型")
    challenge_type: ChallengeType = Field(default=ChallengeType.HTTP_01, description="验证方式")
    auto_renew: bool = Field(default=True, description="是否自动续期")

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, v: list[str]) -> list[str]:
        """验证域名列表"""
        for domain in v:
            if not domain or len(domain) > 255:
                raise ValueError(f"Invalid domain: {domain}")
        return v


class CertificateOrderUpdate(BaseModel):
    """更新证书订单请求"""

    auto_renew: bool | None = Field(default=None, description="是否自动续期")
    status: OrderStatus | None = Field(default=None, description="订单状态")


class CertificateOrderResponse(BaseModel):
    """证书订单响应"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "domains": ["example.com"],
                "email": "admin@example.com",
                "cert_type": "single",
                "challenge_type": "http-01",
                "status": "pending",
                "auto_renew": True,
                "acme_order_url": None,
                "not_before": None,
                "not_after": None,
                "error_message": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "days_until_expiry": None,
                "is_expired": False,
            }
        },
    )

    id: int
    domains: list[str]
    email: str
    cert_type: CertificateType
    challenge_type: ChallengeType
    status: OrderStatus
    auto_renew: bool

    # ACME 信息
    acme_order_url: str | None = None

    # 证书信息
    not_before: datetime | None = None
    not_after: datetime | None = None
    error_message: str | None = None

    # 时间戳
    created_at: datetime
    updated_at: datetime

    # 计算属性
    days_until_expiry: int | None = None
    is_expired: bool = False
