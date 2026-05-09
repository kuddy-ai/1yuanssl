"""
证书文件模型

存储签发的证书文件（加密存储）。

安全原则：
- 所有私钥文件必须加密存储（AES-256-GCM）
- 不允许静态文件下载，必须通过 API 校验权限
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    LargeBinary,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class CertificateFile(Base):
    """
    证书文件表

    存储签发的证书文件（PEM 格式）。

    安全原则：
    - privkey_pem_encrypted: 私钥必须加密存储
    - fullchain_pem_encrypted: 证书链加密存储
    - 不暴露静态下载路径
    """
    __tablename__ = "certificate_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("certificate_orders.id"), nullable=False, unique=True)

    # 证书文件（加密存储）
    cert_pem_encrypted = Column(LargeBinary, nullable=True, comment="证书 PEM（加密）")
    fullchain_pem_encrypted = Column(LargeBinary, nullable=True, comment="证书链 PEM（加密）")
    privkey_pem_encrypted = Column(
        LargeBinary,
        nullable=True,
        comment="私钥 PEM（加密存储，安全重点）"
    )
    chain_pem_encrypted = Column(LargeBinary, nullable=True, comment="中间证书 PEM（加密）")

    # 元数据
    serial_number = Column(String(100), nullable=True, comment="证书序列号")
    fingerprint = Column(String(100), nullable=True, comment="证书指纹")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系
    order = relationship("CertificateOrder", back_populates="certificate_file")

    def __repr__(self) -> str:
        return f"<CertificateFile(id={self.id}, order_id={self.order_id})>"