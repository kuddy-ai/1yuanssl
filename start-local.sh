#!/bin/bash

# 1yuanssl 本地启动脚本（使用 uv + pnpm）

set -e

echo "========================================="
echo "  1yuanssl - 本地开发环境启动"
echo "========================================="
echo ""

# 检查是否安装了必要工具
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ 错误: 未安装 $1"
        if [ "$1" = "uv" ]; then
            echo "   安装 uv: pip install uv 或 curl -LsSf https://astral.sh/uv/install.sh | sh"
        elif [ "$1" = "pnpm" ]; then
            echo "   安装 pnpm: npm install -g pnpm"
        fi
        return 1
    fi
    return 0
}

# 检查 Python
echo "检查 Python 环境..."
if check_command python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python 已安装: $PYTHON_VERSION"
else
    exit 1
fi

# 检查 uv
echo "检查 uv 环境..."
if check_command uv; then
    UV_VERSION=$(uv --version)
    echo "✅ uv 已安装: $UV_VERSION"
else
    echo ""
    echo "正在安装 uv（使用清华源）..."
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple uv || curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv 已安装"
fi

# 检查 pnpm
echo "检查 pnpm 环境..."
if check_command pnpm; then
    PNPM_VERSION=$(pnpm --version)
    echo "✅ pnpm 已安装: $PNPM_VERSION"
else
    echo ""
    echo "正在安装 pnpm..."
    npm install -g pnpm
    echo "✅ pnpm 已安装"
fi

echo ""
echo "========================================="
echo "  启动后端服务（使用 uv + 清华源）"
echo "========================================="
echo ""

cd backend

# 设置清华源环境变量
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
echo "✅ 已配置清华源: $UV_INDEX_URL"

# 使用 uv 创建虚拟环境并安装依赖
echo "使用 uv 创建虚拟环境并安装依赖..."
if [ ! -d ".venv" ]; then
    uv venv
    echo "✅ 虚拟环境已创建"
fi

echo "安装后端依赖（使用清华源，比 pip 快 10-100 倍）..."
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -e ".[dev]"
echo "✅ 后端依赖已安装"

# 创建数据目录
mkdir -p data

# 启动后端（后台运行，端口 7000）
echo "启动后端服务（端口 7000）..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 7000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
echo "等待后端启动..."
sleep 5

# 检查后端是否成功启动
if curl -s http://localhost:7000/api/v1/health > /dev/null; then
    echo "✅ 后端健康检查成功"
else
    echo "⚠️  后端可能启动失败，请检查 backend/backend.log"
    echo "日志内容："
    tail -20 backend.log
fi

cd ..

echo ""
echo "========================================="
echo "  启动前端服务（使用 pnpm）"
echo "========================================="
echo ""

cd frontend

# 安装前端依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖（使用 pnpm）..."
    pnpm install
    echo "✅ 前端依赖已安装"
fi

# 启动前端（后台运行，端口 7001）
echo "启动前端服务（端口 7001）..."
pnpm dev -- --host 0.0.0.0 --port 7001 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

cd ..

echo ""
echo "========================================="
echo "  服务已启动！"
echo "========================================="
echo ""
echo "访问地址："
echo "  📱 前端: http://localhost:7001"
echo "  🔌 后端 API: http://localhost:7000/api/v1"
echo "  📖 API 文档: http://localhost:7000/docs"
echo "  📖 ReDoc 文档: http://localhost:7000/redoc"
echo ""
echo "日志文件："
echo "  📄 backend/backend.log"
echo "  📄 frontend/frontend.log"
echo ""
echo "停止服务："
echo "  kill $BACKEND_PID  # 停止后端"
echo "  kill $FRONTEND_PID  # 停止前端"
echo "  或使用: pkill -f 'uvicorn app.main:app' && pkill -f 'vite'"
echo ""
echo "========================================="