#!/bin/bash

# 华为云服务器部署脚本
SERVER_IP="1.95.37.33"
SERVER_USER="root"

echo "================================"
echo "开始部署到华为云服务器"
echo "================================"

# 添加服务器到已知主机（避免重复询问）
echo "[0/7] 添加服务器指纹..."
ssh-keyscan -H $SERVER_IP >> ~/.ssh/known_hosts 2>/dev/null

# 1. 创建服务器上的项目目录
echo "[1/7] 创建项目目录..."
ssh $SERVER_USER@$SERVER_IP "mkdir -p /var/www/turtle_soup"

# 2. 打包并上传项目文件（排除不需要的文件）
echo "[2/7] 上传项目文件..."
rsync -avz --exclude='.venv/' \
           --exclude='__pycache__/' \
           --exclude='.git/' \
           --exclude='.env' \
           --exclude='*.pyc' \
           --exclude='.DS_Store' \
           . $SERVER_USER@$SERVER_IP:/var/www/turtle_soup/

# 3. 在服务器上安装必要的软件
echo "[3/7] 安装Python和依赖..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
apt update
apt install -y python3 python3-pip python3-venv
cd /var/www/turtle_soup
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# 4. 创建环境变量文件
echo "[4/7] 配置环境变量..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cat > /var/www/turtle_soup/.env << 'EOE'
AI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
AI_API_KEY=7a954c5e-10f2-456f-9439-611c6b5d7be8
AI_MODEL=doubao-lite-32k-character-250228
PORT=5002
EOE
EOF

# 5. 创建系统服务文件
echo "[5/7] 创建系统服务..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cat > /etc/systemd/system/turtle_soup.service << 'EOS'
[Unit]
Description=Turtle Soup Flask Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/turtle_soup
Environment="PATH=/var/www/turtle_soup/venv/bin"
ExecStart=/var/www/turtle_soup/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5002 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOS

# 重新加载systemd配置
systemctl daemon-reload
systemctl enable turtle_soup
EOF

# 6. 启动服务
echo "[6/7] 启动服务..."
ssh $SERVER_USER@$SERVER_IP "systemctl restart turtle_soup"

# 7. 检查服务状态
echo "[7/7] 检查服务状态..."
ssh $SERVER_USER@$SERVER_IP "systemctl status turtle_soup --no-pager"

echo ""
echo "================================"
echo "部署完成！"
echo "访问地址: http://$SERVER_IP:5002"
echo "================================"
echo ""
echo "常用命令："
echo "查看日志: ssh $SERVER_USER@$SERVER_IP 'journalctl -u turtle_soup -f'"
echo "重启服务: ssh $SERVER_USER@$SERVER_IP 'systemctl restart turtle_soup'"
echo "停止服务: ssh $SERVER_USER@$SERVER_IP 'systemctl stop turtle_soup'"