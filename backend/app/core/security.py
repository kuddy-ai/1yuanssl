"""
加密和安全工具模块

安全原则：
- 使用 AES-256-GCM 加密私钥
- 密钥来源：环境变量（MVP）→ Vault/KMS（TODO）
- 日志中不打印私钥、token 等敏感信息
"""

import os
import secrets
from typing import Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509 import CertificateSigningRequestBuilder, NameOID

from app.config import settings


def generate_encryption_key() -> bytes:
    """
    生成加密密钥（32 字节）

    用于 AES-256-GCM 加密。

    安全要求：
    - 生产环境必须使用强随机密钥
    - 不要硬编码在代码中
    - TODO: 后续接入 Vault/KMS 管理
    """
    return secrets.token_bytes(32)


def get_encryption_key() -> bytes:
    """
    获取加密密钥（从环境变量）

    安全警告：
    - MVP 使用环境变量，生产环境建议使用 Vault/KMS
    - 默认密钥仅用于测试，生产环境必须修改
    """
    key_str = settings.ENCRYPTION_KEY

    # 如果是默认密钥，生成临时密钥（仅用于开发）
    if key_str == "change-me-in-production-use-strong-random-key":
        import warnings
        warnings.warn("⚠️  使用临时加密密钥，仅适用于开发环境！")
        # 使用固定临时密钥（避免每次重启都生成新密钥）
        return b"development-temporary-key-do-not-use-in-production-!!"[:32]

    # 将字符串转换为 bytes（确保长度为 32）
    key_bytes = key_str.encode("utf-8")
    if len(key_bytes) < 32:
        # 如果密钥太短，填充
        key_bytes = key_bytes + b"0" * (32 - len(key_bytes))
    elif len(key_bytes) > 32:
        # 如果密钥太长，截断
        key_bytes = key_bytes[:32]

    return key_bytes


def encrypt_data(data: str) -> bytes:
    """
    加密数据（AES-256-GCM）

    安全特性：
    - AES-256-GCM 提供加密和完整性验证
    - 随机 nonce（防止密钥重用攻击）
    - 返回 nonce + ciphertext + tag

    Args:
        data: 待加密的字符串

    Returns:
        encrypted: 加密后的 bytes（nonce + ciphertext + tag）

    TODO: 后续接入 Vault/KMS 进行密钥管理
    """
    if not data:
        return b""

    key = get_encryption_key()
    aesgcm = AESGCM(key)

    # 生成随机 nonce（12 bytes）
    nonce = secrets.token_bytes(12)

    # 加密
    ciphertext = aesgcm.encrypt(nonce, data.encode("utf-8"), None)

    # 返回 nonce + ciphertext（ciphertext 包含 tag）
    return nonce + ciphertext


def decrypt_data(encrypted: bytes) -> str:
    """
    解密数据（AES-256-GCM）

    Args:
        encrypted: 加密后的 bytes（nonce + ciphertext + tag）

    Returns:
        data: 解密后的字符串

    Raises:
        ValueError: 如果解密失败（密钥不匹配或数据损坏）
    """
    if not encrypted:
        return ""

    key = get_encryption_key()
    aesgcm = AESGCM(key)

    # 提取 nonce（前 12 bytes）
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]

    # 解密
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")
    except Exception as e:
        raise ValueError(f"解密失败: {e}")


def generate_rsa_keypair(key_size: int = 2048) -> Tuple[str, str]:
    """
    生成 RSA 密钥对

    Args:
        key_size: 密钥大小（默认 2048）

    Returns:
        (private_key_pem, public_key_pem): PEM 格式的密钥对

    安全原则：
    - 私钥生成后立即加密存储
    - 不在日志中打印私钥
    """
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # 导出私钥（PEM 格式）
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    # 导出公钥（PEM 格式）
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return private_key_pem, public_key_pem


def create_csr(
    private_key_pem: str,
    domains: list[str],
    organization: str = "1yuanssl",
    country: str = "CN"
) -> str:
    """
    创建 CSR（Certificate Signing Request）

    Args:
        private_key_pem: PEM 格式的私钥
        domains: 域名列表（第一个作为 Common Name）
        organization: 组织名称
        country: 国家代码

    Returns:
        csr_pem: PEM 格式的 CSR

    安全原则：
    - CSR 不包含敏感信息，可以明文传输
    - 私钥加密存储，使用时临时解密
    """
    # 加载私钥
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=None,
    )

    # 创建 CSR
    common_name = domains[0]
    csr_builder = CertificateSigningRequestBuilder()

    # 添加 Subject
    csr_builder = csr_builder.subject_name(
        [
            (NameOID.COMMON_NAME, common_name),
            (NameOID.ORGANIZATION_NAME, organization),
            (NameOID.COUNTRY_NAME, country),
        ]
    )

    # TODO: 添加 SAN（Subject Alternative Names）
    # 需要 cryptography 库支持

    # 生成 CSR
    csr = csr_builder.sign(private_key, hashes.SHA256())

    # 导出 PEM
    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    return csr_pem


def validate_domain(domain: str) -> bool:
    """
    验证域名格式

    Args:
        domain: 域名

    Returns:
        bool: 是否有效
    """
    if not domain or len(domain) > 255:
        return False

    # 简单验证（TODO: 更严格的域名验证）
    if "." not in domain:
        return False

    # 不允许特殊字符
    invalid_chars = [" ", "\n", "\t", "@", "#", "$", "%", "^", "&", "*"]
    for char in invalid_chars:
        if char in domain:
            return False

    return True