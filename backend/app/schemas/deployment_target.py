"""
Deployment Target Pydantic Schemas

用于部署目标配置。
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.deployment_target import DeploymentType


class DeploymentTargetCreate(BaseModel):
    """创建部署目标请求"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": 1,
                "type": "manual_download",
                "name": "手动下载",
                "config_json": {},
                "enabled": False,
            }
        }
    )

    order_id: int = Field(description="订单 ID")
    type: DeploymentType = Field(description="部署类型")
    name: str = Field(description="部署名称", min_length=1, max_length=100)
    config_json: dict = Field(default={}, description="配置详情")
    enabled: bool = Field(default=False, description="是否启用")


class DeploymentTargetUpdate(BaseModel):
    """更新部署目标请求"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    config_json: dict | None = Field(default=None)
    enabled: bool | None = Field(default=None)


class DeploymentTargetResponse(BaseModel):
    """部署目标响应"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "order_id": 1,
                "type": "manual_download",
                "name": "手动下载",
                "config_json": {},
                "enabled": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    )

    id: int
    order_id: int
    type: DeploymentType
    name: str
    config_json: dict
    enabled: bool
    created_at: datetime
    updated_at: datetime
