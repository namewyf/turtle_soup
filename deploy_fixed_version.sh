#!/bin/bash

# 部署彻底修复版本的脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "部署彻底修复的版本"
echo "=========================================="
echo ""

echo "步骤 1: 检查修复版本"
if [ ! -f "app_fixed.py" ]; then
    echo "❌ 修复版本不存在，正在创建..."
    python3 create_fixed_app.py
fi

echo "✅ 修复版本已准备就绪"
echo ""

echo "步骤 2: 备份服务器上的原始文件并部署修复版本"
echo "请输入服务器密码："

# 备份原文件并上传修复版本
scp app_fixed.py $SERVER_USER@$SERVER_IP:/var/www/turtle_soup/app_fixed.py

echo ""
echo "步骤 3: 在服务器上切换到修复版本"
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/turtle_soup

# 备份原文件
cp app.py app_original_backup.py
echo "✅ 已备份原始文件为 app_original_backup.py"

# 使用修复版本
cp app_fixed.py app.py
echo "✅ 已切换到修复版本"

# 停止服务
systemctl stop turtle_soup
echo "✅ 服务已停止"

# 清理所有缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ 已清理缓存"

# 重启服务
systemctl start turtle_soup
echo "✅ 服务已启动"

# 等待启动
sleep 3

# 检查状态
if systemctl is-active --quiet turtle_soup; then
    echo "✅ 服务运行正常"
    systemctl status turtle_soup | grep Active
else
    echo "❌ 服务启动失败"
    journalctl -u turtle_soup -n 10 --no-pager
fi
EOF

echo ""
echo "=========================================="
echo "✅ 彻底修复版本已部署"
echo "=========================================="
echo ""
echo "修复内容："
echo "1. 在模块级别清除所有代理环境变量"
echo "2. 使用自定义 HTTP 客户端明确禁用代理"
echo "3. 多重备用方案确保兼容性"
echo ""
echo "请访问测试页面验证："
echo "http://$SERVER_IP:5002/test"
echo ""
echo "如果还有问题，请运行诊断："
echo "./debug_proxy_issue.sh"