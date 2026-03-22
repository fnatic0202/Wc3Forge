#!/usr/bin/env python3
"""
WC3 地图二进制对比分析工具
比较生成的地图与官方地图的二进制差异
"""

import os
import sys
import struct

def read_file(path):
    """读取文件"""
    with open(path, 'rb') as f:
        return f.read()

def compare_headers(hello_data, bay_data):
    """对比 HM3W 头部"""
    print("\n" + "="*60)
    print("HM3W 头部对比分析")
    print("="*60)

    # 检查签名
    hello_sig = hello_data[0:4]
    bay_sig = bay_data[0:4]
    print(f"签名: hello={hello_sig} (期望: b'HM3W')")
    print(f"      bay ={bay_sig}")

    # 版本 (offset 4)
    hello_ver = struct.unpack('<I', hello_data[4:8])[0]
    bay_ver = struct.unpack('<I', bay_data[4:8])[0]
    print(f"版本: hello={hello_ver} (期望: 0)")
    print(f"      bay ={bay_ver}")

    # 地图 ID (offset 8)
    hello_id = struct.unpack('<I', hello_data[8:12])[0]
    bay_id = struct.unpack('<I', bay_data[8:12])[0]
    print(f"地图ID: hello=0x{hello_id:08X} (期望: 0x149C0000)")
    print(f"        bay =0x{bay_id:08X}")

    # 名称长度 (offset 16)
    hello_name_len = struct.unpack('<I', hello_data[16:20])[0]
    bay_name_len = struct.unpack('<I', bay_data[16:20])[0]
    print(f"名称长度: hello={hello_name_len}")
    print(f"          bay ={bay_name_len}")

    # MPQ 偏移 (offset 20)
    hello_mpq_offset = struct.unpack('<I', hello_data[20:24])[0]
    bay_mpq_offset = struct.unpack('<I', bay_data[20:24])[0]
    print(f"MPQ偏移: hello={hello_mpq_offset} (期望: 512 或 131072)")
    print(f"        bay ={bay_mpq_offset}")

    # 名称 (offset 32)
    hello_name = hello_data[32:96].rstrip(b'\x00').decode('gbk', errors='replace')
    bay_name = bay_data[32:96].rstrip(b'\x00').decode('gbk', errors='replace')
    print(f"地图名称: hello='{hello_name}'")
    print(f"          bay ='{bay_name}'")

    # 作者 (offset 96)
    hello_author = hello_data[96:160].rstrip(b'\x00').decode('gbk', errors='replace')
    bay_author = bay_data[96:160].rstrip(b'\x00').decode('gbk', errors='replace')
    print(f"作者: hello='{hello_author}'")
    print(f"      bay ='{bay_author}'")

    # 描述 (offset 160)
    hello_desc = hello_data[160:288].rstrip(b'\x00').decode('gbk', errors='replace')
    bay_desc = bay_data[160:288].rstrip(b'\x00').decode('gbk', errors='replace')
    print(f"描述: hello='{hello_desc}'")
    print(f"      bay ='{bay_desc}'")

    # 地图尺寸 (offset 300)
    hello_width = struct.unpack('<H', hello_data[300:302])[0]
    hello_height = struct.unpack('<H', hello_data[302:304])[0]
    bay_width = struct.unpack('<H', bay_data[300:302])[0]
    bay_height = struct.unpack('<H', bay_data[302:304])[0]
    print(f"地图尺寸: hello={hello_width}x{hello_height}")
    print(f"          bay ={bay_width}x{bay_height}")

    # tileset (offset 308)
    hello_tileset = chr(hello_data[308]) if hello_data[308] < 128 else '?'
    bay_tileset = chr(bay_data[308]) if bay_data[308] < 128 else '?'
    print(f"地形: hello='{hello_tileset}' (L=Lordaeron)")
    print(f"      bay ='{bay_tileset}'")

    # MPQ 大小 (offset 312)
    hello_mpq_size = struct.unpack('<I', hello_data[312:316])[0]
    bay_mpq_size = struct.unpack('<I', bay_data[312:316])[0]
    print(f"MPQ大小: hello={hello_mpq_size} bytes")
    print(f"        bay ={bay_mpq_size} bytes")

    return {
        'signature_ok': hello_sig == b'HM3W',
        'version_ok': hello_ver == bay_ver,
        'map_id_ok': hello_id == bay_id,
        'mpq_offset_ok': hello_mpq_offset == bay_mpq_offset,
    }

