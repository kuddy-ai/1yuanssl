# Backend Dockerfile - 使用 uv 管理 Python 依赖
# 多阶段构建，优化镜像大小

# ==================== 构建阶段 ====================
FROM python:3.11-slim AS builder

# 安装 uv（快速 Python 包管理器）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 复制依赖配置
COPY pyproject.toml .

# 使用 uv 安装依赖（比 pip 快 10-100 倍）
RUN uv pip install --system --no-cache -e .

# ==================== 运行阶段 ====================
FROM python:3.11-slim AS runner

WORKDIR /app

# 从构建阶段复制已安装的依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 复制应用代码
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# 创建数据目录（用于 SQLite）
RUN mkdir -p /app/data

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV DATABASE_URL=sqlite+aiosqlite:///./data/1yuanssl.db

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]