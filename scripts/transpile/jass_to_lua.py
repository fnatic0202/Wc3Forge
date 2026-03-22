#!/usr/bin/env python3
"""
JASS to Lua 转译工具
用法: python jass_to_lua.py <input.j> [output.lua]
"""

import sys
import os
import re

# JASS 到 Lua 的基本转换规则
JASS_TO_LUA_RULES = {
    # 数组访问
    r'(\w+)\s*\[\s*(\w+)\s*\]': r'\1[\2]',

    # 全局变量访问
    r'Get\s+(\w+)': r'Blizzard.Get\1',

    # 函数调用转换
    r'Call\s+(\w+)': r'\1()',
}

# 需要转换的 API 映射
API_MAPPING = {
    # 触发器
    'CreateTrigger': 'Trigger',
    'GetTriggerUnit': 'GetTriggerUnit',
    'GetTriggerPlayer': 'GetTriggerPlayer',
    'TriggerRegisterEnterRectSimple': 'TriggerRegisterEnterRect',
    'TriggerRegisterLeaveRectSimple': 'TriggerRegisterLeaveRect',

    # 单位
    'CreateUnit': 'CreateUnit',
    'CreateUnitAtLoc': 'CreateUnitAtLoc',
    'RemoveUnit': 'RemoveUnit',
    'KillUnit': 'KillUnit',
    'GetUnitX': 'GetUnitX',
    'GetUnitY': 'GetUnitY',
    'SetUnitPosition': 'SetUnitPosition',
    'SetUnitPositionLoc': 'SetUnitPosition',
    'GetUnitState': 'GetUnitState',
    'SetUnitState': 'SetUnitState',
    'GetUnitLife': 'GetWidgetLife',
    'SetUnitLife': 'SetWidgetLife',
    'GetUnitMana': 'GetUnitState',
    'SetUnitMana': 'SetUnitState',

    # 玩家
    'GetOwningPlayer': 'GetOwningPlayer',
    'GetTriggerPlayer': 'GetTriggerPlayer',
    'GetLocalPlayer': 'GetLocalPlayer',
    'GetConvertedPlayerId': 'GetPlayerId',

    # 单位组
    'CreateGroup': 'Group',
    'GroupAddUnit': 'GroupAddUnit',
    'GroupRemoveUnit': 'GroupRemoveUnit',
    'ForGroup': 'ForGroup',
    'FirstOfGroup': 'FirstOfGroup',

    # 物品
    'CreateItem': 'CreateItem',
    'CreateItemAtLoc': 'CreateItemAtLoc',
    'RemoveItem': 'RemoveItem',
    'GetItemX': 'GetItemX',
    'GetItemY': 'GetItemY',

    # UI
    'DisplayTextToPlayer': 'DisplayTextToPlayer',
    'DisplayTimedTextToPlayer': 'DisplayTimedTextToPlayer',
    'DisplayTextToForce': 'DisplayTextToForce',

    # 特效
    'AddSpecialEffect': 'AddSpecialEffect',
    'AddSpecialEffectLoc': 'AddSpecialEffect',
    'AddSpecialEffectTarget': 'AddSpecialEffectTarget',
    'DestroyEffect': 'DestroyEffect',

    # 数学
    'GetRandomInt': 'GetRandomInt',
    'GetRandomReal': 'GetRandomReal',
    'Deg2Rad': 'DegToRad',
    'Rad2Deg': 'RadToDeg',

    # 字符串
    'I2S': 'I2S',
    'S2I': 'S2I',
    'R2S': 'R2S',
    'S2R': 'S2R',
}

# BJ 函数后缀
BJ_SUFFIX = 'BJ'


