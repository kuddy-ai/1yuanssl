"""Mock renewal service tests."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.certificate_file import CertificateFile
from app.models.certificate_order import CertificateOrder, CertificateType, ChallengeType, OrderStatus
from app.services.renewal_service import RenewalService


@pytest.mark.asyncio
async def test_renewal_service_renews_expiring_auto_renew_order(db_session: AsyncSession) -> None:
    order = CertificateOrder(
        domains=["example.com"],
        email="admin@example.com",
        cert_type=CertificateType.SINGLE,
        challenge_type=ChallengeType.HTTP_01,
        status=OrderStatus.ISSUED,
        auto_renew=True,
        not_before=datetime.utcnow() - timedelta(days=80),
        not_after=datetime.utcnow() + timedelta(days=5),
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    result = await RenewalService(db_session).renew_expiring_certificates(threshold_days=30)

    await db_session.refresh(order)
    assert result["renewed"] == 1
    assert result["order_ids"] == [order.id]
    assert order.not_after > datetime.utcnow() + timedelta(days=80)

    cert_file = (
        await db_session.execute(
            select(CertificateFile).where(CertificateFile.order_id == order.id)
        )
    ).scalar_one()
    assert cert_file.fullchain_pem_encrypted


@pytest.mark.asyncio
async def test_renewal_service_skips_manual_renew_order(db_session: AsyncSession) -> None:
    order = CertificateOrder(
        domains=["example.com"],
        email="admin@example.com",
        cert_type=CertificateType.SINGLE,
        challenge_type=ChallengeType.HTTP_01,
        status=OrderStatus.ISSUED,
        auto_renew=False,
        not_before=datetime.utcnow() - timedelta(days=80),
        not_after=datetime.utcnow() + timedelta(days=5),
    )
    db_session.add(order)
    await db_session.commit()

    result = await RenewalService(db_session).renew_expiring_certificates(threshold_days=30)

    assert result["renewed"] == 0
    assert result["order_ids"] == []
