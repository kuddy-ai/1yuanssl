"""
ACME Challenge 模型

记录 ACME 验证挑战信息。

安全原则：
- key_authorization: 加密存储（TODO）
- dns_txt_value: 加密存储（TODO）
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Enum as SQLEnum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class ChallengeStatus(str, enum.Enum):
    """Challenge 状态"""
    PENDING = "pending"  # 待验证
    VALID = "valid"  # 已验证
    INVALID = "invalid"  # 验证失败


class AcmeChallenge(Base):
    """
    ACME Challenge 表

    记录域名验证挑战信息。

    HTTP-01:
    - token: 验证 token
    - key_authorization: 加密存储

    DNS-01:
    - dns_txt_name: TXT 记录名称
    - dns_txt_value: TXT 记录值（加密存储）
    """
    __tablename__ = "acme_challenges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("certificate_orders.id"), nullable=False)

    domain = Column(String(255), nullable=False, comment="域名")
    challenge_type = Column(String(20), nullable=False, comment="验证类型")

    # HTTP-01 验证
    token = Column(String(100), nullable=True, comment="HTTP-01 Token")
    key_authorization = Column(
        Text,
        nullable=True,
        comment="Key Authorization（加密存储）"
    )

    # DNS-01 验证
    dns_txt_name = Column(String(255), nullable=True, comment="DNS TXT 记录名称")
    dns_txt_value = Column(
        Text,
        nullable=True,
        comment="DNS TXT 记录值（加密存储）"
    )

    # 状态
    status = Column(
        SQLEnum(ChallengeStatus),
        nullable=False,
        default=ChallengeStatus.PENDING,
        comment="验证状态"
    )
    validated_at = Column(DateTime, nullable=True, comment="验证时间")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 关系
    order = relationship("CertificateOrder", back_populates="challenges")

    def __repr__(self) -> str:
        return f"<AcmeChallenge(id={self.id}, domain={self.domain}, status={self.status})>"

    @property
    def is_http01(self) -> bool:
        """是否为 HTTP-01 验证"""
        return self.challenge_type == "http-01"

    @property
    def is_dns01(self) -> bool:
        """是否为 DNS-01 验证"""
        return self.challenge_type == "dns-01"