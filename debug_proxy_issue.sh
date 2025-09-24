#!/bin/bash

# 深度诊断代理问题的脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "深度诊断代理问题"
echo "=========================================="
echo ""

echo "步骤 1: 检查服务器环境变量"
echo "请输入服务器密码："

ssh $SERVER_USER@$SERVER_IP << 'EOF'
echo "=== 检查所有代理相关环境变量 ==="
env | grep -i proxy || echo "没有找到代理环境变量"

echo ""
echo "=== 检查 OpenAI 库版本 ==="
cd /var/www/turtle_soup
source venv/bin/activate
pip show openai

echo ""
echo "=== 查看实时错误日志 ==="
echo "最近的错误日志："
journalctl -u turtle_soup -n 20 --no-pager | grep -i error || echo "没有找到错误"

echo ""
echo "=== 测试 Python 环境中的 OpenAI 导入 ==="
python3 -c "
import os
print('Python 环境变量检查:')
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    value = os.environ.get(key)
    if value:
        print(f'{key} = {value}')
    else:
        print(f'{key} = None')

print('\n测试 OpenAI 导入:')
try:
    from openai import OpenAI
    print('✅ OpenAI 库导入成功')

    # 尝试创建客户端（不调用 API）
    client = OpenAI(base_url='https://api.openai.com/v1', api_key='test')
    print('✅ OpenAI 客户端创建成功')
except Exception as e:
    print(f'❌ OpenAI 错误: {e}')
"
EOF

echo ""
echo "=========================================="
echo "基于上述信息，我们需要调整修复策略"