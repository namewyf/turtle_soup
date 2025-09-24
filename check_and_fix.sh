#!/bin/bash

# 检查并修复服务器代码的脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "检查并修复服务器代码"
echo "=========================================="
echo ""

echo "步骤 1: 检查服务器上的代码版本"
echo "请输入服务器密码："
echo ""

# 检查服务器上是否有修复代码
echo "检查服务器上的 app.py 是否包含修复..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
echo "=== 检查代理修复代码 ==="
if grep -q "临时清除代理环境变量" /var/www/turtle_soup/app.py; then
    echo "✅ 服务器代码包含修复"
    echo ""
    echo "=== 显示相关代码段 ==="
    grep -A5 "临时清除代理环境变量" /var/www/turtle_soup/app.py
else
    echo "❌ 服务器代码不包含修复"
    echo ""
    echo "=== 显示当前 get_ai_response 函数 ==="
    grep -A10 "def get_ai_response" /var/www/turtle_soup/app.py
fi
echo ""
echo "=== 检查文件大小 ==="
ls -lh /var/www/turtle_soup/app.py | awk '{print "文件大小:", $5}'
echo ""
echo "=== 检查文件修改时间 ==="
ls -l /var/www/turtle_soup/app.py | awk '{print "修改时间:", $6, $7, $8}'
EOF

echo ""
echo "=========================================="
echo ""

read -p "是否需要强制更新代码？(y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "步骤 2: 强制更新服务器代码"
    echo ""

    # 直接复制文件
    echo "上传本地 app.py 文件..."
    scp app.py $SERVER_USER@$SERVER_IP:/var/www/turtle_soup/app.py

    if [ $? -eq 0 ]; then
        echo "✅ 文件上传成功"

        # 清理缓存并重启服务
        echo ""
        echo "步骤 3: 清理缓存并重启服务"
        ssh $SERVER_USER@$SERVER_IP << 'EOF'
# 停止服务
systemctl stop turtle_soup

# 清理所有 Python 缓存
find /var/www/turtle_soup -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /var/www/turtle_soup -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ 已清理 Python 缓存"

# 重启服务
systemctl start turtle_soup
echo "✅ 服务已重启"

# 等待服务启动
sleep 2

# 检查服务状态
systemctl status turtle_soup | grep Active
EOF

        echo ""
        echo "步骤 4: 验证修复"
        ssh $SERVER_USER@$SERVER_IP << 'EOF'
echo "=== 再次检查修复代码 ==="
if grep -q "临时清除代理环境变量" /var/www/turtle_soup/app.py; then
    echo "✅ 修复已成功部署"
else
    echo "❌ 修复部署失败"
fi
EOF

        echo ""
        echo "=========================================="
        echo "✅ 更新完成！"
        echo "=========================================="
        echo ""
        echo "请访问测试页面验证："
        echo "http://$SERVER_IP:5002/test"
    else
        echo "❌ 文件上传失败"
    fi
else
    echo "已取消更新"
fi