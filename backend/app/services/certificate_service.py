"""
证书服务层

处理证书订单的创建、查询、签发等业务逻辑。
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.certificate_order import CertificateOrder, OrderStatus
from app.models.certificate_file import CertificateFile
from app.models.acme_challenge import AcmeChallenge
from app.acme import get_acme_client, MockACMEClient
from app.acme.crypto import generate_dummy_certificate, generate_privkey_pem
from app.core.security import encrypt_data
from app.core.exceptions import NotFoundException, CertificateException
from app.schemas.certificate_order import CertificateOrderCreate


class CertificateService:
    """证书服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.acme_client = get_acme_client()

    async def create_order(self, order_data: CertificateOrderCreate) -> CertificateOrder:
        """
        创建证书订单

        步骤：
        1. 保存订单到数据库
        2. 调用 ACME 创建订单
        3. 生成 challenges
        """
        # 创建订单记录
        order = CertificateOrder(
            domains=order_data.domains,
            email=order_data.email,
            cert_type=order_data.cert_type,
            challenge_type=order_data.challenge_type,
            status=OrderStatus.PENDING,
            auto_renew=order_data.auto_renew,
        )

        self.db.add(order)
        await self.db.flush()

        # 调用 ACME 创建订单（Mock）
        acme_order = await self.acme_client.create_order(order_data.domains)
        order.acme_order_url = acme_order["url"]

        # 生成 challenges
        challenges = await self.acme_client.get_challenges(acme_order["url"])
        for challenge_data in challenges:
            challenge = AcmeChallenge(
                order_id=order.id,
                domain=challenge_data["domain"],
                challenge_type=challenge_data["type"],
                token=challenge_data.get("token"),
                key_authorization=challenge_data.get("key_authorization"),
                dns_txt_name=challenge_data.get("dns_txt_name"),
                dns_txt_value=challenge_data.get("dns_txt_value"),
            )
            self.db.add(challenge)

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def get_order(self, order_id: int) -> CertificateOrder:
        """获取订单详情"""
        result = await self.db.execute(
            select(CertificateOrder).where(CertificateOrder.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise NotFoundException("CertificateOrder", order_id)

        return order

    async def list_orders(
        self,
        status: Optional[OrderStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[CertificateOrder]:
        """获取订单列表"""
        query = select(CertificateOrder)

        if status:
            query = query.where(CertificateOrder.status == status)

        query = query.order_by(CertificateOrder.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def validate_order(self, order_id: int) -> CertificateOrder:
        """
        触发订单验证

        Mock 实现：直接标记为已验证
        """
        order = await self.get_order(order_id)

        if order.status != OrderStatus.PENDING:
            raise CertificateException(
                f"Order status must be 'pending' to validate",
                detail=f"Current status: {order.status}"
            )

        # Mock：标记所有 challenges 为已验证
        result = await self.db.execute(
            select(AcmeChallenge).where(AcmeChallenge.order_id == order_id)
        )
        challenges = result.scalars().all()

        for challenge in challenges:
            challenge.status = "valid"
            challenge.validated_at = datetime.utcnow()

        order.status = OrderStatus.VALIDATING
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def issue_certificate(self, order_id: int) -> CertificateOrder:
        """
        申请证书

        Mock 实现：生成 dummy certificate 并加密存储
        """
        order = await self.get_order(order_id)

        if order.status not in [OrderStatus.VALIDATING, OrderStatus.PENDING]:
            raise CertificateException(
                f"Order must be validated before issuing",
                detail=f"Current status: {order.status}"
            )

        # Mock：生成私钥和证书
        privkey_pem = generate_privkey_pem()
        cert_pem = generate_dummy_certificate(order.domains, days=90)

        # 加密存储
        privkey_encrypted = encrypt_data(privkey_pem)
        cert_encrypted = encrypt_data(cert_pem)
        fullchain_encrypted = encrypt_data(cert_pem)  # Mock: fullchain = cert

        # 保存证书文件
        cert_file = CertificateFile(
            order_id=order.id,
            privkey_pem_encrypted=privkey_encrypted,
            cert_pem_encrypted=cert_encrypted,
            fullchain_pem_encrypted=fullchain_encrypted,
        )
        self.db.add(cert_file)

        # 更新订单状态
        order.status = OrderStatus.ISSUED
        order.not_before = datetime.utcnow()
        order.not_after = datetime.utcnow() + timedelta(days=90)

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def download_certificate(
        self,
        order_id: int,
        file_type: str = "fullchain"
    ) -> str:
        """
        下载证书文件

        Args:
            order_id: 订单 ID
            file_type: 文件类型（fullchain/privkey/cert）

        Returns:
            pem_content: 解密后的 PEM 内容
        """
        order = await self.get_order(order_id)

        if order.status != OrderStatus.ISSUED:
            raise CertificateException("Certificate not issued yet")

        # 获取证书文件
        result = await self.db.execute(
            select(CertificateFile).where(CertificateFile.order_id == order_id)
        )
        cert_file = result.scalar_one_or_none()

        if not cert_file:
            raise NotFoundException("CertificateFile", order_id)

        # 根据类型解密
        if file_type == "fullchain":
            encrypted = cert_file.fullchain_pem_encrypted
        elif file_type == "privkey":
            encrypted = cert_file.privkey_pem_encrypted
        elif file_type == "cert":
            encrypted = cert_file.cert_pem_encrypted
        else:
            raise CertificateException(f"Invalid file type: {file_type}")

        # 解密
        from app.core.security import decrypt_data
        pem_content = decrypt_data(encrypted)

        return pem_content

    async def delete_order(self, order_id: int) -> None:
        """删除订单"""
        order = await self.get_order(order_id)
        await self.db.delete(order)
        await self.db.commit()

    async def get_stats(self) -> dict:
        """获取统计数据（Dashboard）"""
        # 总订单数
        total_result = await self.db.execute(
            select(CertificateOrder)
        )
        total = len(total_result.scalars().all())

        # 已签发
        issued_result = await self.db.execute(
            select(CertificateOrder).where(CertificateOrder.status == OrderStatus.ISSUED)
        )
        issued = len(issued_result.scalars().all())

        # 失败
        failed_result = await self.db.execute(
            select(CertificateOrder).where(CertificateOrder.status == OrderStatus.FAILED)
        )
        failed = len(failed_result.scalars().all())

        # 即将过期（30天内）
        now = datetime.utcnow()
        expiring_result = await self.db.execute(
            select(CertificateOrder).where(
                CertificateOrder.status == OrderStatus.ISSUED,
                CertificateOrder.not_after < now + timedelta(days=30),
                CertificateOrder.not_after > now
            )
        )
        expiring = len(expiring_result.scalars().all())

        return {
            "total": total,
            "issued": issued,
            "failed": failed,
            "expiring": expiring,
        }