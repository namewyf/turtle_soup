#!/bin/bash

# 快速修复脚本 - 创建必要的数据文件夹
SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "修复数据文件夹问题..."

# 在服务器上创建必要的目录结构
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/turtle_soup

# 创建数据目录
mkdir -p data

# 创建空的数据文件（应用会使用内置数据）
touch data/chemistry_problems.json
touch data/categories.json

# 重启服务
systemctl restart turtle_soup
sleep 2

# 检查服务状态
systemctl status turtle_soup --no-pager | head -n 10
EOF

echo "修复完成！现在访问 http://$SERVER_IP:5002/test 应该可以正常使用了"