"""
应用配置模块

使用 Pydantic Settings 从环境变量加载配置。
所有敏感配置都通过环境变量提供，不硬编码在代码中。
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator


DEFAULT_ENCRYPTION_KEY = "change-me-in-production-use-strong-random-key"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"
DEFAULT_ADMIN_API_TOKEN = "dev-admin-token"
DEFAULT_CORS_ORIGINS = ["http://localhost:7001", "http://localhost:3000", "http://localhost"]
DEFAULT_ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


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

    # 管理员认证配置（MVP）
    ADMIN_USERNAME: str = Field(default=DEFAULT_ADMIN_USERNAME, description="管理员用户名")
    ADMIN_PASSWORD: str = Field(default=DEFAULT_ADMIN_PASSWORD, description="管理员密码")
    ADMIN_API_TOKEN: str = Field(default=DEFAULT_ADMIN_API_TOKEN, description="管理员 API Token")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/1yuanssl.db",
        description="数据库连接 URL"
    )

    # 加密配置（⚠️ 生产环境必须修改）
    ENCRYPTION_KEY: str = Field(
        default=DEFAULT_ENCRYPTION_KEY,
        description="私钥加密密钥（生产环境必须使用强随机密钥）"
    )

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """验证加密密钥是否为默认值"""
        if v == DEFAULT_ENCRYPTION_KEY:
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
        default=DEFAULT_ALLOWED_HOSTS,
        description="允许的主机名"
    )
    CORS_ORIGINS: List[str] = Field(
        default=DEFAULT_CORS_ORIGINS,
        description="CORS 允许的来源"
    )

    # 后台任务配置
    SCHEDULER_ENABLED: bool = Field(default=False, description="是否启用调度器")
    RENEWAL_CHECK_INTERVAL_HOURS: int = Field(
        default=24,
        description="证书续期检查间隔（小时）"
    )

    # 基础限流配置
    LOGIN_RATE_LIMIT_REQUESTS: int = Field(default=5, description="登录窗口内最大尝试次数")
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, description="登录限流窗口秒数")

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

    @model_validator(mode="after")
    def validate_production_safety(self) -> "Settings":
        """生产环境禁止使用本地开发默认安全配置。"""
        if not self.is_production:
            return self

        errors: list[str] = []
        if self.DEBUG:
            errors.append("DEBUG must be false in production")
        if self.ENCRYPTION_KEY == DEFAULT_ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY must be changed in production")
        if self.ADMIN_PASSWORD == DEFAULT_ADMIN_PASSWORD:
            errors.append("ADMIN_PASSWORD must be changed in production")
        if self.ADMIN_API_TOKEN == DEFAULT_ADMIN_API_TOKEN:
            errors.append("ADMIN_API_TOKEN must be changed in production")
        if self.CORS_ORIGINS == DEFAULT_CORS_ORIGINS:
            errors.append("CORS_ORIGINS must be restricted to production frontend origins")
        if self.ALLOWED_HOSTS == DEFAULT_ALLOWED_HOSTS:
            errors.append("ALLOWED_HOSTS must include production hostnames")

        if errors:
            raise ValueError("; ".join(errors))

        return self


# 全局配置实例
settings = Settings()
