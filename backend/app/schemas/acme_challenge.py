"""
ACME Challenge Pydantic Schema
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.acme_challenge import ChallengeStatus


class AcmeChallengeResponse(BaseModel):
    """ACME Challenge 响应"""
    id: int
    order_id: int
    domain: str
    challenge_type: str
    status: ChallengeStatus

    # HTTP-01
    token: Optional[str] = None
    key_authorization: Optional[str] = None

    # DNS-01
    dns_txt_name: Optional[str] = None
    dns_txt_value: Optional[str] = None

    # 时间戳
    validated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @property
    def is_http01(self) -> bool:
        """是否为 HTTP-01 验证"""
        return self.challenge_type == "http-01"

    @property
    def is_dns01(self) -> bool:
        """是否为 DNS-01 验证"""
        return self.challenge_type == "dns-01"

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "order_id": 1,
                "domain": "example.com",
                "challenge_type": "http-01",
                "status": "pending",
                "token": "mock-token-123",
                "key_authorization": "mock-token-123.thumbprint",
                "dns_txt_name": None,
                "dns_txt_value": None,
                "validated_at": None,
                "created_at": "2024-01-01T00:00:00"
            }
        }