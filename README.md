# 1yuanssl - Let's Encrypt SSL 证书申请管理系统

一个傻瓜化的 SSL 证书申请与部署辅助系统。用户在网页上填写域名、邮箱、验证方式等信息后，系统通过 ACME 协议申请 Let's Encrypt SSL 证书，并提供证书下载、自动续期、部署回调等能力。

> ⚠️ **当前版本：MVP（最小可行产品）**
> 本版本使用 Mock ACME 客户端，**不调用真实 Let's Encrypt API**，仅用于演示流程和测试架构。
> 真实 Let's Encrypt 集成将在第二阶段实现。

## 🎯 项目目标

- **傻瓜化**：用户只需填写基本信息，系统自动完成证书申请
- **安全第一**：尽量不获取客户机密数据（核心设计原则）
- **自动化**：支持自动续期、自动部署
- **可扩展**：预留多种部署方式和验证方式接口

## 🏗️ 技术栈

### 后端
- Python 3.11+
- FastAPI（异步 Web 框架）
- SQLAlchemy 2.x（ORM，支持异步）
- Pydantic v2（数据校验）
- APScheduler（后台任务调度，暂未启用）
- AES-256-GCM（私钥加密）

### 前端
- React 18
- TypeScript
- Vite（构建工具）
- Ant Design（UI 组件库）
- Axios（HTTP 客户端）

### 数据库
- SQLite（开发环境）
- PostgreSQL（预留支持）

### 部署
- Docker + Docker Compose
- uv（Python 包管理，比 pip 快 10-100 倍）
- Nginx（前端反向代理）

## 🚀 快速开始

### 方式一：Docker Compose 一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/1yuanssl.git
cd 1yuanssl

# 一键启动（前后端）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

启动后访问：
- **前端**: http://localhost:7001
- **后端 API**: http://localhost:7000/api/v1
- **API 文档**: http://localhost:7000/docs

### 方式二：本地开发（使用 uv）

#### 后端启动

```bash
cd backend

# 安装 uv（如果未安装）
# pip install uv  或
# curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e ".[dev]"

# 启动开发服务器（端口 7000）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 7000
```

#### 前端启动

```bash
cd frontend

# 安装依赖（使用 pnpm）
pnpm install

# 启动开发服务器（端口 7001）
pnpm dev
```

### 方式三：使用 Makefile

```bash
# 查看所有可用命令
make help

# Docker 一键启动
make docker-dev

# 本地开发（后端）
make dev-backend

# 本地开发（前端）
make dev-frontend

# 运行测试
make test-backend

# 清理
make clean
```

## 🔐 安全原则：如何在不获取客户机密数据的情况下完成证书申请和部署

这是本项目的核心设计理念，我们**尽量不获取客户机密数据**，通过以下方式实现：

### 1. HTTP-01 验证（推荐场景）

**适合客户将域名 CNAME 或反代到本系统时使用**

- 客户只需将域名解析到本系统服务器
- 系统自动处理 ACME HTTP-01 验证
- **无需客户提供 DNS API 密钥**
- 客户只需配置反向代理规则

使用场景：
- 客户已有服务器，但希望简化证书申请流程
- 客户愿意将域名临时指向证书管理系统

### 2. DNS-01 验证（手动模式）

**让客户手动添加 TXT 记录**

- 系统生成 DNS TXT 记录信息
- 客户手动添加到 DNS 配置
- 系统验证 TXT 记录生效后继续申请
- **平台不保存客户 DNS API 密钥**

使用场景：
- 泛域名证书申请（*.example.com）
- 客户不希望域名指向本系统

### 3. DNS API 接入（自动模式）

**建议客户使用最小权限 API Token**

- 如果客户选择自动 DNS 验证
- **建议使用仅 DNS TXT 编辑权限的 API Token**
- 不要使用云账号主密钥或 DNS Provider 主密钥
- Token 加密存储，定期轮换

权限示例（Cloudflare）：
```
Zone:DNS:Edit (仅单个 zone)
Zone:Zone:Read (仅读取 zone 信息)
```

