#!/usr/bin/env python3
"""
JASS 脚本分析工具
用法: python count_api.py <war3map.j>
"""

import sys
import os
import re
from collections import Counter

# 常用 JASS API 列表（按类别分组）
JASS_API_CATEGORIES = {
    '触发器': [
        'CreateTrigger', 'DestroyTrigger', 'EnableTrigger', 'DisableTrigger',
        'TriggerAddCondition', 'TriggerAddAction', 'TriggerRegisterVariableEvent',
        'TriggerRegisterPlayerEvent', 'TriggerRegisterUnitEvent',
        'GetTriggeringTrigger', 'GetTriggerUnit', 'GetTriggerEval',
        'GetTriggerExecCount', 'GetTriggerActionCount'
    ],
    '单位': [
        'CreateUnit', 'CreateUnitByName', 'CreateUnitAtLoc', 'CreateUnitAtPoint',
        'RemoveUnit', 'KillUnit', 'RemoveAllItems', 'GetUnitX', 'GetUnitY',
        'GetUnitLoc', 'SetUnitPosition', 'SetUnitX', 'SetUnitY',
        'GetUnitTypeId', 'GetUnitUserData', 'SetUnitUserData',
        'GetOwningPlayer', 'GetUnitsInRect', 'GetUnitsInRangeOfLoc',
        'GetUnitState', 'SetUnitState', 'GetUnitLife', 'SetUnitLife',
        'GetUnitMana', 'SetUnitMana', 'GetUnitMaxLife', 'GetUnitState',
        'IsUnit', 'IsUnitInGroup', 'IsUnitInRangeOfLoc', 'IsUnitVisible',
        'ShowUnit', 'HideUnit', 'UnitAddAbility', 'UnitRemoveAbility',
        'UnitAddItem', 'UnitRemoveItem', 'UnitUseItem', 'UnitUseItemPoint'
    ],
    '玩家': [
        'GetTriggerPlayer', 'GetLocalPlayer', 'GetOwningPlayer',
        'GetConvertedPlayerId', 'GetPlayerId', 'GetPlayerTeam',
        'GetPlayerController', 'GetPlayerRace', 'GetPlayerStartLocation',
        'GetForceOfPlayer', 'GetPlayersAll', 'GetPlayersByTeam',
        'GetPlayersMatching', 'IsPlayerEnemy', 'IsPlayerAlly',
        'SetPlayerTechResearched', 'SetPlayerUnitAvailable'
    ],
    '单位组': [
        'CreateGroup', 'DestroyGroup', 'GroupAddUnit', 'GroupRemoveUnit',
        'GroupClear', 'GroupEnumUnitsInRect', 'GroupEnumUnitsInRangeOfLoc',
        'ForGroup', 'FirstOfGroup', 'GetGroupUnitCount',
        'GroupImmediateOrder', 'GroupPointOrder', 'GroupTargetOrder'
    ],
    '物品': [
        'CreateItem', 'CreateItemAtLoc', 'CreateItemById',
        'RemoveItem', 'GetItemX', 'GetItemY', 'GetItemLoc',
        'GetItemTypeId', 'GetItemUserData', 'SetItemUserData',
        'GetItemLevel', 'GetItemCharges', 'SetItemCharges',
        'GetItemLife', 'SetItemLife', 'GetItemName',
        'IsItemVisible', 'IsItemOwned', 'IsItemPawnable',
        'ShowItem', 'HideItem'
    ],
    '技能/魔法': [
        'GetSpellAbilityId', 'GetSpellTargetUnit', 'GetSpellTargetLoc',
        'GetSpellTargetX', 'GetSpellTargetY', 'GetAbilityName',
        'GetAbilityLevel', 'SetAbilityLevel', 'EnableAbility',
        'DisableAbility', 'UnitAddAbility', 'UnitRemoveAbility',
        'GetLearnedSkill', 'GetLearnedSkillLevel', 'SelectHeroSkill'
    ],
    '地形/区域': [
        'GetRectCenter', 'GetRectMinX', 'GetRectMaxX', 'GetRectMinY', 'GetRectMaxY',
        'GetRectFromCircleBJ', 'GetRectFromCircle',
        'IsPointInRegion', 'IsPointInRect', 'IsUnitInRegion',
        'GetEnteringUnit', 'GetLeavingUnit', 'GetFilterUnit'
    ],
    '相机': [
        'SetCameraPosition', 'SetCameraTargetController', 'SetCameraBounds',
        'SetCameraField', 'GetCameraTargetPositionX', 'GetCameraTargetPositionY',
        'GetCameraTargetPositionZ', 'SetCameraQuickPosition',
        'PanCameraTo', 'PanCameraToTimed', 'ResetToGameCamera'
    ],
    'UI/消息': [
        'DisplayTextToPlayer', 'DisplayTimedTextToPlayer', 'DisplayTextToForce',
        'DisplayTimedTextFromPlayer', 'ClearTextMessages', 'SimulateMessage',
        'GetLocalPlayer', 'GetPlayerName', 'GetPlayerColor'
    ],
    '音效': [
        'PlaySound', 'StopSound', 'SetSoundVolume', 'SetSoundPosition',
        'AttachSoundToUnit', 'PlayMusic', 'PlayMusicEx', 'StopMusic',
        'GetSoundDuration', 'GetSoundFileDuration'
    ],
    '特效': [
        'CreateEffect', 'CreateEffectAtLoc', 'CreateDestructable',
        'CreateDestructableAtLoc', 'CreateDeadDestructable', 'CreateDeadDestructableAtLoc',
        'AddSpecialEffect', 'AddSpecialEffectLoc', 'AddSpecialEffectTarget',
        'DestroyEffect', 'GetEffectName', 'GetEffectPosition'
    ],
    '任务/对话': [
        'CreateQuest', 'DestroyQuest', 'QuestSetEnabled', 'QuestSetCompleted',
        'QuestSetFailed', 'QuestSetRequired', 'QuestSetDiscovered',
        'CreateQuestItem', 'QuestItemSetDescription', 'QuestItemSetCompleted',
        'CreateDialog', 'DestroyDialog', 'DialogAddButton', 'DialogClear',
        'DialogAddMessage', 'GetClickedButton', 'GetClickedDialog'
    ],
    '存档': [
        'SaveInteger', 'SaveReal', 'SaveBoolean', 'SaveStr', 'SavePlayerHandle',
        'SaveUnitHandle', 'SaveItemHandle', 'SaveAbilityHandle',
        'LoadInteger', 'LoadReal', 'LoadBoolean', 'LoadStr', 'LoadPlayerHandle',
        'LoadUnitHandle', 'LoadItemHandle', 'LoadAbilityHandle',
        'HaveSavedInteger', 'RemoveSavedInteger', 'FlushGameCache'
    ],
    '数学/逻辑': [
        'GetRandomInt', 'GetRandomReal', 'GetRandomDestructable', 'GetRandomUnit',
        'I2R', 'R2I', 'I2S', 'R2S', 'S2I', 'S2R', 'GetHandleId',
        'ModuloInteger', 'Deg2Rad', 'Rad2Deg', 'Sin', 'Cos', 'Tan',
        'ASin', 'ACos', 'ATan', 'ATan2', 'SquareRoot', 'Pow'
    ],
    'BJ 函数 (Blizzard.j)': [
        'GetTriggerUnit', 'GetTriggerPlayer', 'GetOwningPlayer',
        'GetRectCenter', 'GetUnitsInRectAll', 'GetUnitsInRangeOfLocAll',
        'GroupEnumAllUnitsInRect', 'ForGroup', 'ForForce',
        'CreateQuestItem', 'CreateDefeatConditionItem',
        'AddSpecialEffectTargetUnitBJ', 'DestroyEffectBJ',
        'SetUnitPositionLocBJ', 'CreateUnitAtLocSaveLast',
        'DisplayTextToForce', 'PingMinimapLocForForce',
        'ConditionalTriggerExecute', 'DoNothing'
    ]
}


