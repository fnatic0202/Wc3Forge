#!/usr/bin/env bash
#============================================================================
# Wc3Forge - WC3 地图开发自动化脚本集
#
# 用法:
#   ./run.sh build          # 构建示例地图
#   ./run.sh test           # 测试地图
#   ./run.sh install        # 安装地图到 WC3
#   ./run.sh all            # 完整流程: 构建 + 测试 + 安装
#   ./run.sh launch         # 启动 WC3
#   ./run.sh clean          # 清理临时文件
#============================================================================

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
MAP_SOURCE="sample_map/src"
MAP_OUTPUT="sample_map/hello_rpg.w3x"
TEST_MAP="$PROJECT_DIR/$MAP_OUTPUT"

# WC3 目录 (根据实际情况修改)
WC3_PATH="/mnt/e/Warcraft III Frozen Throne/Warcraft III Frozen Throne"
MAPS_FOLDER="$WC3_PATH/Maps/Wc3Forge"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

#============================================================================
# 构建地图
#============================================================================
cmd_build() {
    log_info "构建示例地图..."

    cd "$PROJECT_DIR"
    python3 scripts/convert/build_map.py \
        --src "$MAP_SOURCE" \
        --output "$MAP_OUTPUT"

    if [ -f "$TEST_MAP" ]; then
        log_info "地图构建成功: $TEST_MAP"
    else
        log_error "地图构建失败"
        exit 1
    fi
}

#============================================================================
# 验证地图
#============================================================================
cmd_verify() {
    log_info "验证地图文件..."

    if [ ! -f "$TEST_MAP" ]; then
        log_error "地图文件不存在: $TEST_MAP"
        log_info "请先运行: ./run.sh build"
        exit 1
    fi

    cd "$PROJECT_DIR"
    python3 scripts/test/test_map.py \
        --wc3-path "$WC3_PATH" \
        --map "$TEST_MAP" \
        --no-launch
}

#============================================================================
# 安装地图
#============================================================================
cmd_install() {
    log_info "安装地图到 WC3..."

    if [ ! -f "$TEST_MAP" ]; then
        log_error "地图文件不存在: $TEST_MAP"
        log_info "请先运行: ./run.sh build"
        exit 1
    fi

    mkdir -p "$MAPS_FOLDER"
    cp "$TEST_MAP" "$MAPS_FOLDER/"

    log_info "地图已安装: $MAPS_FOLDER/hello_rpg.w3x"
}

#============================================================================
# 测试地图
#============================================================================
cmd_test() {
    cmd_verify

    log_info "安装地图..."
    cmd_install

    log_info "测试完成!"
}

#============================================================================
# 启动 WC3
#============================================================================
cmd_launch() {
    log_info "启动 Warcraft 3..."

    if [ ! -f "$WC3_PATH/War3.exe" ]; then
        log_error "找不到 WC3 可执行文件: $WC3_PATH/War3.exe"
        exit 1
    fi

    log_info "启动 WC3..."

    # 使用 PowerShell 启动
    powershell.exe -Command "Start-Process 'E:\Warcraft III Frozen Throne\Warcraft III Frozen Throne\War3.exe' -WorkingDirectory 'E:\Warcraft III Frozen Throne\Warcraft III Frozen Throne'"

    log_info "WC3 已启动，请在游戏中选择 Wc3Forge/hello_rpg.w3x 测试"
}

#============================================================================
# 完整流程
#============================================================================
cmd_all() {
    log_info "执行完整流程: 构建 + 测试 + 安装"
    echo "========================================"

    cmd_build
    echo "----------------------------------------"
    cmd_test

    echo "========================================"
    log_info "完成!"
    echo ""
    echo "请在 WC3 中:"
    echo "  1. 创建自定义游戏"
    echo "  2. 选择 Wc3Forge/hello_rpg.w3x"
    echo "  3. 开始游戏测试"
}

#============================================================================
# 清理
#============================================================================
cmd_clean() {
    log_info "清理临时文件..."

    find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf "$PROJECT_DIR/extracted"/* 2>/dev/null || true
    rm -rf "$PROJECT_DIR/temp"/* 2>/dev/null || true

    log_info "清理完成"
}

#============================================================================
# 卸载地图
#============================================================================
cmd_uninstall() {
    log_info "从 WC3 卸载地图..."

    if [ -f "$MAPS_FOLDER/hello_rpg.w3x" ]; then
        rm "$MAPS_FOLDER/hello_rpg.w3x"
        log_info "地图已卸载"
    else
        log_warn "地图未安装"
    fi
}

#============================================================================
# 帮助
#============================================================================
cmd_help() {
    echo "Wc3Forge - WC3 地图开发自动化脚本"
    echo ""
    echo "用法: $0 <命令>"
    echo ""
    echo "命令:"
    echo "  build       构建示例地图"
    echo "  verify      验证地图结构"
    echo "  install     安装地图到 WC3"
    echo "  test        测试地图 (验证 + 安装)"
    echo "  launch      启动 WC3"
    echo "  all         完整流程 (构建 + 测试 + 安装)"
    echo "  uninstall   卸载地图"
    echo "  clean       清理临时文件"
    echo "  help        显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 build            # 构建地图"
    echo "  $0 test             # 测试地图"
    echo "  $0 all              # 完整流程"
    echo ""
    echo "配置:"
    echo "  WC3_PATH: $WC3_PATH"
    echo "  MAPS_FOLDER: $MAPS_FOLDER"
}

#============================================================================
# 主入口
#============================================================================
case "${1:-help}" in
    build)
        cmd_build
        ;;
    verify)
        cmd_verify
        ;;
    install)
        cmd_install
        ;;
    test)
        cmd_test
        ;;
    launch)
        cmd_launch
        ;;
    all)
        cmd_all
        ;;
    uninstall)
        cmd_uninstall
        ;;
    clean)
        cmd_clean
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        log_error "未知命令: $1"
        cmd_help
        exit 1
        ;;
esac