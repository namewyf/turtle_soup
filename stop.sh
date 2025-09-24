#!/bin/bash

# 停止运行在 5002 端口的服务

PORT=5002

echo "=========================================="
echo "停止 Turtle Soup 服务"
echo "=========================================="

# 查找占用端口的进程
PIDS=$(lsof -ti:$PORT)

if [ -z "$PIDS" ]; then
    echo "✅ 端口 $PORT 没有被占用，服务未运行"
else
    echo "找到以下进程占用端口 $PORT："
    lsof -i:$PORT
    echo ""
    echo "正在停止进程..."
    for PID in $PIDS; do
        echo "  停止进程 PID: $PID"
        kill -9 $PID 2>/dev/null
    done
    echo ""
    echo "✅ 服务已停止"
fi

echo "=========================================="