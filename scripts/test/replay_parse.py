#!/usr/bin/env python3
"""
WC3 Replay 解析工具
用法: python replay_parse.py <replay.w3g>
"""

import sys
import os
import struct
from datetime import datetime

# W3G 文件格式定义
W3G_HEADER_SIZE = 128
W3G_COMPRESSION_ZLIB = 0
W3G_COMPRESSION_PK = 1

def parse_w3g_header(data):
    """解析 W3G 文件头"""
    if len(data) < W3G_HEADER_SIZE:
        return None

    # 解析文件头
    header = {
        'signature': data[0:4],
        'version': struct.unpack('<H', data[4:6])[0],
        'build_number': struct.unpack('<H', data[6:8])[0],
        'flags': struct.unpack('<H', data[8:10])[0],
        'length': struct.unpack('<I', data[0x10:0x14])[0],
        'checksum': struct.unpack('<I', data[0x14:0x18])[0],
        'header_size': struct.unpack('<I', data[0x18:0x1C])[0],
    }

    # 验证签名
    if header['signature'] != b'W3G\x01':
        print(f"警告: 未知签名 {header['signature']}")
        return None

    # 解析游戏名称（从偏移 0x58 开始）
    game_name = data[0x58:0x58+64].split(b'\x00')[0].decode('utf-8', errors='ignore')
    header['game_name'] = game_name

    # 解析时间戳
    header['timestamp'] = datetime.fromtimestamp(
        struct.unpack('<I', data[0x1C:0x20])[0]
    )

    # 解析玩家数量
    header['player_count'] = data[0x20]

    # 解析游戏长度（以 100ms 为单位）
    header['game_length_100ms'] = struct.unpack('<I', data[0x30:0x34])[0]
    header['game_length_sec'] = header['game_length_100ms'] / 10

    return header


def parse_w3g_player_info(data, offset):
    """解析玩家信息块"""
    if offset + 4 > len(data):
        return None, offset

    num_players = struct.unpack('<H', data[offset:offset+2])[0]
    offset += 2

    players = []
    for i in range(num_players):
        if offset + 25 > len(data):
            break

        player = {
            'player_id': data[offset],
            'race': data[offset + 1],
            'team': struct.unpack('<H', data[offset + 2:offset + 4])[0],
            'color': data[offset + 4],
            'flags': data[offset + 5],
        }

        # 读取玩家名称
        name_start = offset + 24
        name_end = name_start
        while name_end < len(data) and data[name_end] != 0:
            name_end += 1

        player['name'] = data[name_start:name_end].decode('utf-8', errors='ignore')
        players.append(player)

        offset = name_end + 1

    return players, offset


def analyze_replay(file_path):
    """分析 Replay 文件"""
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return

    print(f"分析回放: {file_path}")
    print("=" * 60)

    with open(file_path, 'rb') as f:
        data = f.read()

    print(f"文件大小: {len(data)} bytes")

    # 解析文件头
    header = parse_w3g_header(data)
    if not header:
        print("无法解析文件头")
        return

    print(f"\n基本信息:")
    print(f"  版本: {header['version']}")
    print(f"  构建号: {header['build_number']}")
    print(f"  游戏名称: {header['game_name']}")
    print(f"  游戏时长: {header['game_length_sec']:.1f} 秒 ({header['game_length_sec']/60:.1f} 分钟)")
    print(f"  玩家数: {header['player_count']}")
    print(f"  时间戳: {header['timestamp']}")

    # 解析玩家信息
    print(f"\n玩家信息:")
    players, offset = parse_w3g_player_info(data, W3G_HEADER_SIZE)
    if players:
        race_names = {0: 'Human', 1: 'Orc', 2: 'Undead', 3: 'Night Elf', 4: 'Random', 7: 'Custom'}
        team_names = {0: '红', 1: '蓝', 2: '青', 3: '紫', 4: '黄', 5: '橙', 6: '绿', 7: '白'}

        for p in players:
            race = race_names.get(p['race'], f'Unknown({p["race"]})')
            team = team_names.get(p['team'], f'Team {p["team"]}')
            print(f"  [{p['player_id']}] {p['name']} - {race} - {team}")
    else:
        print("  无法解析玩家信息")

    # 简化版：显示文件结构
    print(f"\n文件结构:")
    print(f"  文件头: {W3G_HEADER_SIZE} bytes")
    print(f"  玩家数据: {offset - W3G_HEADER_SIZE} bytes")
    print(f"  游戏数据: {len(data) - offset} bytes (已压缩)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python replay_parse.py <replay.w3g>")
        print("示例: python replay_parse.py tests/data/replays/game.w3g")
        sys.exit(1)

    analyze_replay(sys.argv[1])