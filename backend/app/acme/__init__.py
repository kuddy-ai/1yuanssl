"""ACME 协议层模块"""

from app.acme.base import ACMEClientBase
from app.acme.mock_client import MockACMEClient
from app.acme.crypto import generate_dummy_certificate

__all__ = [
    "ACMEClientBase",
    "MockACMEClient",
    "generate_dummy_certificate",
    "get_acme_client",
]


def get_acme_client() -> ACMEClientBase:
    """
    获取 ACME 客户端（根据配置）

    MVP 使用 Mock 客户端，后续支持真实 Let's Encrypt。
    """
    from app.config import settings

    if settings.ACME_MODE == "mock":
        return MockACMEClient()
    else:
        # TODO: 实现真实 Let's Encrypt 客户端
        raise NotImplementedError(f"ACME mode '{settings.ACME_MODE}' not implemented yet")