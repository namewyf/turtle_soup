#!/bin/bash

# 验证部署是否成功的脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "验证部署状态"
echo "=========================================="
echo ""

echo "1. 检查服务器上的代码是否包含修复..."
echo "请输入服务器密码："

# 检查服务器上的文件是否包含修复代码
ssh $SERVER_USER@$SERVER_IP "grep -c '临时清除代理环境变量' /var/www/turtle_soup/app.py" 2>/dev/null

if [ $? -eq 0 ]; then
    RESULT=$(ssh $SERVER_USER@$SERVER_IP "grep -c '临时清除代理环境变量' /var/www/turtle_soup/app.py" 2>/dev/null)
    if [ "$RESULT" -gt 0 ]; then
        echo "✅ 服务器上的代码已包含修复"

        echo ""
        echo "2. 重启服务以应用更改..."
        ssh $SERVER_USER@$SERVER_IP "systemctl restart turtle_soup"

        echo ""
        echo "3. 检查服务状态..."
        ssh $SERVER_USER@$SERVER_IP "systemctl status turtle_soup --no-pager | head -20"

        echo ""
        echo "=========================================="
        echo "✅ 服务已重启，请再次测试"
        echo "访问: http://$SERVER_IP:5002/test"
        echo "=========================================="
    else
        echo "❌ 服务器上的代码未包含修复"
        echo ""
        echo "需要重新部署："
        echo "1. 确保本地 app.py 包含修复"
        echo "2. 运行 ./deploy.sh"
    fi
else
    echo "❌ 无法连接到服务器或检查失败"
fi