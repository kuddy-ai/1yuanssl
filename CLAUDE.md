# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

1yuanssl 是一个 Let's Encrypt SSL 证书申请管理系统（MVP 阶段）。通过 ACME 协议自动化证书签发流程。**当前使用 Mock ACME 客户端**，不调用真实 Let's Encrypt API。

## 常用命令

### 开发启动
```bash
# Docker 方式（推荐）
make docker-dev          # 启动前后端
make docker-down         # 停止服务
make docker-logs         # 查看日志

# 本地开发（使用 uv + pnpm）
make dev-backend         # 启动后端（端口 7000）
make dev-frontend        # 启动前端（端口 7001）
make install             # 安装所有依赖

# 或使用启动脚本
./start-local.sh         # 一键本地启动
```

### 测试与代码质量
```bash
make test-backend        # 运行后端 pytest 测试
make lint-backend        # Ruff 代码检查
make format-backend      # Ruff 格式化
make lint-frontend       # ESLint 检查
make format-frontend     # Prettier 格式化
```

### 数据库
```bash
make db-init             # 初始化数据库
make db-reset            # 重置（警告：删除所有数据）
```

## 架构说明

### 后端 (`/backend`)
- **入口**: `app/main.py` - FastAPI 应用，包含生命周期管理
- **配置**: `app/config.py` - Pydantic Settings 从环境变量加载
- **API 路由**: `app/api/v1/` - REST 接口按功能组织
- **服务层**: `app/services/` - 业务逻辑（certificate_service, challenge_service）
- **ACME 层**: `app/acme/` - ACME 协议实现（mock_client, 加密工具）
- **核心工具**: `app/core/` - 安全加密（AES-256-GCM）、日志、异常处理
- **数据模型**: `app/models/` - SQLAlchemy ORM 模型
- **数据校验**: `app/schemas/` - Pydantic 请求/响应 schema

### 前端 (`/frontend`)
- **入口**: `src/App.tsx` - React Router 配置
- **页面**: `src/pages/` - Dashboard、CertificateList
- **API 客户端**: `src/api/` - 基于 Axios 的 API 调用
- **组件**: `src/components/` - 共享 Layout 组件
- **类型**: `src/types/` - TypeScript 类型定义

### 端口
- 前端: 7001
- 后端 API: 7000
- API 文档: http://localhost:7000/docs (Swagger UI)

## 安全原则（核心设计理念）

本项目遵循核心原则：**尽量不获取客户机密数据**。

1. **私钥加密存储**: AES-256-GCM，位于 `app/core/security.py`。密钥来自环境变量 `ENCRYPTION_KEY`（MVP）→ 生产环境应使用 Vault/KMS。

2. **禁止存储的数据**: SSH 密码、root 密钥、云账号主密钥、DNS Provider 主密钥。

3. **HTTP-01 验证（推荐）**: 客户将域名指向本系统即可，无需 DNS API 密钥。

4. **DNS-01 手动模式**: 客户手动添加 TXT 记录，平台不保存 DNS API 凭证。

5. **日志脱敏**: 绝不在日志中打印私钥、token 等敏感信息，见 `app/core/logging.py`。

## 代码风格

- 后端: Python 3.11+, Ruff（行宽 100），异步 FastAPI
- 前端: TypeScript, ESLint + Prettier, React 18 + Ant Design
- 包管理器: `uv`（后端，比 pip 快 10-100 倍）、`pnpm`（前端）

## 开发流程

- 开发前先创建或确认对应 GitHub issue。
- 基于该 issue 切换到专门的开发分支，不直接在 `main` 上做功能或修复开发。
- 完成改动后提交 commit。
- 提交 Pull Request，等待检查/Review 后合并 PR。

## 关键文件

- `backend/app/core/security.py`: encrypt_data/decrypt_data - AES-256-GCM 加密
- `backend/app/acme/crypto.py`: generate_dummy_certificate - Mock 证书生成
- `backend/app/services/certificate_service.py`: 证书订单核心业务逻辑
- `backend/app/api/v1/certificates.py`: 证书 API 接口
- `backend/app/api/v1/challenges.py`: HTTP-01 挑战路由（特殊路径，无 /api/v1 前缀）

## 环境变量

见 `.env.example`：
- `ENCRYPTION_KEY`: 生产环境必须修改
- `ACME_MODE`: mock/letsencrypt_staging/letsencrypt_prod
- `DATABASE_URL`: 开发用 sqlite，生产用 PostgreSQL
- `CORS_ORIGINS`: 允许的前端来源
