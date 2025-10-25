#!/bin/bash
# 启动LiveRecorder（命令行模式）

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${BLUE}→${NC} 启动LiveRecorder（命令行模式）"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} 虚拟环境已激活"
else
    echo -e "${YELLOW}⚠${NC}  虚拟环境不存在，请先运行 scripts/install.sh"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo -e "${YELLOW}⚠${NC}  配置文件不存在，从示例创建..."
    cp config.sample.json config.json
fi

# 启动程序
python app.py --mode cli

echo -e "${GREEN}✓${NC} 程序已退出"