def convert_jass_to_lua(jass_code):
    """将 JASS 代码转换为 Lua 代码"""

    lua_code = jass_code

    # 1. 转换注释
    lua_code = re.sub(r'//(.+)$', r'-- \1', lua_code, flags=re.MULTILINE)

    # 2. 转换函数定义
    # function xxx returns yyy -> function xxx()
    lua_code = re.sub(
        r'function\s+(\w+)\s+returns\s+(\w+)',
        r'function \1()',
        lua_code
    )

    # 3. 转换全局变量声明
    # globals ... endglobals -> local globals = {}
    lua_code = re.sub(
        r'globals\s*\n(.*?)\nendglobals',
        r'-- globals\nlocal g = {}',
        lua_code,
        flags=re.DOTALL
    )

    # 4. 转换本地变量声明
    # local integer x -> local x
    lua_code = re.sub(
        r'local\s+(?:integer|real|boolean|string|handle|unit|player|item|location|rect|group|trigger|force|timer|effect|destructable)\s+(\w+)',
        r'local \1',
        lua_code
    )

    # 5. 转换 set x = y -> x = y
    lua_code = re.sub(r'^(\s*)set\s+', r'\1', lua_code, flags=re.MULTILINE)

    # 6. 转换调用语法
    # call Function(x, y) -> Function(x, y)
    lua_code = re.sub(r'^(\s*)call\s+(\w+)\(', r'\1\2(', lua_code, flags=re.MULTILINE)

    # 7. 转换数组赋值
    # set array[x] = y -> array[x] = y
    lua_code = re.sub(r'set\s+(\w+)\[([^\]]+)\]\s*=\s*(.+)', r'\1[\2] = \3', lua_code)

    # 8. 转换 if then elseif then else then endif
    # JASS: if x then ... else then ... endif
    # Lua: if x then ... elseif ... then ... else ... end
    lua_code = re.sub(r'\belse\s+then\b', 'else', lua_code)
    lua_code = re.sub(r'\bendif\b', 'end', lua_code)
    lua_code = re.sub(r'\bthen\s+endif\b', 'end', lua_code)

    # 9. 转换 loop endloop
    # loop -> while true do
    # endloop -> end
    lua_code = re.sub(r'\bloop\b', 'while true do', lua_code)
    lua_code = re.sub(r'\bendloop\b', 'end', lua_code)

    # 10. 转换 exitwhen
    # exitwhen x -> if x then break end
    lua_code = re.sub(r'exitwhen\s+(.+)', r'if \1 then break end', lua_code)

    # 11. 转换 return
    lua_code = re.sub(r'\breturn\b', 'return', lua_code)

    # 12. 转换 and/or
    lua_code = lua_code.replace(' and ', ' and ')
    lua_code = lua_code.replace(' or ', ' or ')

    # 13. 转换 API 名称（添加 Blizzard. 前缀）
    for jass_api, lua_api in API_MAPPING.items():
        if jass_api != lua_api:
            lua_code = re.sub(r'\b' + jass_api + r'\b', lua_api, lua_code)

    # 14. 添加 Blizzard 命名空间包装
    # 这是一个简化处理，完整的转换需要更复杂的分析

    return lua_code


def add_lua_header(lua_code):
    """添加 Lua 文件头和 Blizzard 模拟"""
    header = '''--[[
    WC3 Lua Script
    自动从 JASS 转换生成
    警告: 此文件需要手动调整以适配 WC3 Lua API
]]

-- Blizzard API 模拟（需要根据实际 API 调整）
local Blizzard = setmetatable({}, {
    __index = function(t, k)
        -- 动态查找 WC3 原生 API
        return rawget(t, k) or _G[k]
    end
})

-- 常用类型别名
local unit = BlzGetUnit()
local player = GetTriggerPlayer()
local group = CreateGroup()
local trigger = CreateTrigger()
local item = CreateItem()

'''
    return header + lua_code


def convert_file(input_path, output_path=None):
    """转换文件"""
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在: {input_path}")
        return False

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + '.lua'

    print(f"转换: {input_path} -> {output_path}")

    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        jass_code = f.read()

    # 转换
    lua_code = convert_jass_to_lua(jass_code)
    lua_code = add_lua_header(lua_code)

    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(lua_code)

    print(f"转换完成!")
    print(f"\n注意: 此转换是基础转换，需要手动调整:")
    print("  1. 调整 Blizzard API 调用")
    print("  2. 处理类型转换")
    print("  3. 验证逻辑正确性")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python jass_to_lua.py <input.j> [output.lua]")
        print("示例: python jass_to_lua.py war3map.j war3map.lua")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_file(input_file, output_file)