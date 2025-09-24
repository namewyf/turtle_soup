#!/bin/bash

# 开发环境启动脚本（使用 Flask 内置服务器，方便调试）

echo "======================================="
echo "启动开发服务器（调试模式）"
echo "======================================="

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
export FLASK_ENV=development
export FLASK_DEBUG=1

# 启动 Flask 开发服务器
echo "启动服务器在 http://localhost:5002"
echo "测试页面在 http://localhost:5002/test"
echo ""
echo "调试模式已开启，代码修改会自动重载"
echo "按 Ctrl+C 停止服务器"
echo "---------------------------------------"

python app.py