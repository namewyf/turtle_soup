#!/bin/bash

# 设置 SSH 免密登录脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "设置 SSH 免密登录到华为云服务器"
echo "=========================================="
echo ""
echo "注意：这个过程需要输入一次服务器密码"
echo "之后就不需要再输入密码了"
echo ""

# 检查本地是否有 SSH 密钥
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo "❌ 没有找到 SSH 公钥"
    echo "请先运行: ssh-keygen -t rsa -b 4096"
    exit 1
fi

echo "✅ 找到 SSH 公钥"
echo ""
echo "即将把以下公钥添加到服务器："
echo "----------------------------------------"
cat ~/.ssh/id_rsa.pub
echo "----------------------------------------"
echo ""
echo "请输入服务器密码（只需要这一次）："

# 将公钥复制到服务器
ssh-copy-id -i ~/.ssh/id_rsa.pub $SERVER_USER@$SERVER_IP

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ SSH 密钥配置成功！"
    echo "=========================================="
    echo ""
    echo "测试连接（应该不需要密码）..."
    ssh -o BatchMode=yes -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo '✅ 免密登录测试成功！'" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 设置完成！现在你可以："
        echo "1. 运行 ./deploy.sh 无需输入密码"
        echo "2. 直接 SSH 登录: ssh $SERVER_USER@$SERVER_IP"
    else
        echo "⚠️  密钥已添加，但测试连接失败"
        echo "请手动测试: ssh $SERVER_USER@$SERVER_IP"
    fi
else
    echo ""
    echo "❌ 设置失败"
    echo "请检查："
    echo "1. 服务器地址是否正确: $SERVER_IP"
    echo "2. 用户名是否正确: $SERVER_USER"
    echo "3. 密码是否正确"
fi