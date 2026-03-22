#!/usr/bin/env python3
"""
WC3 地图构建脚本
用法: python build_map.py [options]

选项:
  --src <dir>     源码目录 (默认: sample_map/src)
  --output <file> 输出地图文件 (默认: sample_map/hello_rpg.w3x)
  --compress     启用压缩
"""

import sys
import os
import struct
import zipfile
import argparse

# WC3 地图文件签名和版本
W3X_SIGNATURE = b'W3G\x01'  # 对于 w3g 是 W3G\x01，w3x 使用不同签名
W3X_VERSION_CLASSIC = 18    # Classic
W3X_VERSION_REFORGED = 28   # Reforged

# 内部文件列表
CORE_FILES = [
    'war3map.w3i',  # 地图信息
    'war3map.w3e',  # 地形
    'war3map.w3u',  # 单位
    'war3map.w3a',  # 技能
    'war3map.w3t',  # 物品
    'war3map.w3h',  # 科技
    'war3map.w3b',  # Buff
    'war3map.w3d',  # Doodad
    'war3map.w3q',  # 升级
    'war3map.j',    # JASS 脚本
    'war3map.doo',  # Doodad 放置
    'war3mapUnits.doo', # 单位放置
    'war3map.wts',  # 字符串
    'war3map.shd',  # 阴影
]


def create_w3i():
    """创建 war3map.w3i (地图信息文件)"""
    # 这是一个最小化的 w3i 文件结构
    # 格式: 大端序整数/浮点数
    data = bytearray()

    # 地图标志
    data += b'\x00\x00\x00\x00'  # flags
    data += b'\x00\x00\x00\x00'  # directory offset

    # 地图名称 (64 bytes, null-terminated)
    name = b'Hello RPG\x00' + b'\x00' * (64 - len(b'Hello RPG\x00'))
    data += name

    # 地图作者
    author = b'RPG Project\x00' + b'\x00' * (64 - len(b'RPG Project\x00'))
    data += author

    # 描述
    desc = b'A simple RPG demo map\x00' + b'\x00' * (128 - len(b'A simple RPG demo map\x00'))
    data += desc

    # 地图尺寸 (width, height)
    data += struct.pack('<H', 64)   # width in tiles
    data += struct.pack('<H', 64)   # height in tiles

    # 边界
    data += struct.pack('<f', -4096.0)  # left
    data += struct.pack('<f', 4096.0)   # right
    data += struct.pack('<f', -4096.0)  # bottom
    data += struct.pack('<f', 4096.0)   # top

    # 玩家数量
    data += b'\x01'  # 1 player
    data += b'\x00' * 3  # padding

    # 地形文件
    terrain = b'war3map.w3e\x00'
    data += terrain + b'\x00' * (260 - len(terrain))

    # 声音文件
    data += b'\x00' * 260

    return bytes(data)


def create_w3e():
    """创建 war3map.w3e (地形文件) - 简化版"""
    data = bytearray()

    # 地形版本
    data += struct.pack('<I', 1)  # version

    # 地图尺寸
    width = 64
    height = 64
    data += struct.pack('<I', width)
    data += struct.pack('<I', height)

    # 地形数据 (简化: 所有 tiles 使用相同设置)
    # 每个 tile: 4 bytes (flags, ground height, water height, edge)
    for y in range(height):
        for x in range(width):
            # 默认地面高度 0，草地纹理
            data += struct.pack('<BBBB', 0, 0, 0, 0)  # flags, ground, water, cliff

    # 悬崖数据 (简化)
    data += struct.pack('<I', 0)  # cliff count

    return bytes(data)


def create_w3u():
    """创建 war3map.w3u (单位数据) - 简化版"""
    data = bytearray()

    # 版本
    data += struct.pack('<I', 1)

    # 自定义单位数量 (0)
    data += struct.pack('<I', 0)

    return bytes(data)


def create_w3a():
    """创建 war3map.w3a (技能数据) - 简化版"""
    data = bytearray()
    data += struct.pack('<I', 1)  # version
    data += struct.pack('<I', 0)  # custom ability count
    return bytes(data)


