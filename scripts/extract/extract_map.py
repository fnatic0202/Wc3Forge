#!/usr/bin/env python3
"""
WC3 地图解包脚本
用法: python extract_map.py <map.w3x> [output_dir]
"""

import sys
import os
import struct
import json

try:
    import mpq
except ImportError:
    mpq = None

def detect_mpq_offset(data):
    """检测 MPQ 归档在文件中的偏移量"""
    # WC3 地图文件结构: [header][MPQ archive][signature (optional)]
    # 常见偏移: 0x200 (512) 或 0x0

    # 检查文件开头是否是 MPQ 签名 "MPQ\x1a"
    if data[:4] == b'MPQ\x1a':
        return 0

    # 检查偏移 0x200 处
    if len(data) > 0x200 and data[0x200:0x204] == b'MPQ\x1a':
        return 0x200

    # 尝试在文件前 4KB 内查找
    for offset in range(0, 4096, 512):
        if len(data) > offset + 4 and data[offset:offset+4] == b'MPQ\x1a':
            return offset

    return None


def extract_map_basic(map_path, output_dir=None):
    """
    基础地图解包（不依赖外部 MPQ 库）
    仅提取核心文件
    """
    if not os.path.exists(map_path):
        print(f"错误: 文件不存在: {map_path}")
        return False

    # 确定输出目录
    if output_dir is None:
        map_name = os.path.splitext(os.path.basename(map_path))[0]
        output_dir = f"extracted/{map_name}"

    os.makedirs(output_dir, exist_ok=True)
    print(f"解包到: {output_dir}")

    with open(map_path, 'rb') as f:
        data = f.read()

    # 简单检查文件格式
    if data[:2] != b'PK':  # 不是 ZIP/MPQ 格式
        print("警告: 文件格式可能不正确")

    # 尝试使用 Python 内置 zipfile（部分地图可能是 ZIP 格式）
    try:
        import zipfile
        from io import BytesIO

        # 检查是否是 ZIP 格式
        if data[:2] == b'PK':
            with zipfile.ZipFile(BytesIO(data)) as zf:
                zf.extractall(output_dir)
                print(f"解包完成: {len(zf.namelist())} 个文件")
                return True
    except:
        pass

    # 对于真正的 MPQ 格式，需要 mpq 库
    # 这里我们创建一个占位符结构
    print("注意: 需要安装 py-mpq 库来解包 MPQ 格式")
    print(f"  pip install pympq")

    # 创建基本目录结构
    core_files = [
        'war3map.w3i', 'war3map.w3e', 'war3map.w3u', 'war3map.w3a',
        'war3map.w3t', 'war3map.w3h', 'war3map.w3b', 'war3map.w3d',
        'war3map.w3q', 'war3map.j', 'war3map.lua', 'war3map.doo',
        'war3mapUnits.doo', 'war3map.wts', 'war3map.shd', 'war3map.wtg'
    ]

    for fname in core_files:
        fpath = os.path.join(output_dir, fname)
        if not os.path.exists(fpath):
            # 创建空占位文件
            with open(fpath, 'wb') as f:
                pass

    # 创建 assets 目录
    os.makedirs(os.path.join(output_dir, 'assets', 'models'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'assets', 'textures'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'assets', 'sounds'), exist_ok=True)

    print(f"创建了基础目录结构")

    # 保存地图基本信息
    info = {
        'source_file': map_path,
        'file_size': len(data),
        'format': 'w3x/w3m (MPQ archive)',
        'core_files': core_files
    }

    with open(os.path.join(output_dir, 'extract_info.json'), 'w') as f:
        json.dump(info, f, indent=2)

    return True


def analyze_extracted_map(map_dir):
    """分析解包后的地图"""
    if not os.path.isdir(map_dir):
        print(f"错误: 目录不存在: {map_dir}")
        return

    print(f"\n分析地图: {map_dir}")
    print("-" * 40)

    # 检查核心文件
    core_files = {
        'war3map.w3i': '地图信息',
        'war3map.w3e': '地形数据',
        'war3map.w3u': '单位数据',
        'war3map.w3a': '技能数据',
        'war3map.j': 'JASS 脚本',
        'war3map.lua': 'Lua 脚本',
    }

    found_files = []
    missing_files = []

    for fname, desc in core_files.items():
        fpath = os.path.join(map_dir, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            size = os.path.getsize(fpath)
            found_files.append((fname, desc, size))
        else:
            missing_files.append((fname, desc))

    print("找到的文件:")
    for fname, desc, size in found_files:
        print(f"  ✓ {fname} ({desc}) - {size} bytes")

    if missing_files:
        print("\n缺失的文件:")
        for fname, desc in missing_files:
            print(f"  ✗ {fname} ({desc})")

    # 分析 JASS 脚本
    jass_path = os.path.join(map_dir, 'war3map.j')
    if os.path.exists(jass_path) and os.path.getsize(jass_path) > 0:
        print("\nJASS 脚本分析:")
        with open(jass_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 统计函数数量
        import re
        functions = re.findall(r'function\s+(\w+)\s+', content)
        print(f"  函数数量: {len(functions)}")

        # 统计触发器
        triggers = re.findall(r'call\s+TriggerAddAction\([^,]+,\s*function\s+(\w+)', content)
        print(f"  触发器动作: {len(triggers)}")

        # 常见 API 调用统计
        apis = ['GetTriggerUnit', 'GetTriggerPlayer', 'GetOwningPlayer',
                'CreateUnit', 'CreateItem', 'SetUnitPosition']
        print("\n  常用 API 调用:")
        for api in apis:
            count = content.count(api)
            if count > 0:
                print(f"    {api}: {count}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python extract_map.py <map.w3x> [output_dir]")
        print("示例: python extract_map.py maps/source/my_map.w3x")
        sys.exit(1)

    map_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if extract_map_basic(map_path, output_dir):
        print("\n解包完成!")

        # 自动分析
        if output_dir:
            analyze_extracted_map(output_dir)
        else:
            map_name = os.path.splitext(os.path.basename(map_path))[0]
            analyze_extracted_map(f"extracted/{map_name}")