#!/bin/bash
# 启动LiveRecorder（Web模式）

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${BLUE}→${NC} 启动LiveRecorder（Web模式）"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} 虚拟环境已激活"
else
    echo -e "${YELLOW}⚠${NC}  虚拟环境不存在，请先运行 scripts/install.sh"
    exit 1
fi

# 启动程序（后台运行）
python app.py --mode web > /tmp/liverecorder.log 2>&1 &
PID=$!

echo -e "${GREEN}✓${NC} Web服务已启动 (PID: $PID)"
echo -e "${BLUE}→${NC} 访问: http://localhost:8888"
echo ""
echo -e "${YELLOW}查看日志:${NC} tail -f /tmp/liverecorder.log"
echo -e "${YELLOW}停止服务:${NC} scripts/stop.sh"
