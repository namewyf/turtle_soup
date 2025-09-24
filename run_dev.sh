#!/bin/bash

# 开发环境启动脚本（带自动重载的 Gunicorn）

echo "======================================="
echo "启动开发服务器（开发模式）"
echo "======================================="

# 添加用户 Python bin 目录到 PATH（用于 macOS）
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# 设置环境变量
export AI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export AI_API_KEY=7a954c5e-10f2-456f-9439-611c6b5d7be8
export AI_MODEL=doubao-lite-32k-character-250228
export PORT=5002

echo "启动服务器在 http://localhost:5002"
echo "测试页面在 http://localhost:5002/test"
echo ""
echo "开发模式特性："
echo "✅ 自动重载（代码修改后自动重启）"
echo "✅ 详细错误信息"
echo "⚠️  注意：reload 模式仅运行单进程，不会暴露多进程问题"
echo ""
echo "如需测试生产环境配置，请使用 ./run_local.sh"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "---------------------------------------"

# 使用 Gunicorn 的开发模式（带自动重载）
gunicorn \
    --reload \
    --bind 0.0.0.0:5002 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    app:app