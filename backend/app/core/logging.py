"""
日志配置模块

安全原则：
- 不打印私钥、token、完整 key_authorization
- 只打印必要的状态信息
- 日志脱敏处理
"""

import logging
import sys
from typing import Any

from app.config import settings


def setup_logging() -> None:
    """
    配置日志系统

    安全特性：
    - 日志脱敏（不打印敏感信息）
    - 按级别过滤
    - 结构化日志格式
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # 配置应用日志器
    logger = logging.getLogger("app")
    logger.setLevel(log_level)

    # 降低第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)


def sanitize_for_log(data: Any) -> Any:
    """
    日志脱敏处理

    安全原则：
    - 私钥：替换为 "[PRIVATE_KEY]"
    - Token：只显示前 8 字符
    - Key Authorization：替换为 "[KEY_AUTH]"
    - 密码：替换为 "[PASSWORD]"
    """
    if isinstance(data, str):
        # 检测私钥
        if "PRIVATE KEY" in data or data.startswith("-----BEGIN"):
            return "[PRIVATE_KEY]"

        # 检测 token（只显示前 8 字符）
        if len(data) > 20 and data.count(".") >= 2:
            # 可能是 key_authorization
            return "[KEY_AUTH]"

        # 检测密码字段
        if "password" in data.lower() or "secret" in data.lower():
            return "[SENSITIVE]"

        return data

    elif isinstance(data, dict):
        # 处理字典
        sanitized = {}
        for key, value in data.items():
            # 敏感字段名检测
            if any(word in key.lower() for word in ["password", "secret", "key", "token", "auth"]):
                sanitized[key] = "[SENSITIVE]"
            else:
                sanitized[key] = sanitize_for_log(value)
        return sanitized

    elif isinstance(data, list):
        # 处理列表
        return [sanitize_for_log(item) for item in data]

    else:
        return data


class SecureLogger:
    """
    安全日志器

    自动对日志内容进行脱敏处理。
    """

    def __init__(self, name: str):
        self.logger = get_logger(name)

    def info(self, message: str, **kwargs) -> None:
        """安全 info 日志"""
        sanitized_kwargs = sanitize_for_log(kwargs)
        self.logger.info(message, **sanitized_kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """安全 warning 日志"""
        sanitized_kwargs = sanitize_for_log(kwargs)
        self.logger.warning(message, **sanitized_kwargs)

    def error(self, message: str, **kwargs) -> None:
        """安全 error 日志"""
        sanitized_kwargs = sanitize_for_log(kwargs)
        self.logger.error(message, **sanitized_kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """安全 debug 日志（开发环境）"""
        if settings.DEBUG:
            sanitized_kwargs = sanitize_for_log(kwargs)
            self.logger.debug(message, **sanitized_kwargs)