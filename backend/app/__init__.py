"""
1yuanssl Backend - Let's Encrypt Certificate Management System

这是一个 MVP 版本，用于演示证书申请流程。

安全原则：
- 私钥加密存储
- 不保存客户机密数据
- 所有敏感信息使用 AES-256-GCM 加密
"""

__version__ = "0.1.0"