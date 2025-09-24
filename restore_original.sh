#!/bin/bash

# 恢复原始的简单版本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "恢复原始的 OpenAI 调用方式"
echo "=========================================="
echo ""

echo "服务器上可能有备份文件，让我们检查一下"
echo "请输入服务器密码："

ssh $SERVER_USER@$SERVER_IP << 'EOF'
cd /var/www/turtle_soup

echo "=== 查找备份文件 ==="
ls -la app*backup*.py 2>/dev/null || echo "没有找到备份文件"

echo ""
echo "=== 直接修复 get_ai_response 函数 ==="

# 创建一个简单的 Python 脚本来修复
cat > restore_simple.py << 'PYTHON'
# 读取当前文件
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 get_ai_response 函数并重写为最简单版本
in_function = False
new_lines = []
skip_lines = 0

for i, line in enumerate(lines):
    if skip_lines > 0:
        skip_lines -= 1
        continue

    if 'def get_ai_response():' in line:
        # 找到函数开始，写入新的简单版本
        new_lines.append('        def get_ai_response():\n')
        new_lines.append('            try:\n')
        new_lines.append('                client = OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY)\n')
        new_lines.append('                completion = client.chat.completions.create(\n')
        new_lines.append('                    model=AI_MODEL,\n')
        new_lines.append('                    messages=messages\n')
        new_lines.append('                )\n')
        new_lines.append('                return completion.choices[0].message.content\n')
        new_lines.append('            except Exception as e:\n')
        new_lines.append('                return f"[AI错误] {str(e)}"\n')

        # 跳过原函数的所有行
        in_function = True
        continue

    if in_function:
        # 检查是否到了函数结束（下一个函数或类定义）
        if line and not line.startswith(' ') and not line.startswith('\t'):
            in_function = False
            new_lines.append(line)
        elif 'future = ai_executor.submit' in line:
            # 找到函数调用的下一部分
            in_function = False
            new_lines.append(line)
    else:
        new_lines.append(line)

# 写回文件
with open('app_restored.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 已创建修复版本 app_restored.py")

# 检查修复版本
print("\n=== 检查修复后的函数 ===")
with open('app_restored.py', 'r', encoding='utf-8') as f:
    content = f.read()
    start = content.find('def get_ai_response():')
    if start != -1:
        end = content.find('future = ai_executor.submit', start)
        print(content[start:end])
PYTHON

# 执行修复
python3 restore_simple.py

# 备份当前文件并应用修复
cp app.py app_problematic_$(date +%Y%m%d_%H%M%S).py
cp app_restored.py app.py

echo "✅ 已应用修复"

# 清理缓存并重启
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
systemctl restart turtle_soup

echo "✅ 服务已重启"

# 测试
sleep 3
systemctl status turtle_soup | grep Active
EOF

echo ""
echo "=========================================="
echo "恢复完成！"
echo "=========================================="
echo ""
echo "问题原因：我之前的'修复'引入了不兼容的 proxies 参数"
echo "解决方案：恢复到最简单的 OpenAI 客户端创建方式"
echo ""
echo "请访问测试页面验证："
echo "http://$SERVER_IP:5002/test"