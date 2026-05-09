"""Mock certificate renewal service."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.acme.crypto import generate_dummy_certificate, generate_privkey_pem
from app.core.audit import audit_event
from app.core.security import encrypt_data
from app.models.certificate_file import CertificateFile
from app.models.certificate_order import CertificateOrder, OrderStatus


class RenewalService:
    """Renew issued mock certificates that are close to expiry."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def renew_expiring_certificates(self, threshold_days: int = 30) -> dict:
        """Renew issued auto-renew orders expiring within threshold_days."""
        now = datetime.utcnow()
        threshold = now + timedelta(days=threshold_days)
        result = await self.db.execute(
            select(CertificateOrder).where(
                CertificateOrder.status == OrderStatus.ISSUED,
                CertificateOrder.auto_renew.is_(True),
                CertificateOrder.not_after.is_not(None),
                CertificateOrder.not_after <= threshold,
            )
        )
        orders = result.scalars().all()
        renewed_order_ids: list[int] = []

        for order in orders:
            await self._renew_order(order)
            renewed_order_ids.append(order.id)
            audit_event("certificate_renewed", actor="system", order_id=order.id)

        await self.db.commit()

        return {
            "checked_at": now.isoformat(),
            "threshold_days": threshold_days,
            "renewed": len(renewed_order_ids),
            "order_ids": renewed_order_ids,
        }

    async def _renew_order(self, order: CertificateOrder) -> None:
        privkey_pem = generate_privkey_pem()
        cert_pem = generate_dummy_certificate(order.domains, days=90)

        result = await self.db.execute(
            select(CertificateFile).where(CertificateFile.order_id == order.id)
        )
        cert_file = result.scalar_one_or_none()
        if cert_file is None:
            cert_file = CertificateFile(order_id=order.id)
            self.db.add(cert_file)

        cert_file.privkey_pem_encrypted = encrypt_data(privkey_pem)
        cert_file.cert_pem_encrypted = encrypt_data(cert_pem)
        cert_file.fullchain_pem_encrypted = encrypt_data(cert_pem)

        order.status = OrderStatus.ISSUED
        order.not_before = datetime.utcnow()
        order.not_after = datetime.utcnow() + timedelta(days=90)
