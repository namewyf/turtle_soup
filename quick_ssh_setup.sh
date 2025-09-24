#!/bin/bash

# 快速设置 SSH 密钥（一键方案）

SERVER_IP="1.95.37.33"
SERVER_USER="root"
PUBLIC_KEY=$(cat ~/.ssh/id_rsa.pub)

echo "=========================================="
echo "一键设置 SSH 免密登录"
echo "=========================================="
echo ""
echo "这个方法只需要输入一次密码"
echo ""
echo "准备添加的公钥："
echo "----------------------------------------"
echo "$PUBLIC_KEY"
echo "----------------------------------------"
echo ""
echo "请输入服务器密码："

# 通过 SSH 直接执行命令添加密钥
ssh $SERVER_USER@$SERVER_IP "
    mkdir -p ~/.ssh && \
    chmod 700 ~/.ssh && \
    echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys && \
    chmod 600 ~/.ssh/authorized_keys && \
    echo '✅ 密钥添加成功'
"

if [ $? -eq 0 ]; then
    echo ""
    echo "测试免密登录..."
    sleep 1

    # 测试免密登录
    ssh -o BatchMode=yes -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo '✅ 免密登录测试成功！'" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "🎉 设置成功！"
        echo "=========================================="
        echo ""
        echo "现在你可以："
        echo "✅ ./deploy.sh - 无需密码自动部署"
        echo "✅ ssh $SERVER_USER@$SERVER_IP - 直接登录服务器"
    else
        echo ""
        echo "⚠️  密钥已添加，但免密登录测试失败"
        echo "可能需要等待几秒钟再试"
    fi
else
    echo ""
    echo "❌ 添加密钥失败"
    echo ""
    echo "可能的原因："
    echo "1. 密码错误"
    echo "2. 网络连接问题"
    echo "3. 服务器 SSH 配置限制"
    echo ""
    echo "你可以尝试手动方式："
    echo "./manual_ssh_setup.sh"
fi