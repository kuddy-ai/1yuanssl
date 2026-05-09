"""
自定义异常模块

定义应用特定异常类型。
"""

from typing import Optional


class AppException(Exception):
    """应用基础异常"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        detail: Optional[str] = None
    ):
        self.message = message
        self.code = code or "APP_ERROR"
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """资源不存在异常"""

    def __init__(self, resource: str, identifier: int | str):
        super().__init__(
            message=f"{resource} not found",
            code="NOT_FOUND",
            detail=f"{resource} with ID {identifier} does not exist"
        )


class CertificateException(AppException):
    """证书相关异常"""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            code="CERTIFICATE_ERROR",
            detail=detail
        )


class AcmeException(AppException):
    """ACME 协议异常"""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            code="ACME_ERROR",
            detail=detail
        )


class ValidationError(AppException):
    """数据验证异常"""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            detail=detail
        )


class EncryptionException(AppException):
    """加密相关异常"""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(
            message=message,
            code="ENCRYPTION_ERROR",
            detail=detail
        )