def analyze_jass(file_path):
    """分析 JASS 脚本"""
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return

    print(f"分析文件: {file_path}")
    print("=" * 60)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.split('\n')

    # 基本统计
    print(f"\n基本统计:")
    print(f"  总行数: {len(lines)}")
    print(f"  文件大小: {len(content)} bytes")

    # 统计函数定义
    func_defs = re.findall(r'function\s+(\w+)\s+returns\s+(\w+)', content)
    print(f"  函数定义: {len(func_defs)}")

    # 统计触发器
    trigger_creates = re.findall(r'call\s+CreateTrigger\(\)', content)
    print(f"  触发器创建: {len(trigger_creates)}")

    trigger_actions = re.findall(r'call\s+TriggerAddAction\([^,]+,\s*function\s+(\w+)', content)
    print(f"  触发器动作: {len(trigger_actions)}")

    trigger_conditions = re.findall(r'call\s+TriggerAddCondition\([^,]+,\s*function\s+(\w+)', content)
    print(f"  触发器条件: {len(trigger_conditions)}")

    # 统计变量定义
    globals = re.findall(r'(?:globals|endglobals)', content, re.IGNORECASE)
    if globals:
        # 提取全局变量
        in_globals = False
        var_count = 0
        for line in lines:
            if 'globals' in line.lower():
                in_globals = True
            elif 'endglobals' in line.lower():
                in_globals = False
            elif in_globals and line.strip() and not line.strip().startswith('//'):
                if 'type' not in line.lower():
                    var_count += 1
        print(f"  全局变量: {var_count}")

    # 统计 API 调用
    print(f"\n" + "=" * 60)
    print("API 调用统计 (按类别):")
    print("=" * 60)

    api_counter = Counter()
    api_by_category = {}

    for category, apis in JASS_API_CATEGORIES.items():
        category_count = 0
        api_by_category[category] = {}

        for api in apis:
            count = content.count(api)
            if count > 0:
                api_counter[api] = count
                category_count += count
                api_by_category[category][api] = count

        if category_count > 0:
            print(f"\n{category}: {category_count} 次")
            sorted_apis = sorted(api_by_category[category].items(), key=lambda x: x[1], reverse=True)
            for api, count in sorted_apis[:10]:  # 只显示前10个
                print(f"    {api}: {count}")

    # Top 20 API
    print(f"\n" + "=" * 60)
    print("Top 20 API 调用:")
    print("=" * 60)
    for i, (api, count) in enumerate(api_counter.most_common(20), 1):
        print(f"  {i:2d}. {api}: {count}")

    # 函数列表
    print(f"\n" + "=" * 60)
    print("函数定义列表:")
    print("=" * 60)
    for name, ret_type in func_defs[:30]:
        print(f"  function {name} returns {ret_type}")
    if len(func_defs) > 30:
        print(f"  ... 还有 {len(func_defs) - 30} 个函数")

    # 触发器动作函数
    if trigger_actions:
        print(f"\n触发器动作函数:")
        for action in set(trigger_actions):
            print(f"  - {action}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python count_api.py <war3map.j>")
        print("示例: python count_api.py extracted/my_map/war3map.j")
        sys.exit(1)

    analyze_jass(sys.argv[1])