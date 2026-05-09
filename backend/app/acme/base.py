"""
ACME 客户端抽象基类

定义 ACME 协议接口，便于后续切换不同实现。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ACMEClientBase(ABC):
    """
    ACME 客户端抽象基类

    支持：
    - Mock 客户端（MVP 测试）
    - Let's Encrypt 客户端（真实）
    - ZeroSSL 客户端（可选）
    """

    @abstractmethod
    async def create_account(self, email: str) -> Dict[str, Any]:
        """
        创建 ACME 账户

        Args:
            email: 联系邮箱

        Returns:
            account_info: 账户信息（包含 account URL）
        """
        pass

    @abstractmethod
    async def create_order(self, domains: List[str]) -> Dict[str, Any]:
        """
        创建 ACME 订单

        Args:
            domains: 域名列表

        Returns:
            order_info: 订单信息（包含 order URL 和 status）
        """
        pass

    @abstractmethod
    async def get_challenges(self, order_url: str) -> List[Dict[str, Any]]:
        """
        获取验证挑战

        Args:
            order_url: ACME 订单 URL

        Returns:
            challenges: 挑战列表（包含 token, type, url）
        """
        pass

    @abstractmethod
    async def validate_challenge(self, challenge_url: str) -> Dict[str, Any]:
        """
        验证挑战（触发 ACME 服务器验证）

        Args:
            challenge_url: 挑战 URL

        Returns:
            validation_result: 验证结果
        """
        pass

    @abstractmethod
    async def finalize_order(
        self,
        order_url: str,
        csr: str
    ) -> Dict[str, Any]:
        """
        完成订单（提交 CSR）

        Args:
            order_url: ACME 订单 URL
            csr: CSR（PEM 格式）

        Returns:
            finalization_result: 完成结果（包含 certificate URL）
        """
        pass

    @abstractmethod
    async def download_certificate(self, certificate_url: str) -> str:
        """
        下载证书

        Args:
            certificate_url: 证书 URL

        Returns:
            certificate_pem: 证书（PEM 格式）
        """
        pass

    @abstractmethod
    async def check_order_status(self, order_url: str) -> Dict[str, Any]:
        """
        检查订单状态

        Args:
            order_url: ACME 订单 URL

        Returns:
            order_status: 订单状态
        """
        pass