### 4. 部署方式推荐

#### 推荐方式：客户侧 Agent 主动拉取

- 客户服务器部署 Agent
- Agent 定期检查证书更新
- Agent 通过 API 拉取新证书
- **无需把服务器 SSH 密码交给平台**

优势：
- 平台不接触客户服务器
- 客户完全控制证书部署时机
- 降低安全风险

#### 避免：平台主动推送（SSH/密码）

- **不要把服务器 SSH 密码、root 密钥交给平台**
- 如果必须使用 SSH 部署：
  - 使用专用部署账号（非 root）
  - 使用 SSH Key（加密存储）
  - TODO: 后续接入 Vault/KMS 管理

### 5. Webhook 模式

**由客户服务器暴露签名验证接口**

- 客户服务器暴露一个 Webhook 接口
- 平台推送带签名的证书更新通知
- 客户服务器验证签名后下载证书
- **不保存客户 Webhook 密钥**

验证方式：
- HMAC 签名（使用一次性 token）
- 时间戳验证（防止重放攻击）
- IP 白名单（可选）

### 6. 私钥管理

#### 方案 A：客户侧生成私钥（最安全）

- 客户本地生成私钥
- 客户提供 CSR（Certificate Signing Request）
- 平台只负责 ACME 流程编排
- **平台不接触私钥**

优势：
- 私钥永远不离开客户环境
- 最高安全级别

#### 方案 B：平台生成私钥（加密存储）

- 平台生成私钥（AES-256-GCM 加密）
- 加密密钥来源：
  - MVP: 环境变量 `ENCRYPTION_KEY`
  - TODO: Vault/KMS（生产环境）
- **私钥不暴露静态下载，必须通过 API**

安全措施：
- 加密密钥不硬编码在代码中
- 私钥下载需要权限验证（预留）
- 日志中不打印私钥信息

### 7. 禁止保存的数据

**以下数据本系统绝不保存：**

- ❌ 客户服务器密码
- ❌ Root SSH 密钥
- ❌ 云账号主密钥（AWS AccessKey、阿里云 AccessKey）
- ❌ DNS Provider 主密钥
- ❌ 数据库密码（客户侧）
- ❌ 其他客户核心机密

**只保存必要数据：**

- ✅ 域名列表（公开信息）
- ✅ 联系邮箱（ACME 需要）
- ✅ 证书文件（加密存储）
- ✅ 部署目标配置（不含敏感信息）

## 📋 当前实现的功能（MVP）

### ✅ 已实现

1. **Docker Compose 一键启动** - 前后端可通过 Docker Compose 启动
2. **FastAPI 后端** - 基础框架和健康检查接口
3. **React 前端** - Dashboard 和证书列表页面
4. **创建证书订单** - 保存到 SQLite 数据库
5. **Mock ACME 客户端** - 模拟 ACME 流程（不调用真实 API）
6. **生成 Mock Challenge** - HTTP-01 和 DNS-01 挑战信息
7. **订单详情查询** - 查看订单状态和挑战信息
8. **模拟签发证书** - 生成 dummy certificate（加密存储）
9. **下载证书文件** - 通过 API 解密并下载 PEM 文件
10. **HTTP-01 验证路由** - /.well-known/acme-challenge/{token}
11. **私钥加密存储** - AES-256-GCM 加密
12. **日志脱敏** - 不打印私钥、token 等敏感信息

### ❌ 第一阶段不实现

1. 真实 Let's Encrypt API 调用
2. DNS-01 自动验证（仅手动确认）
3. 真实 DNS TXT 检查
4. 用户认证登录
5. Webhook/SSH 真实部署
6. 自动续期调度（仅框架）
7. 生产环境配置

## 🔄 API 文档

启动后访问：http://localhost:7000/docs（Swagger UI）

