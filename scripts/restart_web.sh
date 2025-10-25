#!/bin/bash
# 重启LiveRecorder Web服务

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")/.."

echo -e "${YELLOW}→${NC} 停止现有服务..."
scripts/stop.sh

sleep 2

echo -e "${BLUE}→${NC} 启动Web服务..."
scripts/start_web.sh
