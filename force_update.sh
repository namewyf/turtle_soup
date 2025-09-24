#!/bin/bash

# 强制更新服务器代码的脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "强制更新服务器代码"
echo "=========================================="
echo ""

echo "步骤 1: 上传 app.py 文件"
echo "请输入服务器密码："

# 直接复制 app.py 文件到服务器
scp app.py $SERVER_USER@$SERVER_IP:/var/www/turtle_soup/app.py

if [ $? -eq 0 ]; then
    echo "✅ 文件上传成功"

    echo ""
    echo "步骤 2: 重启服务..."
    ssh $SERVER_USER@$SERVER_IP "systemctl restart turtle_soup"

    echo ""
    echo "步骤 3: 验证服务状态..."
    ssh $SERVER_USER@$SERVER_IP "systemctl status turtle_soup | grep Active"

    echo ""
    echo "步骤 4: 查看最新日志..."
    ssh $SERVER_USER@$SERVER_IP "journalctl -u turtle_soup -n 10 --no-pager"

    echo ""
    echo "=========================================="
    echo "✅ 更新完成！"
    echo "=========================================="
    echo ""
    echo "请访问测试页面验证："
    echo "http://$SERVER_IP:5002/test"
    echo ""
    echo "如果还有问题，查看详细日志："
    echo "ssh $SERVER_USER@$SERVER_IP 'journalctl -u turtle_soup -f'"
else
    echo "❌ 文件上传失败"
    echo ""
    echo "请检查："
    echo "1. 服务器连接是否正常"
    echo "2. 密码是否正确"
    echo "3. 目录权限是否正确"
fi