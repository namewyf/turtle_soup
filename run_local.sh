#!/bin/bash

# 本地开发环境启动脚本（使用 Gunicorn，模拟生产环境）

echo "=========================================="
echo "启动本地 Gunicorn 服务器（生产环境模式）"
echo "=========================================="

# 添加用户 Python bin 目录到 PATH
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# 激活虚拟环境（如果有）
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 设置环境变量
export AI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export AI_API_KEY=7a954c5e-10f2-456f-9439-611c6b5d7be8
export AI_MODEL=doubao-lite-32k-character-250228
export PORT=5002

# 启动 Gunicorn
echo "启动服务器在 http://localhost:5002"
echo "测试页面在 http://localhost:5002/test"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "------------------------------------------"

# 设置开发环境的特殊配置
export GUNICORN_RELOAD=true
export GUNICORN_WORKERS=2

# 使用 Gunicorn 启动（与生产环境相同的配置）
gunicorn --config gunicorn_config.py app:app