.PHONY: help install dev build docker-up docker-down clean test

help: ## 显示帮助信息
	@echo "可用命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ==================== uv + pnpm 安装命令 ====================
install-backend: ## 使用 uv 安装后端依赖
	cd backend && uv venv && uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -e ".[dev]"

install-frontend: ## 使用 pnpm 安装前端依赖
	cd frontend && pnpm install

install: install-backend install-frontend ## 安装所有依赖

# ==================== 本地开发命令 ====================
dev-backend: ## 启动后端开发服务器（本地 uv，端口 7000）
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 7000

dev-frontend: ## 启动前端开发服务器（本地 pnpm，端口 7001）
	cd frontend && pnpm dev

dev: ## 同时启动前后端（需要两个终端）
	@echo "请在两个终端分别运行："
	@echo "  make dev-backend"
	@echo "  make dev-frontend"

# ==================== Docker 开发命令 ====================
docker-dev: ## 启动 Docker 开发环境（一键启动前后端）
	docker compose up -d
	@echo ""
	@echo "✅ 服务已启动："
	@echo "   前端: http://localhost:7001"
	@echo "   后端 API: http://localhost:7000/api/v1"
	@echo "   API 文档: http://localhost:7000/docs"
	@echo ""
	@echo "查看日志: make docker-logs"
	@echo "停止服务: make docker-down"

docker-prod: ## 启动 Docker 生产环境（带 Nginx）
	docker compose --profile production up -d
	@echo "服务已启动: http://localhost"

docker-down: ## 停止 Docker 服务
	docker compose down

docker-logs: ## 查看 Docker 日志
	docker compose logs -f

docker-build: ## 重新构建 Docker 镜像
	docker compose build --no-cache

# ==================== 数据库命令 ====================
db-init: ## 初始化数据库（本地）
	cd backend && uv run python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"

db-migrate: ## 运行数据库迁移（本地）
	cd backend && uv run alembic upgrade head

db-reset: ## 重置数据库
	@echo "⚠️  这将删除所有数据！"
	rm -rf backend/data/*.db
	cd backend && uv run python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"

# ==================== 测试命令 ====================
test-backend: ## 运行后端测试（本地 uv）
	cd backend && uv run pytest tests/ -v

test-frontend: ## 运行前端测试
	cd frontend && pnpm test

test: test-backend test-frontend ## 运行所有测试

# ==================== 清理命令 ====================
clean: ## 清理构建产物和临时文件
	@echo "清理 Docker..."
	docker compose down -v --remove-orphans 2>/dev/null || true
	@echo "清理前端..."
	rm -rf frontend/node_modules frontend/dist
	@echo "清理后端虚拟环境..."
	rm -rf backend/.venv
	@echo "✅ 清理完成"

clean-all: ## 清理所有（包括数据）
	docker compose down -v --remove-orphans --rmi all 2>/dev/null || true
	rm -rf backend/.venv backend/data frontend/node_modules frontend/dist

# ==================== 代码质量命令 ====================
lint-backend: ## 后端代码检查（本地 uv）
	cd backend && uv run ruff check app/ tests/

lint-frontend: ## 前端代码检查
	cd frontend && pnpm lint

format-backend: ## 格式化后端代码（本地 uv）
	cd backend && uv run ruff format app/ tests/

format-frontend: ## 格式化前端代码
	cd frontend && pnpm format

# ==================== 快捷命令 ====================
shell-backend: ## 进入后端容器 shell
	docker compose exec backend /bin/bash

shell-frontend: ## 进入前端容器 shell
	docker compose exec frontend /bin/sh

status: ## 查看服务状态
	docker compose ps

restart: ## 重启所有服务
	docker compose restart

start: ## 快速启动（使用 start-local.sh）
	./start-local.sh