#!/bin/bash
# 停止LiveRecorder

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}→${NC} 正在停止LiveRecorder..."

# 查找并停止进程
PIDS=$(ps aux | grep -E '(app\.py|main\.py|main_web\.py)' | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo -e "${GREEN}✓${NC} 没有运行中的LiveRecorder进程"
else
    echo "$PIDS" | while read PID; do
        kill $PID 2>/dev/null
        echo -e "${GREEN}✓${NC} 已停止进程: $PID"
    done
    sleep 1
fi

echo -e "${GREEN}✓${NC} 完成"
