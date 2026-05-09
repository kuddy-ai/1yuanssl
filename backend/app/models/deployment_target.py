"""
部署目标模型

配置证书部署方式。

安全原则：
- config_json: 不保存客户密钥、密码
- SSH: 只保存 host/port/user，密码通过环境变量（TODO）
- Webhook: 使用一次性 token 或客户侧 pull 模式（TODO）
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    Enum as SQLEnum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class DeploymentType(str, enum.Enum):
    """部署类型"""
    WEBHOOK = "webhook"  # Webhook 推送
    SSH = "ssh"  # SSH 部署
    LOCAL_PATH = "local_path"  # 本地路径
    OBJECT_STORAGE = "object_storage"  # 对象存储
    MANUAL_DOWNLOAD = "manual_download"  # 手动下载


class DeploymentTarget(Base):
    """
    部署目标表

    配置证书部署方式。

    安全原则：
    - 不保存客户服务器密码、root SSH 密钥
    - 不保存云账号主密钥
    - Webhook: 使用签名验证，不保存客户密钥
    - SSH: 只保存 host/port/user，密码通过安全方式传递
    - TODO: 后续接入 Vault/KMS 管理敏感配置
    """
    __tablename__ = "deployment_targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("certificate_orders.id"), nullable=False)

    # 部署类型
    type = Column(
        SQLEnum(DeploymentType),
        nullable=False,
        default=DeploymentType.MANUAL_DOWNLOAD,
        comment="部署类型"
    )
    name = Column(String(100), nullable=False, comment="部署名称")

    # 配置（不含敏感信息）
    # 示例：
    # webhook: {"url": "https://...", "method": "POST"}
    # ssh: {"host": "example.com", "port": 22, "user": "root"}
    # local_path: {"path": "/etc/nginx/ssl"}
    config_json = Column(JSON, nullable=False, default={}, comment="配置详情")

    # 状态
    enabled = Column(Boolean, default=False, comment="是否启用")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )

    # 关系
    order = relationship("CertificateOrder", back_populates="deployment_targets")

    def __repr__(self) -> str:
        return f"<DeploymentTarget(id={self.id}, name={self.name}, type={self.type})>"

    @property
    def is_webhook(self) -> bool:
        """是否为 Webhook 部署"""
        return self.type == DeploymentType.WEBHOOK

    @property
    def is_ssh(self) -> bool:
        """是否为 SSH 部署"""
        return self.type == DeploymentType.SSH

    @property
    def is_manual(self) -> bool:
        """是否为手动下载"""
        return self.type == DeploymentType.MANUAL_DOWNLOAD