def create_w3t():
    """创建 war3map.w3t (物品数据) - 简化版"""
    data = bytearray()
    data += struct.pack('<I', 1)
    data += struct.pack('<I', 0)  # custom item count
    return bytes(data)


def create_doo(units_file=True):
    """创建 war3map.doo 或 war3mapUnits.doo"""
    data = bytearray()
    data += struct.pack('<I', 1)  # version

    # 简化版本：无单位/doodad
    data += struct.pack('<I', 0)  # count

    return bytes(data)


def create_wts():
    """创建 war3map.wts (字符串表)"""
    data = bytearray()

    # 字符串数量
    count = 5
    data += struct.pack('<I', count)

    # 字符串 (偏移量先设为 0，稍后填充)
    strings = [
        'Hello RPG',
        'A simple RPG demo map',
        'Hero',
        'Enemy',
        'Gold'
    ]

    # 写入字符串
    offset = 4 + count * 4  # header size
    string_offsets = []

    for s in strings:
        string_offsets.append(offset)
        data += s.encode('utf-8') + b'\x00'
        offset += len(s) + 1

    # 填充偏移量
    result = bytearray()
    result += struct.pack('<I', count)

    for i, off in enumerate(string_offsets):
        # 重新计算相对于字符串数据开始的偏移
        data_offset = 4 + count * 4 + off - string_offsets[0]
        result += struct.pack('<I', data_offset)

    result += bytes(data[len(result):])

    return bytes(result)


def create_war3map_j(src_dir):
    """读取或创建 war3map.j"""
    jass_path = os.path.join(src_dir, 'war3map.j')
    if os.path.exists(jass_path):
        with open(jass_path, 'rb') as f:
            return f.read()

    # 默认 JASS
    return b'''// Default war3map.j
function main takes nothing returns nothing
    call DisplayTextToPlayer(Player(0), 0, 0, "Hello from WC3!")
endfunction
'''


def create_map(src_dir, output_path, compress=False):
    """创建 w3x 地图文件"""

    print(f"构建地图: {output_path}")
    print(f"源码目录: {src_dir}")

    # 如果输出是 .w3x，使用 ZIP 格式（现代 WC3 支持）
    if output_path.endswith('.w3x'):
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED) as zf:
                # 添加核心文件
                for filename in CORE_FILES:
                    src_path = os.path.join(src_dir, filename)
                    if os.path.exists(src_path):
                        zf.write(src_path, filename)
                        print(f"  添加: {filename}")
                    else:
                        # 创建默认文件
                        if filename == 'war3map.w3i':
                            data = create_w3i()
                        elif filename == 'war3map.w3e':
                            data = create_w3e()
                        elif filename == 'war3map.w3u':
                            data = create_w3u()
                        elif filename == 'war3map.w3a':
                            data = create_w3a()
                        elif filename == 'war3map.w3t':
                            data = create_w3t()
                        elif filename == 'war3map.doo':
                            data = create_doo(False)
                        elif filename == 'war3mapUnits.doo':
                            data = create_doo(True)
                        elif filename == 'war3map.wts':
                            data = create_wts()
                        elif filename == 'war3map.j':
                            data = create_war3map_j(src_dir)
                        else:
                            data = b''

                        if data:
                            zf.writestr(filename, data)
                            print(f"  创建: {filename}")

            print(f"\n地图构建完成: {output_path}")
            return True

        except Exception as e:
            print(f"错误: {e}")
            return False
    else:
        print("错误: 暂仅支持 .w3x 格式")
        return False


def main():
    parser = argparse.ArgumentParser(description='WC3 地图构建工具')
    parser.add_argument('--src', default='sample_map/src', help='源码目录')
    parser.add_argument('--output', default='sample_map/hello_rpg.w3x', help='输出文件')
    parser.add_argument('--compress', action='store_true', help='启用压缩')

    args = parser.parse_args()

    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    create_map(args.src, args.output, args.compress)


if __name__ == '__main__':
    main()