#!/bin/bash
# LiveRecorder 安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  LiveRecorder 安装脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo

# 检测Python版本
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}✓${NC} 找到 Python: $PYTHON_VERSION"
    else
        echo -e "${RED}✗${NC} 未找到 Python3，请先安装 Python 3.8+"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    if [ -d "venv" ]; then
        echo -e "${YELLOW}!${NC} 虚拟环境已存在"
        read -p "是否重新创建？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}→${NC} 删除旧的虚拟环境..."
            rm -rf venv
        else
            echo -e "${GREEN}→${NC} 使用现有虚拟环境"
            return
        fi
    fi
    
    echo -e "${BLUE}→${NC} 创建虚拟环境..."
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓${NC} 虚拟环境创建成功"
}

# 激活虚拟环境
activate_venv() {
    echo -e "${BLUE}→${NC} 激活虚拟环境..."
    source venv/bin/activate
    echo -e "${GREEN}✓${NC} 虚拟环境已激活"
}

# 升级pip
upgrade_pip() {
    echo -e "${BLUE}→${NC} 升级 pip..."
    pip install --upgrade pip -q
    echo -e "${GREEN}✓${NC} pip 已升级"
}

# 安装基础依赖
install_base_deps() {
    echo -e "${BLUE}→${NC} 安装基础依赖..."
    if [ -f "pyproject.toml" ]; then
        pip install -e . -q
        echo -e "${GREEN}✓${NC} 基础依赖安装完成"
    else
        echo -e "${RED}✗${NC} 未找到 pyproject.toml"
        exit 1
    fi
}

# 安装Web依赖
install_web_deps() {
    echo
    read -p "是否安装Web界面依赖？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}→${NC} 安装Web界面依赖..."
        pip install -e ".[web]" -q
        echo -e "${GREEN}✓${NC} Web依赖安装完成"
    fi
}

# 检查配置文件
check_config() {
    echo
    echo -e "${BLUE}→${NC} 检查配置文件..."
    if [ ! -f "config.json" ]; then
        if [ -f "config.sample.json" ]; then
            echo -e "${YELLOW}!${NC} 未找到 config.json，从示例创建..."
            cp config.sample.json config.json
            echo -e "${GREEN}✓${NC} 已创建 config.json，请编辑后使用"
        else
            echo -e "${RED}✗${NC} 未找到配置文件"
        fi
    else
        echo -e "${GREEN}✓${NC} 配置文件已存在"
    fi
}

# 创建必要的目录
create_dirs() {
    echo -e "${BLUE}→${NC} 创建必要的目录..."
    mkdir -p output logs
    echo -e "${GREEN}✓${NC} 目录创建完成"
}

# 主函数
main() {
    check_python
    create_venv
    activate_venv
    upgrade_pip
    install_base_deps
    install_web_deps
    check_config
    create_dirs
    
    echo
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  安装完成！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo
    echo -e "使用方法："
    echo -e "  ${BLUE}./scripts/start.sh${NC}      - 启动命令行版本"
    echo -e "  ${BLUE}./scripts/start_web.sh${NC}  - 启动Web界面版本"
    echo
}

main
