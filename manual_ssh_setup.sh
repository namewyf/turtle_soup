#!/bin/bash

# 手动设置 SSH 密钥的脚本

SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "=========================================="
echo "手动设置 SSH 免密登录"
echo "=========================================="
echo ""
echo "步骤 1: 复制下面的公钥内容"
echo "----------------------------------------"
cat ~/.ssh/id_rsa.pub
echo "----------------------------------------"
echo ""
echo "步骤 2: 手动登录服务器并添加密钥"
echo ""
echo "请在新的终端窗口执行以下命令："
echo ""
echo "# 1. 登录服务器"
echo "ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "# 2. 创建 .ssh 目录（如果不存在）"
echo "mkdir -p ~/.ssh"
echo "chmod 700 ~/.ssh"
echo ""
echo "# 3. 添加公钥到 authorized_keys"
echo "echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys"
echo ""
echo "# 4. 设置正确的权限"
echo "chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "# 5. 退出服务器"
echo "exit"
echo ""
echo "=========================================="
echo ""
echo "完成上述步骤后，按回车键测试连接..."
read -p ""

echo ""
echo "测试免密登录..."
ssh -o BatchMode=yes -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo '✅ 免密登录设置成功！'" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 恭喜！SSH 免密登录配置成功！"
    echo ""
    echo "现在你可以："
    echo "1. 运行 ./deploy.sh 无需输入密码"
    echo "2. 直接 SSH 登录: ssh $SERVER_USER@$SERVER_IP"
else
    echo ""
    echo "⚠️  测试失败，请检查："
    echo "1. 是否正确执行了上述步骤"
    echo "2. 公钥是否正确添加"
    echo "3. 权限设置是否正确"
fi