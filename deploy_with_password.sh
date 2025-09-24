#!/bin/bash

# 自动部署脚本（使用密码）
# 需要先安装 sshpass: brew install hudochenkov/sshpass/sshpass

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "自动部署脚本（密码方式）"
echo "=========================================="
echo ""

# 检查是否安装了 sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ 需要安装 sshpass"
    echo ""
    echo "macOS 安装方法："
    echo "brew install hudochenkov/sshpass/sshpass"
    echo ""
    echo "或者使用 SSH 密钥方式："
    echo "./setup_ssh_key.sh"
    exit 1
fi

# 提示输入密码
echo -n "请输入服务器密码: "
read -s SERVER_PASSWORD
echo ""
echo ""

# 设置密码环境变量
export SSHPASS="$SERVER_PASSWORD"

# 执行部署（使用 sshpass 自动输入密码）
echo "开始部署..."
./deploy.sh

echo ""
echo "部署完成！"