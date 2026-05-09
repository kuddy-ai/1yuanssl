"""
通用 Pydantic Schemas

用于 API 响应和错误处理。
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(default=False)
    error: str = Field(description="错误信息")
    detail: Optional[str] = Field(default=None, description="详细错误")
    code: Optional[str] = Field(default=None, description="错误代码")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Certificate order not found",
                "detail": "Order ID 123 does not exist",
                "code": "NOT_FOUND"
            }
        }


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应"""
    success: bool = Field(default=True)
    data: T = Field(description="响应数据")
    message: Optional[str] = Field(default=None, description="成功消息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {},
                "message": "Operation completed successfully"
            }
        }


class PaginationMeta(BaseModel):
    """分页元数据"""
    total: int = Field(description="总数")
    page: int = Field(description="当前页")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    success: bool = Field(default=True)
    data: List[T] = Field(description="数据列表")
    meta: PaginationMeta = Field(description="分页信息")