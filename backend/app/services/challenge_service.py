"""
Challenge 服务层

处理 ACME challenge 的生成、验证等业务逻辑。
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.acme_challenge import AcmeChallenge, ChallengeStatus
from app.models.certificate_order import CertificateOrder
from app.core.exceptions import NotFoundException


class ChallengeService:
    """Challenge 服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_challenges_by_order(self, order_id: int) -> List[AcmeChallenge]:
        """获取订单的所有挑战"""
        result = await self.db.execute(
            select(AcmeChallenge)
            .where(AcmeChallenge.order_id == order_id)
            .order_by(AcmeChallenge.created_at)
        )
        return result.scalars().all()

    async def get_challenge(self, challenge_id: int) -> AcmeChallenge:
        """获取单个挑战"""
        result = await self.db.execute(
            select(AcmeChallenge).where(AcmeChallenge.id == challenge_id)
        )
        challenge = result.scalar_one_or_none()

        if not challenge:
            raise NotFoundException("AcmeChallenge", challenge_id)

        return challenge

    async def get_challenge_by_token(self, token: str) -> Optional[AcmeChallenge]:
        """
        根据 token 获取 HTTP-01 challenge

        用于 ACME HTTP-01 验证路由。
        """
        result = await self.db.execute(
            select(AcmeChallenge)
            .where(AcmeChallenge.token == token)
            .where(AcmeChallenge.challenge_type == "http-01")
        )
        return result.scalar_one_or_none()

    async def update_challenge_status(
        self,
        challenge_id: int,
        status: ChallengeStatus
    ) -> AcmeChallenge:
        """更新挑战状态"""
        challenge = await self.get_challenge(challenge_id)
        challenge.status = status

        if status == ChallengeStatus.VALID:
            from datetime import datetime
            challenge.validated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(challenge)

        return challenge