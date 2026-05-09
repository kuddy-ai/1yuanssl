"""
Certificate File Pydantic Schema

用于证书文件下载响应。
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CertificateFileResponse(BaseModel):
    """证书文件响应"""
    id: int
    order_id: int

    # 元数据
    serial_number: Optional[str] = None
    fingerprint: Optional[str] = None

    # 时间戳
    created_at: datetime

    # 注意：不直接返回加密的证书内容
    # 需要通过专门的下载 API 获取解密后的证书

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "order_id": 1,
                "serial_number": "1234567890abcdef",
                "fingerprint": "sha256:abcdef123456",
                "created_at": "2024-01-01T00:00:00"
            }
        }


class CertificateDownloadResponse(BaseModel):
    """证书下载响应"""
    content: str = Field(description="证书内容（PEM 格式）")
    filename: str = Field(description="建议文件名")
    content_type: str = Field(default="application/x-pem-file", description="内容类型")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "-----BEGIN CERTIFICATE-----...",
                "filename": "example.com-fullchain.pem",
                "content_type": "application/x-pem-file"
            }
        }