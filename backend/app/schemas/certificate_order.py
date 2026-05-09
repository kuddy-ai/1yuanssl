"""
Certificate Order Pydantic Schemas

用于 API 请求和响应验证。
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.certificate_order import CertificateType, ChallengeType, OrderStatus


class CertificateOrderCreate(BaseModel):
    """创建证书订单请求"""
    domains: List[str] = Field(
        description="域名列表",
        min_length=1,
        max_length=100,
        examples=["example.com", "*.example.com"]
    )
    email: EmailStr = Field(description="联系邮箱")
    cert_type: CertificateType = Field(
        default=CertificateType.SINGLE,
        description="证书类型"
    )
    challenge_type: ChallengeType = Field(
        default=ChallengeType.HTTP_01,
        description="验证方式"
    )
    auto_renew: bool = Field(default=True, description="是否自动续期")

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, v: List[str]) -> List[str]:
        """验证域名列表"""
        for domain in v:
            if not domain or len(domain) > 255:
                raise ValueError(f"Invalid domain: {domain}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "domains": ["example.com"],
                "email": "admin@example.com",
                "cert_type": "single",
                "challenge_type": "http-01",
                "auto_renew": True
            }
        }


class CertificateOrderUpdate(BaseModel):
    """更新证书订单请求"""
    auto_renew: Optional[bool] = Field(default=None, description="是否自动续期")
    status: Optional[OrderStatus] = Field(default=None, description="订单状态")


class CertificateOrderResponse(BaseModel):
    """证书订单响应"""
    id: int
    domains: List[str]
    email: str
    cert_type: CertificateType
    challenge_type: ChallengeType
    status: OrderStatus
    auto_renew: bool

    # ACME 信息
    acme_order_url: Optional[str] = None

    # 证书信息
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    error_message: Optional[str] = None

    # 时间戳
    created_at: datetime
    updated_at: datetime

    # 计算属性
    days_until_expiry: Optional[int] = None
    is_expired: bool = False

    class Config:
        from_attributes = True
        json_schema_extra = {
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
                "is_expired": False
            }
        }