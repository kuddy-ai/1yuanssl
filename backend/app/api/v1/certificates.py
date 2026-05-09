"""
证书 API 路由

处理证书订单的创建、查询、验证、签发、下载等操作。
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit_event
from app.db import get_db
from app.models.certificate_order import OrderStatus
from app.schemas.certificate_order import (
    CertificateOrderCreate,
    CertificateOrderResponse,
)
from app.schemas.acme_challenge import AcmeChallengeResponse
from app.schemas.certificate_file import CertificateDownloadResponse
from app.schemas.common import SuccessResponse, ErrorResponse
from app.services.certificate_service import CertificateService
from app.services.challenge_service import ChallengeService
from app.services.renewal_service import RenewalService

router = APIRouter()


@router.post(
    "/orders",
    response_model=SuccessResponse[CertificateOrderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="创建证书订单"
)
async def create_certificate_order(
    order_data: CertificateOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建证书订单

    用户提交域名、邮箱、验证方式等信息，系统创建 ACME 订单。

    流程：
    1. 保存订单到数据库
    2. 调用 ACME（Mock）创建订单
    3. 生成 challenges
    """
    service = CertificateService(db)
    order = await service.create_order(order_data)
    audit_event(
        "certificate_order_created",
        actor="admin",
        order_id=order.id,
        domains=order.domains,
        challenge_type=order.challenge_type.value,
    )

    return SuccessResponse(
        data=CertificateOrderResponse.model_validate(order),
        message="Certificate order created successfully"
    )


@router.get(
    "/orders",
    response_model=SuccessResponse[List[CertificateOrderResponse]],
    summary="获取证书订单列表"
)
async def list_certificate_orders(
    status: Optional[OrderStatus] = Query(default=None, description="订单状态"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """获取证书订单列表"""
    service = CertificateService(db)
    orders = await service.list_orders(status=status, limit=limit, offset=offset)

    return SuccessResponse(
        data=[CertificateOrderResponse.model_validate(o) for o in orders]
    )


@router.get(
    "/orders/{order_id}",
    response_model=SuccessResponse[CertificateOrderResponse],
    summary="获取订单详情"
)
async def get_certificate_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取证书订单详情"""
    service = CertificateService(db)
    order = await service.get_order(order_id)

    return SuccessResponse(
        data=CertificateOrderResponse.model_validate(order)
    )


@router.get(
    "/orders/{order_id}/challenges",
    response_model=SuccessResponse[List[AcmeChallengeResponse]],
    summary="获取订单的挑战信息"
)
async def get_order_challenges(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单的 ACME challenge 信息

    HTTP-01: 显示 token 和 key_authorization
    DNS-01: 显示 TXT 记录名称和值
    """
    service = ChallengeService(db)
    challenges = await service.get_challenges_by_order(order_id)

    return SuccessResponse(
        data=[AcmeChallengeResponse.model_validate(c) for c in challenges]
    )


@router.post(
    "/orders/{order_id}/validate",
    response_model=SuccessResponse[CertificateOrderResponse],
    summary="触发验证"
)
async def validate_certificate_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    触发订单验证

    Mock 实现：直接标记为已验证。
    真实实现：调用 ACME validate_challenge。
    """
    service = CertificateService(db)
    order = await service.validate_order(order_id)
    audit_event("certificate_order_validated", actor="admin", order_id=order.id)

    return SuccessResponse(
        data=CertificateOrderResponse.model_validate(order),
        message="Order validation triggered"
    )


@router.post(
    "/orders/{order_id}/issue",
    response_model=SuccessResponse[CertificateOrderResponse],
    summary="申请证书"
)
async def issue_certificate(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    申请证书

    Mock 实现：生成 dummy certificate 并加密存储。
    真实实现：调用 ACME finalize_order + download_certificate。
    """
    service = CertificateService(db)
    order = await service.issue_certificate(order_id)
    audit_event("certificate_issued", actor="admin", order_id=order.id)

    return SuccessResponse(
        data=CertificateOrderResponse.model_validate(order),
        message="Certificate issued successfully"
    )


@router.get(
    "/orders/{order_id}/download/{file_type}",
    response_class=PlainTextResponse,
    summary="下载证书文件"
)
async def download_certificate_file(
    order_id: int,
    file_type: str,  # fullchain/privkey/cert
    db: AsyncSession = Depends(get_db)
):
    """
    下载证书文件

    file_type:
    - fullchain: 证书链（fullchain.pem）
    - privkey: 私钥（privkey.pem）
    - cert: 单个证书（cert.pem）

    安全特性：
    - 通过 API 校验权限（MVP 暂不实现，预留结构）
    - 私钥从加密存储中解密
    - 不暴露静态下载路径
    """
    service = CertificateService(db)
    pem_content = await service.download_certificate(order_id, file_type)
    audit_event(
        "certificate_file_downloaded",
        actor="admin",
        order_id=order_id,
        file_type=file_type,
    )

    # 设置文件名
    filename = f"cert-{order_id}-{file_type}.pem"

    return PlainTextResponse(
        content=pem_content,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.delete(
    "/orders/{order_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="删除证书订单"
)
async def delete_certificate_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除证书订单及其关联数据"""
    service = CertificateService(db)
    await service.delete_order(order_id)
    audit_event("certificate_order_deleted", actor="admin", order_id=order_id)

    return SuccessResponse(
        data=None,
        message="Certificate order deleted successfully"
    )


@router.get(
    "/stats",
    response_model=SuccessResponse[dict],
    summary="获取统计数据"
)
async def get_certificate_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取统计数据（Dashboard）

    返回：
    - total: 总订单数
    - issued: 已签发数
    - failed: 失败数
    - expiring: 即将过期数（30天内）
    """
    service = CertificateService(db)
    stats = await service.get_stats()

    return SuccessResponse(data=stats)


@router.post(
    "/renewals/run",
    response_model=SuccessResponse[dict],
    summary="手动触发续期检查"
)
async def run_renewal_check(
    threshold_days: int = Query(default=30, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    手动触发 Mock 自动续期检查。

    扫描已签发、开启自动续期、且即将在 threshold_days 天内过期的订单。
    """
    service = RenewalService(db)
    result = await service.renew_expiring_certificates(threshold_days=threshold_days)

    return SuccessResponse(data=result, message="Renewal check completed")
