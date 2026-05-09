"""
应用配置模块

使用 Pydantic Settings 从环境变量加载配置。
所有敏感配置都通过环境变量提供，不硬编码在代码中。
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    APP_NAME: str = Field(default="1yuanssl", description="应用名称")
    APP_ENV: str = Field(default="development", description="运行环境")
    DEBUG: bool = Field(default=False, description="调试模式")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    # API 配置
    API_V1_STR: str = Field(default="/api/v1", description="API v1 路径前缀")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/1yuanssl.db",
        description="数据库连接 URL"
    )

    # 加密配置（⚠️ 生产环境必须修改）
    ENCRYPTION_KEY: str = Field(
        default="change-me-in-production-use-strong-random-key",
        description="私钥加密密钥（生产环境必须使用强随机密钥）"
    )

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """验证加密密钥是否为默认值"""
        if v == "change-me-in-production-use-strong-random-key":
            import warnings
            warnings.warn(
                "⚠️  正在使用默认加密密钥！生产环境必须修改 ENCRYPTION_KEY！"
            )
        return v

    # ACME 配置
    ACME_MODE: str = Field(
        default="mock",
        description="ACME 模式：mock/letsencrypt_staging/letsencrypt_prod"
    )
    ACME_DIRECTORY_URL: str = Field(
        default="https://acme-v02.api.letsencrypt.org/directory",
        description="ACME Directory URL"
    )

    # 安全配置
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="允许的主机名"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:7001", "http://localhost:3000", "http://localhost"],
        description="CORS 允许的来源"
    )

    # 后台任务配置
    SCHEDULER_ENABLED: bool = Field(default=False, description="是否启用调度器")
    RENEWAL_CHECK_INTERVAL_HOURS: int = Field(
        default=24,
        description="证书续期检查间隔（小时）"
    )

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.APP_ENV == "development"

    @property
    def is_staging(self) -> bool:
        """是否为 staging 环境"""
        return self.APP_ENV == "staging"


# 全局配置实例
settings = Settings()