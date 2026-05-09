"""
ACME 加密工具模块

用于生成测试用的 dummy certificate（MVP）。
"""

from datetime import datetime, timedelta, timezone
from typing import List

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_dummy_certificate(
    domains: List[str],
    days: int = 90,
    organization: str = "1yuanssl-test",
    country: str = "CN"
) -> str:
    """
    生成测试用的 dummy certificate

    注意：这不是真实证书，仅用于 MVP 测试。

    Args:
        domains: 域名列表（第一个作为 Common Name）
        days: 有效期（天数）
        organization: 组织名称
        country: 国家代码

    Returns:
        cert_pem: PEM 格式的证书链（fullchain）

    安全说明：
    - 此证书不会被浏览器信任
    - 仅用于测试流程，不用于生产
    - 不生成真实私钥（避免误导）
    """
    # 生成临时密钥对（仅用于测试）
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Common Name
    common_name = domains[0]

    # 创建证书
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    # 自签名（issuer = subject）
    issuer = subject

    # 创建证书 builder
    cert_builder = x509.CertificateBuilder()

    # 设置基本信息
    cert_builder = cert_builder.subject_name(subject)
    cert_builder = cert_builder.issuer_name(issuer)

    # 设置有效期
    now = datetime.now(timezone.utc)
    cert_builder = cert_builder.not_valid_before(now)
    cert_builder = cert_builder.not_valid_after(now + timedelta(days=days))

    # 设置序列号
    cert_builder = cert_builder.serial_number(x509.random_serial_number())

    # 设置公钥
    cert_builder = cert_builder.public_key(private_key.public_key())

    # 添加 Subject Alternative Names（SAN）
    san_names = [x509.DNSName(domain) for domain in domains]
    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName(san_names),
        critical=False,
    )

    # 添加基本约束
    cert_builder = cert_builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )

    # 添加 Key Usage
    cert_builder = cert_builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )

    # 签名（使用 SHA256）
    certificate = cert_builder.sign(private_key, hashes.SHA256())

    # 导出 PEM 格式
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    # 注意：不导出私钥（仅返回证书）
    # Mock 环境下私钥由系统生成并加密存储

    # 返回 fullchain（实际上只有单个证书，没有中间证书）
    # 真实证书需要包含中间证书链
    return cert_pem


def generate_privkey_pem() -> str:
    """
    生成私钥 PEM（用于测试）

    安全原则：
    - 返回后立即加密存储
    - 不在日志中打印
    - 不暴露静态下载
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    privkey_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    return privkey_pem