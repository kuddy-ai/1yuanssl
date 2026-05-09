# 1yuanssl Backend

Let's Encrypt SSL 证书申请管理系统 - 后端 API 服务

## 技术栈

- Python 3.11+
- FastAPI（异步 Web 框架）
- SQLAlchemy 2.x（异步 ORM）
- Pydantic v2（数据校验）
- AES-256-GCM（私钥加密）

## 开发环境启动

```bash
# 使用 uv（推荐）
uv venv
uv pip install -e ".[dev]"
uv run uvicorn app.main:app --reload

# 或使用 pip
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## API 文档

启动后访问：
- Swagger UI: http://localhost:7000/docs
- ReDoc: http://localhost:7000/redoc

## 项目结构

```
backend/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── config.py        # 配置管理
│   ├── models/          # SQLAlchemy 模型
│   ├── schemas/         # Pydantic schemas
│   ├── api/v1/          # API 路由
│   ├── services/        # 业务逻辑层
│   ├── acme/            # ACME 协议层
│   ├── core/            # 加密、日志等核心工具
│   └── db/              # 数据库工具
└── tests/               # 测试
```

## 安全原则

- 私钥使用 AES-256-GCM 加密存储
- 不保存客户机密数据
- 日志脱敏（不打印私钥、token 等敏感信息）

详见项目根目录 README.md