def find_mpq_start(data, start=0):
    """查找 MPQ 签名位置"""
    for i in range(start, min(start + 1024, len(data) - 4)):
        if data[i:i+4] == b'MPQ\x1a':
            return i
    return -1

def check_mpq_structure(data, offset):
    """检查 MPQ 结构"""
    print(f"\nMPQ 起始位置: {offset} (0x{offset:X})")

    if offset + 4 > len(data):
        print("数据不足")
        return False

    # MPQ 签名
    mpq_sig = data[offset:offset+4]
    print(f"MPQ 签名: {mpq_sig}")

    # 头部大小
    if offset + 8 <= len(data):
        header_size = struct.unpack('<I', data[offset+4:offset+8])[0]
        print(f"头部大小: {header_size}")

    # 文件列表
    if offset + 20 <= len(data):
        archive_size = struct.unpack('<I', data[offset+16:offset+20])[0]
        print(f"归档大小: {archive_size}")

    return mpq_sig == b'MPQ\x1a'

def analyze_mpq_files(data, offset):
    """分析 MPQ 内部文件"""
    print("\n" + "="*60)
    print("MPQ 内部文件分析")
    print("="*60)

    # 跳过 MPQ 头部，查找文件
    # 标准 MPQ: 偏移 0x200 (512) 处是 MPQ 签名
    if offset + 32 > len(data):
        print("数据不足")
        return

    # 尝试从 offset 位置开始查找文件
    pos = offset + 20  # 跳过 MPQ 头

    # 简单方法: 查找已知的文件名字符串
    known_files = [
        b'war3map.w3i', b'war3map.w3e', b'war3map.w3u',
        b'war3map.w3a', b'war3map.w3t', b'war3map.j',
        b'war3map.doo', b'war3map.wts'
    ]

    print("\n搜索已知文件...")
    for fname in known_files:
        idx = data.find(fname, offset)
        if idx >= 0:
            print(f"  找到: {fname.decode()} @ 0x{idx:X}")
        else:
            print(f"  未找到: {fname.decode()}")

def compare_mpq_content(hello_data, bay_data, hello_offset, bay_offset):
    """对比 MPQ 内容"""
    print("\n" + "="*60)
    print("MPQ 内容对比")
    print("="*60)

    # 找到 war3map.w3i 的位置
    hello_w3i = hello_data.find(b'war3map.w3i', hello_offset)
    bay_w3i = bay_data.find(b'war3map.w3i', bay_offset)

    print(f"\nwar3map.w3i 位置:")
    print(f"  hello: 0x{hello_w3i:X}")
    print(f"  bay:   0x{bay_w3i:X}")

    if hello_w3i > 0 and bay_w3i > 0:
        # 对比 w3i 文件头部
        print(f"\nwar3map.w3i 头部 (前 32 字节):")
        print(f"  hello: {hello_data[hello_w3i:hello_w3i+32].hex()}")
        print(f"  bay:   {bay_data[bay_w3i:bay_w3i+32].hex()}")

        # format_version
        hello_fv = struct.unpack('<I', hello_data[hello_w3i:hello_w3i+4])[0]
        bay_fv = struct.unpack('<I', bay_data[bay_w3i:bay_w3i+4])[0]
        print(f"  format_version: hello={hello_fv}, bay={bay_fv}")

