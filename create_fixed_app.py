#!/usr/bin/env python3

# 创建一个彻底修复的 app.py 版本

import re

# 读取当前的 app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在文件开头添加代理环境变量清理
proxy_fix_header = '''import os
# 彻底清除代理环境变量，防止 OpenAI 库冲突
for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]

'''

# 在导入部分之后添加
import_pattern = r'(from openai import OpenAI\n)'
content = re.sub(import_pattern, r'\1' + proxy_fix_header, content)

# 创建更健壮的 OpenAI 客户端创建函数
robust_client_code = '''
def create_openai_client():
    """创建健壮的 OpenAI 客户端，避免代理相关问题"""
    try:
        # 确保没有代理环境变量
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
        saved_vars = {}

        # 临时清除所有代理变量
        for var in proxy_vars:
            if var in os.environ:
                saved_vars[var] = os.environ[var]
                del os.environ[var]

        try:
            import httpx
            # 创建一个明确禁用代理的 HTTP 客户端
            http_client = httpx.Client(
                proxies=None,
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=1, max_connections=1)
            )

            # 使用自定义 HTTP 客户端创建 OpenAI 客户端
            client = OpenAI(
                base_url=AI_BASE_URL,
                api_key=AI_API_KEY,
                http_client=http_client
            )

            return client
        finally:
            # 恢复环境变量
            for var, value in saved_vars.items():
                os.environ[var] = value

    except Exception as e:
        print(f"OpenAI 客户端创建失败: {e}")
        # 如果上面的方法失败，尝试更简单的方法
        try:
            return OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY)
        except Exception as e2:
            print(f"简单方法也失败: {e2}")
            raise e2

'''

# 添加新函数到适当位置
function_insertion_point = content.find('# ==================== 初始化 ====================')
if function_insertion_point != -1:
    content = content[:function_insertion_point] + robust_client_code + '\n' + content[function_insertion_point:]

# 替换原来的客户端创建代码
old_client_creation = r'client = OpenAI\(base_url=AI_BASE_URL, api_key=AI_API_KEY\)'
new_client_creation = 'client = create_openai_client()'
content = re.sub(old_client_creation, new_client_creation, content)

# 写入新的文件
with open('app_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 创建了彻底修复的 app_fixed.py")
print("这个版本:")
print("1. 在模块级别清除所有代理环境变量")
print("2. 使用自定义 HTTP 客户端明确禁用代理")
print("3. 有多重备用方案")