### 核心 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| POST | `/api/v1/certificates/orders` | 创建证书订单 |
| GET | `/api/v1/certificates/orders` | 证书订单列表 |
| GET | `/api/v1/certificates/orders/{id}` | 订单详情 |
| POST | `/api/v1/certificates/orders/{id}/validate` | 触发验证 |
| POST | `/api/v1/certificates/orders/{id}/issue` | 申请证书 |
| GET | `/api/v1/certificates/orders/{id}/download/fullchain` | 下载证书链 |
| DELETE | `/api/v1/certificates/orders/{id}` | 删除订单 |
| GET | `.well-known/acme-challenge/{token}` | HTTP-01 验证 |

## 🗂️ 项目结构

```
1yuanssl/
├── README.md
├── docker-compose.yml
├── Makefile
├── backend/
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置管理
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/v1/          # API 路由
│   │   ├── services/        # 业务逻辑层
│   │   ├── acme/            # ACME 协议层
│   │   ├── core/            # 加密、日志等核心工具
│   │   └── db/              # 数据库工具
│   └── tests/               # 测试
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── api/             # API 客户端
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 共享组件
│   │   ├── types/           # TypeScript 类型
│   │   └── styles/          # 样式
│   ├── Dockerfile
│   └── Dockerfile.dev
│   └── nginx.conf
└── docs/                    # 文档
```

## 🔧 配置说明

### 环境变量

#### Backend `.env`

```bash
# 应用配置
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./data/1yuanssl.db

# 加密密钥（⚠️ 生产环境必须修改）
ENCRYPTION_KEY=change-me-in-production-use-strong-random-key

# ACME 配置
ACME_MODE=mock  # mock/letsencrypt_staging/letsencrypt_prod

# CORS
CORS_ORIGINS=http://localhost:7001,http://localhost:3000
```

#### Frontend `.env`

```bash
VITE_API_BASE_URL=http://localhost:7000/api/v1
```

## 🧪 测试

### 后端测试

```bash
cd backend
uv run pytest tests/ -v
```

### API 测试

```bash
# 健康检查
curl http://localhost:7000/api/v1/health

# 创建订单
curl -X POST http://localhost:7000/api/v1/certificates/orders \
  -H "Content-Type: application/json" \
  -d '{"domains":["example.com"],"email":"admin@example.com","cert_type":"single","challenge_type":"http-01","auto_renew":true}'

# 查看订单
curl http://localhost:7000/api/v1/certificates/orders/1

# 触发验证
curl -X POST http://localhost:7000/api/v1/certificates/orders/1/validate

# 申请证书
curl -X POST http://localhost:7000/api/v1/certificates/orders/1/issue

# 下载证书
curl http://localhost:7000/api/v1/certificates/orders/1/download/fullchain
```

## 🚧 下一步计划（第二阶段）

### 真实 Let's Encrypt 集成

1. 实现 `LetsEncryptClient`
2. 真实 CSR 生成
3. DNS-01 自动验证（支持 Cloudflare、阿里云 DNS）
4. Rate Limit 处理
5. Staging 环境测试
6. 生产环境配置

### 生产功能

1. 用户认证（JWT）
2. 多租户支持
3. 证书监控告警
4. 审计日志
5. Webhook 通知
6. 高可用部署
7. Vault/KMS 集成

## 📚 相关文档

- [API 文档](docs/api.md) - 详细的 API 说明
- [部署指南](docs/deployment.md) - 生产环境部署
- [安全说明](docs/security.md) - 安全设计细节
- [生产部署说明](docs/production.md) - 公网演示/生产环境上线检查

## ⚠️ 注意事项

1. **本版本为 MVP，不建议直接用于生产环境**
2. **使用 Mock ACME，不会申请真实证书**
3. **默认加密密钥仅用于测试，生产环境必须修改**
4. **SQLite 不适合生产环境，请使用 PostgreSQL**
5. **真实 Let's Encrypt 有 Rate Limit（每域名每周 5 次）**

## 📄 License

MIT License

## 🙏 致谢

- Let's Encrypt（免费 SSL 证书）
- FastAPI（优秀的异步框架）
- Ant Design（优秀的 UI 库）
- uv（超快的 Python 包管理器）
