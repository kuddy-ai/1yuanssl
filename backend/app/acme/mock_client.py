"""
Mock ACME 客户端

用于 MVP 测试，不调用真实 Let's Encrypt API。

模拟流程：
1. 创建订单 → 返回 mock order URL
2. 获取挑战 → 返回 mock challenges（HTTP-01/DNS-01）
3. 验证挑战 → 模拟成功
4. 完成订单 → 模拟签发（生成 dummy certificate）
5. 下载证书 → 返回 dummy certificate

安全特性：
- 不调用真实 ACME API（避免 Rate Limit）
- 不生成真实私钥（仅测试流程）
- 所有操作返回模拟数据
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.acme.base import ACMEClientBase
from app.acme.crypto import generate_dummy_certificate
from app.core.logging import SecureLogger

logger = SecureLogger("acme.mock")


class MockACMEClient(ACMEClientBase):
    """
    Mock ACME 客户端（MVP）

    模拟 ACME 协议流程，用于测试。

    TODO: 第二阶段实现真实 Let's Encrypt 客户端
    """

    async def create_account(self, email: str) -> Dict[str, Any]:
        """
        创建 Mock ACME 账户

        返回模拟账户信息。
        """
        account_id = str(uuid.uuid4())
        account_url = f"mock://account/{account_id}"

        logger.info(
            "Mock account created",
            account_id=account_id,
            email=email
        )

        return {
            "url": account_url,
            "status": "valid",
            "contact": [f"mailto:{email}"],
            "created_at": datetime.utcnow().isoformat(),
        }

    async def create_order(self, domains: List[str]) -> Dict[str, Any]:
        """
        创建 Mock ACME 订单

        返回模拟订单 URL 和状态。
        """
        order_id = str(uuid.uuid4())
        order_url = f"mock://order/{order_id}"

        logger.info(
            "Mock order created",
            order_id=order_id,
            domains=domains
        )

        return {
            "url": order_url,
            "status": "pending",
            "domains": domains,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }

    async def get_challenges(self, order_url: str) -> List[Dict[str, Any]]:
        """
        获取 Mock 挑战

        返回模拟 HTTP-01 和 DNS-01 挑战。
        """
        # 从 order URL 提取 order_id
        order_id = order_url.split("/")[-1]

        challenges = []
        for i, domain in enumerate(["example.com", "*.example.com"]):  # Mock domains
            # HTTP-01 挑战
            http01_token = f"mock-token-{order_id[:8]}-{i}"
            http01_challenge = {
                "type": "http-01",
                "url": f"mock://challenge/{order_id}/http01/{i}",
                "domain": domain,
                "token": http01_token,
                "key_authorization": f"{http01_token}.mock-thumbprint",
                "status": "pending",
            }
            challenges.append(http01_challenge)

            # DNS-01 挑战
            dns01_token = f"mock-dns-token-{order_id[:8]}-{i}"
            dns01_challenge = {
                "type": "dns-01",
                "url": f"mock://challenge/{order_id}/dns01/{i}",
                "domain": domain,
                "dns_txt_name": f"_acme-challenge.{domain}",
                "dns_txt_value": dns01_token,
                "status": "pending",
            }
            challenges.append(dns01_challenge)

        logger.info(
            "Mock challenges generated",
            order_id=order_id,
            challenge_count=len(challenges)
        )

        return challenges

    async def validate_challenge(self, challenge_url: str) -> Dict[str, Any]:
        """
        验证 Mock 挑战

        模拟验证成功。
        """
        # 提取 challenge ID
        challenge_id = challenge_url.split("/")[-1]

        logger.info(
            "Mock challenge validated",
            challenge_id=challenge_id,
            status="valid"
        )

        return {
            "url": challenge_url,
            "status": "valid",
            "validated_at": datetime.utcnow().isoformat(),
        }

    async def finalize_order(
        self,
        order_url: str,
        csr: str
    ) -> Dict[str, Any]:
        """
        完成 Mock 订单

        模拟签发成功，返回证书 URL。
        """
        order_id = order_url.split("/")[-1]
        certificate_url = f"mock://certificate/{order_id}"

        logger.info(
            "Mock order finalized",
            order_id=order_id,
            certificate_url=certificate_url
        )

        return {
            "url": order_url,
            "status": "valid",
            "certificate_url": certificate_url,
            "not_before": datetime.utcnow().isoformat(),
            "not_after": (datetime.utcnow() + timedelta(days=90)).isoformat(),
        }

    async def download_certificate(self, certificate_url: str) -> str:
        """
        下载 Mock 证书

        返回生成的 dummy certificate（PEM 格式）。
        """
        # 提取 certificate ID
        cert_id = certificate_url.split("/")[-1]

        # 生成 dummy certificate
        cert_pem = generate_dummy_certificate(
            domains=["example.com", "*.example.com"],
            days=90
        )

        logger.info(
            "Mock certificate downloaded",
            cert_id=cert_id,
            cert_length=len(cert_pem)
        )

        return cert_pem

    async def check_order_status(self, order_url: str) -> Dict[str, Any]:
        """
        检查 Mock 订单状态

        模拟返回订单状态。
        """
        order_id = order_url.split("/")[-1]

        # Mock 状态逻辑
        status = "pending"  # 默认 pending

        logger.info(
            "Mock order status checked",
            order_id=order_id,
            status=status
        )

        return {
            "url": order_url,
            "status": status,
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        }