def find_all_strings(data, min_len=4):
    """查找所有可打印字符串"""
    strings = []
    current = b''

    for byte in data:
        if 32 <= byte <= 126:
            current += bytes([byte])
        else:
            if len(current) >= min_len:
                strings.append(current)
            current = b''

    return strings

def main():
    hello_path = '/home/nx/rpg/sample_map/hello_rpg.w3x'
    bay_path = '/mnt/e/Warcraft III Frozen Throne/Warcraft III Frozen Throne/Maps/(2)BootyBay.w3m'

    if not os.path.exists(hello_path):
        print(f"错误: 找不到 {hello_path}")
        return

    if not os.path.exists(bay_path):
        print(f"错误: 找不到 {bay_path}")
        return

    print(f"读取地图文件...")
    print(f"  hello: {hello_path}")
    print(f"  bay:   {bay_path}")

    hello_data = read_file(hello_path)
    bay_data = read_file(bay_path)

    print(f"\n文件大小:")
    print(f"  hello: {len(hello_data)} bytes ({len(hello_data)/1024:.1f} KB)")
    print(f"  bay:   {len(bay_data)} bytes ({len(bay_data)/1024:.1f} KB)")

    # 对比头部
    results = compare_headers(hello_data, bay_data)

    # 查找 MPQ 起始位置
    print("\n" + "="*60)
    print("MPQ 结构分析")
    print("="*60)

    # 在 512 (0x200) 处查找 MPQ
    hello_mpq = find_mpq_start(hello_data, 0x200)
    bay_mpq = find_mpq_start(bay_data, 0x200)

    print(f"\nMPQ 签名位置:")
    print(f"  hello: 0x{hello_mpq:X}")
    print(f"  bay:   0x{bay_mpq:X}")

    if hello_mpq >= 0:
        check_mpq_structure(hello_data, hello_mpq)
    if bay_mpq >= 0:
        check_mpq_structure(bay_data, bay_mpq)

    # 分析 MPQ 文件
    if hello_mpq >= 0:
        analyze_mpq_files(hello_data, hello_mpq)

    # 对比 MPQ 内容
    compare_mpq_content(hello_data, bay_data, hello_mpq, bay_mpq)

    # 总结
    print("\n" + "="*60)
    print("检查结果总结")
    print("="*60)
    for key, value in results.items():
        status = "OK" if value else "FAIL"
        print(f"  {key}: {status}")

    # 提示问题
    print("\n可能的问题:")
    if not results['version_ok']:
        print("  - 版本号不匹配")
    if not results['map_id_ok']:
        print("  - 地图ID不匹配 (应为 0x149C0000)")
    if hello_mpq != bay_mpq or hello_mpq < 0:
        print("  - MPQ 偏移位置不正确")

    # 保存详细对比报告
    report_path = '/home/nx/rpg/scripts/test/compare_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("WC3 地图对比分析报告\n")
        f.write("="*60 + "\n\n")
        f.write(f"hello_rpg: {hello_path}\n")
        f.write(f"BootyBay:  {bay_path}\n\n")
        f.write(f"文件大小: hello={len(hello_data)}, bay={len(bay_data)}\n\n")
        f.write("头部差异:\n")
        f.write(f"  版本: hello={struct.unpack('<I', hello_data[4:8])[0]}, bay={struct.unpack('<I', bay_data[4:8])[0]}\n")
        f.write(f"  地图ID: hello=0x{struct.unpack('<I', hello_data[8:12])[0]:08X}, bay=0x{struct.unpack('<I', bay_data[8:12])[0]:08X}\n")
        f.write(f"  MPQ偏移: hello={struct.unpack('<I', hello_data[20:24])[0]}, bay={struct.unpack('<I', bay_data[20:24])[0]}\n")
        f.write(f"  MPQ位置: hello=0x{hello_mpq:X}, bay=0x{bay_mpq:X}\n")

    print(f"\n报告已保存到: {report_path}")

if __name__ == '__main__':
    main()