#!/bin/bash

# 华为云服务器部署脚本
SERVER_IP="1.95.37.33"
SERVER_USER="root"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}开始部署到华为云服务器${NC}"
echo -e "${BLUE}================================${NC}"

# 添加服务器到已知主机（避免重复询问）
echo -e "${YELLOW}[0/8] 添加服务器指纹...${NC}"
ssh-keyscan -H $SERVER_IP >> ~/.ssh/known_hosts 2>/dev/null

# 1. 创建服务器上的项目目录
echo -e "${YELLOW}[1/8] 创建项目目录...${NC}"
ssh $SERVER_USER@$SERVER_IP "mkdir -p /var/www/turtle_soup"

# 2. 打包并上传项目文件（排除不需要的文件）
echo -e "${YELLOW}[2/8] 上传项目文件...${NC}"
rsync -avz --exclude='.venv/' \
           --exclude='venv/' \
           --exclude='__pycache__/' \
           --exclude='.git/' \
           --exclude='.env' \
           --exclude='*.pyc' \
           --exclude='.DS_Store' \
           --exclude='server.log' \
           --delete \
           . $SERVER_USER@$SERVER_IP:/var/www/turtle_soup/

# 3. 在服务器上安装必要的软件
echo -e "${YELLOW}[3/8] 安装Python和依赖...${NC}"
ssh $SERVER_USER@$SERVER_IP << 'EOF'
apt update
apt install -y python3 python3-pip python3-venv
cd /var/www/turtle_soup

# 如果虚拟环境不存在则创建
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# 4. 创建环境变量文件
echo -e "${YELLOW}[4/8] 配置环境变量...${NC}"
ssh $SERVER_USER@$SERVER_IP << 'EOF'
cat > /var/www/turtle_soup/.env << 'EOE'
AI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
AI_API_KEY=7a954c5e-10f2-456f-9439-611c6b5d7be8
AI_MODEL=doubao-lite-32k-character-250228
PORT=5002
EOE
EOF

# 5. 创建系统服务文件
echo -e "${YELLOW}[5/8] 创建系统服务...${NC}"
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
Environment="PYTHONPATH=/var/www/turtle_soup"
ExecStart=/var/www/turtle_soup/venv/bin/gunicorn --workers 1 --bind 0.0.0.0:5002 --timeout 120 --access-logfile - --error-logfile - app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOS

# 重新加载systemd配置
systemctl daemon-reload
systemctl enable turtle_soup
EOF

# 6. 停止旧服务（如果存在）
echo -e "${YELLOW}[6/8] 停止旧服务...${NC}"
ssh $SERVER_USER@$SERVER_IP "systemctl stop turtle_soup 2>/dev/null || true"

# 7. 启动新服务
echo -e "${YELLOW}[7/8] 启动服务...${NC}"
ssh $SERVER_USER@$SERVER_IP "systemctl start turtle_soup"

# 等待服务启动
sleep 3

# 8. 检查服务状态
echo -e "${YELLOW}[8/8] 检查服务状态...${NC}"
if ssh $SERVER_USER@$SERVER_IP "systemctl is-active --quiet turtle_soup"; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    ssh $SERVER_USER@$SERVER_IP "systemctl status turtle_soup --no-pager"

    # 测试API是否可访问
    echo -e "\n${YELLOW}测试API健康状态...${NC}"
    if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:5002/health | grep -q "200"; then
        echo -e "${GREEN}✅ API服务正常响应${NC}"
    else
        echo -e "${YELLOW}⚠️  API暂时无法访问，可能需要等待几秒钟${NC}"
    fi

    # 检查题目加载情况
    echo -e "\n${YELLOW}检查题目加载情况...${NC}"
    ssh $SERVER_USER@$SERVER_IP "cd /var/www/turtle_soup && source venv/bin/activate && python3 -c 'from app import chemistry_problems; print(f\"已加载 {len(chemistry_problems)} 个化学题目\")'"

else
    echo -e "${RED}❌ 服务启动失败！${NC}"
    echo -e "${YELLOW}查看错误日志：${NC}"
    ssh $SERVER_USER@$SERVER_IP "journalctl -u turtle_soup -n 50 --no-pager"
    exit 1
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${BLUE}访问地址: ${GREEN}http://$SERVER_IP:5002${NC}"
echo -e "${BLUE}测试地址: ${GREEN}http://$SERVER_IP:5002/test${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${YELLOW}常用命令：${NC}"
echo -e "查看日志: ssh $SERVER_USER@$SERVER_IP 'journalctl -u turtle_soup -f'"
echo -e "重启服务: ssh $SERVER_USER@$SERVER_IP 'systemctl restart turtle_soup'"
echo -e "停止服务: ssh $SERVER_USER@$SERVER_IP 'systemctl stop turtle_soup'"
echo -e "查看状态: ssh $SERVER_USER@$SERVER_IP 'systemctl status turtle_soup'"
echo ""
echo -e "${YELLOW}故障排查：${NC}"
echo -e "查看错误: ssh $SERVER_USER@$SERVER_IP 'journalctl -u turtle_soup -n 100 | grep ERROR'"
echo -e "实时日志: ssh $SERVER_USER@$SERVER_IP 'tail -f /var/www/turtle_soup/server.log'"