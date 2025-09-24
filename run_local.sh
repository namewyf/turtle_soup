#!/bin/bash

# 本地生产模式启动脚本（与云服务器配置完全一致）

echo "=========================================="
echo "启动本地生产模式服务器"
echo "配置与云服务器完全一致"
echo "=========================================="

# 检查并关闭占用 5002 端口的进程
PORT=5002
PIDS=$(lsof -ti:$PORT)
if [ ! -z "$PIDS" ]; then
    echo "发现端口 $PORT 被占用，正在关闭相关进程..."
    for PID in $PIDS; do
        echo "  关闭进程 PID: $PID"
        kill -9 $PID 2>/dev/null
    done
    echo "已清理端口 $PORT"
    sleep 1
fi

# 添加用户 Python bin 目录到 PATH（用于 macOS）
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# 设置环境变量（与云服务器一致）
export AI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export AI_API_KEY=7a954c5e-10f2-456f-9439-611c6b5d7be8
export AI_MODEL=doubao-lite-32k-character-250228
export PORT=5002

echo "启动服务器在 http://localhost:5002"
echo "测试页面在 http://localhost:5002/test"
echo ""
echo "警告：此模式与云服务器配置完全一致（单进程，无自动重载）"
echo "如需开发模式，请使用 ./run_dev.sh"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "------------------------------------------"

# 使用与云服务器完全一致的 Gunicorn 配置
# 重要：使用 --workers 1 避免多进程内存共享问题
gunicorn \
    --workers 1 \
    --bind 0.0.0.0:5002 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:app