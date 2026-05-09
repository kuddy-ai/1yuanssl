"""
证书订单模型

核心数据模型，记录证书申请的所有信息。
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    LargeBinary,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class CertificateType(str, enum.Enum):
    """证书类型"""
    SINGLE = "single"  # 单域名
    WILDCARD = "wildcard"  # 泛域名
    MULTI = "multi"  # 多域名


class ChallengeType(str, enum.Enum):
    """验证方式"""
    HTTP_01 = "http-01"
    DNS_01 = "dns-01"


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"  # 待处理
    VALIDATING = "validating"  # 正在验证
    ISSUED = "issued"  # 已签发
    FAILED = "failed"  # 失败
    EXPIRED = "expired"  # 已过期
    RENEWING = "renewing"  # 正在续期


class CertificateOrder(Base):
    """
    证书订单表

    记录用户提交的证书申请信息。

    安全原则：
    - acme_account_key_encrypted: 加密存储
    - csr_encrypted: 加密存储
    - 不保存客户服务器密码、SSH 密钥等敏感信息
    """
    __tablename__ = "certificate_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基础信息
    domains = Column(JSON, nullable=False, comment="域名列表")
    email = Column(String(255), nullable=False, comment="联系邮箱")
    cert_type = Column(
        SQLEnum(CertificateType),
        nullable=False,
        default=CertificateType.SINGLE,
        comment="证书类型"
    )
    challenge_type = Column(
        SQLEnum(ChallengeType),
        nullable=False,
        default=ChallengeType.HTTP_01,
        comment="验证方式"
    )
    status = Column(
        SQLEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        comment="订单状态"
    )
    auto_renew = Column(Boolean, default=True, comment="是否自动续期")

    # ACME 相关
    acme_order_url = Column(String(500), nullable=True, comment="ACME 订单 URL")
    acme_account_key_encrypted = Column(
        LargeBinary,
        nullable=True,
        comment="ACME Account Key（加密存储）"
    )

    # 证书信息
    not_before = Column(DateTime, nullable=True, comment="证书生效时间")
    not_after = Column(DateTime, nullable=True, comment="证书过期时间")
    csr_encrypted = Column(LargeBinary, nullable=True, comment="CSR（加密存储）")
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 关系
    challenges = relationship(
        "AcmeChallenge",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    certificate_file = relationship(
        "CertificateFile",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan"
    )
    deployment_targets = relationship(
        "DeploymentTarget",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CertificateOrder(id={self.id}, domains={self.domains}, status={self.status})>"

    @property
    def is_expired(self) -> bool:
        """证书是否过期"""
        if self.not_after:
            return datetime.utcnow() > self.not_after
        return False

    @property
    def days_until_expiry(self) -> Optional[int]:
        """距离过期天数"""
        if self.not_after:
            delta = self.not_after - datetime.utcnow()
            return delta.days
        return None