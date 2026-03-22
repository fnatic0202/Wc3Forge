# Wc3Forge - WC3 地图开发技术文档

## 目录

1. [地图文件格式](#1-地图文件格式)
2. [内部文件规范](#2-内部文件规范)
3. [JASS API 参考](#3-jass-api-参考)
4. [触发器系统](#4-触发器系统)
5. [已知问题与注意事项](#5-已知问题与注意事项)
6. [参考资源](#6-参考资源)

---

## 1. 地图文件格式

### 1.1 文件结构

WC3 地图文件 (`.w3x` / `.w3m`) 由两部分组成：

```
+------------------+--------------------+
|   HM3W 头部      |    MPQ 归档        |
|   (131072 字节)  |   (从偏移 131072)  |
+------------------+--------------------+
```

**关键发现：**
- HM3W 头部大小是 **131072 字节 (128KB)**，不是 512 字节！
- MPQ 归档从偏移 **131072 (0x20000)** 开始

### 1.2 HM3W 头部结构 (131072 字节)

| 偏移 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0x00 | signature | char[4] | 固定值 "HM3W" |
| 0x04 | version | uint32 | **必须为 0** (不是 1!) |
| 0x08 | map_id | uint32 | 固定值 0x149C0000 |
| 0x10 | name_length | uint32 | 名称长度 |
| 0x14 | unknown | uint32 | 未知 |
| 0x20 | mpq_offset | uint32 | MPQ 偏移 (固定 131072) |
| 0x20 | mpq_size | uint32 | MPQ 大小 |
| 0x20 | name | char[64] | 地图名称 (GBK 编码, 从 offset 32 开始) |
| 0x60 | author | char[64] | 作者 (从 offset 96 开始) |
| 0xA0 | description | char[128] | 描述 (从 offset 160 开始) |
| 0x12C | width | uint16 | 地图宽度 tiles |
| 0x12E | height | uint16 | 地图高度 tiles |
| 0x130 | flags | uint32 | 地图标志 |
| 0x134 | tileset | char | 地形类型 (L=Lordaeron, A=Ashenvale...) |
| ... | ... | ... | ... |

### 1.3 MPQ 归档

从偏移 131072 开始是标准 MPQ 归档，包含以下文件：

| 文件名 | 必选 | 说明 |
|--------|------|------|
| war3map.w3i | ✓ | 地图信息 (format_version=18 for RoC/TFT) |
| war3map.w3e | ✓ | 地形数据 (magic="W3E!", version=11) |
| war3map.w3u | ✓ | 单位数据 |
| war3map.w3a | ✓ | 技能数据 |
| war3map.w3t | ✓ | 物品数据 |
| war3map.j | ✓ | JASS 脚本 |
| war3map.doo | ✓ | Doodad 放置 |
| war3mapUnits.doo | ✓ | 单位放置 |
| war3map.wts | ✓ | 字符串表 |
| war3map.w3h | | 科技数据 |
| war3map.w3b | | Buff 数据 |
| war3map.w3d | | Doodad 数据 |
| war3map.w3q | | 升级数据 |
| war3map.shd | | 阴影数据 |

### 1.4 format_version 参考

| format_version | 游戏版本 |
|----------------|----------|
| 18 | RoC (Reign of Chaos) |
| 25 | TFT (The Frozen Throne) |
| 28 | 1.31 |
| 31 | 1.32 |
| 33+ | 1.33+ |

---

## 2. 内部文件规范

### 2.1 war3map.w3i - 地图信息文件

**文件结构 (format_version=18):**

| 偏移 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0x00 | format_version | uint32 | 18 |
| 0x04 | map_version | uint32 | 地图版本 |
| 0x08 | editor_version | uint32 | 编辑器版本 |
| 0x0C | name | cstring | 地图名称 |
| ... | author | cstring | 作者 |
| ... | description | cstring | 描述 |
| ... | suggested_players | cstring | 推荐玩家数 |
| ... | camera bounds | float[8] | 相机边界 |
| ... | playable_area | uint32[2] | 可玩区域宽高 |
| 0x? | flags | uint32 | 地图标志 |
| 0x? | tileset | char | 地形类型 |
| ... | players | player[] | 玩家数据 (24个) |
| ... | forces | force[] | 势力数据 (16个) |

### 2.2 war3map.w3e - 地形数据文件

**文件头 (44 字节 + 可变):**

| 偏移 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0x00 | magic | char[4] | 固定值 "W3E!" |
| 0x04 | version | int32 | 固定值 11 |
| 0x08 | main_tileset | char | 地形类型 (L=A, B=B...) |
| 0x0C | uses_custom | int32 | 1=自定义, 0=预定义 |
| 0x10 | ground_count | int32 | 地面纹理数量 |
| 0x14 | ground_ids | char[4][] | 地面纹理 ID |
| ... | cliff_count | int32 | 悬崖纹理数量 |
| ... | cliff_ids | char[4][] | 悬崖纹理 ID |
| ... | width | int32 | 宽度 (+1) |
| ... | height | int32 | 高度 (+1) |
| ... | offset_x | float | 水平偏移 |
| ... | offset_y | float | 垂直偏移 |

**Tilepoint 数据 (每个 7 字节):**

- ground_height: int16 (2 字节) - 地面高度
- water_height + boundary: uint16 (2 字节) - bit 15 = boundary flag
- flags + textures: 3 字节

### 2.3 地形纹理 ID

**地面纹理 (Lordaeron Summer):**
- "Ldrg" - Grass
- "Ldrt" - Dirt
- "Ldug" - Grass Dark
- "Ldry" - Dirt Dark

**悬崖纹理:**
- "CLdi" - Cliff Dirt
- "CLgr" - Cliff Grass

---

## 3. JASS API 参考

### 3.1 核心触发器函数

```jass
// 创建与销毁
native CreateTrigger takes nothing returns trigger
native DestroyTrigger takes trigger whichTrigger returns nothing
native EnableTrigger takes trigger whichTrigger returns nothing
native DisableTrigger takes trigger whichTrigger returns nothing
native IsTriggerEnabled takes trigger whichTrigger returns boolean

// 执行
native TriggerEvaluate takes trigger whichTrigger returns boolean
native TriggerExecute takes trigger whichTrigger returns nothing
native GetTriggeringTrigger takes nothing returns trigger
```

### 3.2 条件/动作管理

```jass
native TriggerAddCondition takes trigger whichTrigger, boolexpr condition returns condition
native TriggerClearConditions takes trigger whichTrigger returns nothing
native TriggerAddAction takes trigger whichTrigger, code actionFunc returns action
native TriggerClearActions takes trigger whichTrigger returns nothing
```

### 3.3 事件注册

```jass
native TriggerRegisterGameEvent takes trigger whichTrigger, gameevent whichGameEvent returns event
native TriggerRegisterTimerEvent takes trigger whichTrigger, real timeout, boolean periodic returns event
native TriggerRegisterPlayerEvent takes trigger whichTrigger, player whichPlayer, playerevent whichPlayerEvent returns event
native TriggerRegisterPlayerUnitEvent takes trigger whichTrigger, player whichPlayer, playerunitevent whichPlayerUnitEvent, boolexpr filter returns event
native TriggerRegisterUnitEvent takes trigger whichTrigger, unit whichUnit, unitevent whichEvent returns event
native TriggerRegisterEnterRegion takes trigger whichTrigger, region whichRegion, boolexpr filter returns event
native TriggerRegisterDeathEvent takes trigger whichTrigger, widget whichWidget returns event
native TriggerRegisterPlayerChatEvent takes trigger whichTrigger, player whichPlayer, string chatMessageToDetect, boolean exactMatchOnly returns event
```

### 3.4 单位操作

```jass
native CreateUnit takes player whichPlayer, integer unitId, real x, real y, real face returns unit
native CreateUnitAtLoc takes player whichPlayer, integer unitId, location whichLocation, real face returns unit
native RemoveUnit takes unit whichUnit returns nothing
native KillUnit takes unit whichUnit returns nothing
native GetUnitX takes unit whichUnit returns real
native GetUnitY takes unit whichUnit returns real
native SetUnitPosition takes unit whichUnit, real x, real y returns nothing
native GetUnitLife takes unit whichUnit returns real
native SetUnitLife takes unit whichUnit, real life returns nothing
native GetUnitMana takes unit whichUnit returns real
native SetUnitMana takes unit whichUnit, real mana returns nothing
native GetOwningPlayer takes unit whichUnit returns player
native GetUnitTypeId takes unit whichUnit returns integer
native UnitAddAbility takes unit whichUnit, integer abilityId returns boolean
native UnitRemoveAbility takes unit whichUnit, integer abilityId returns boolean
```

### 3.5 玩家操作

```jass
native Player takes integer playerNumber returns player
native GetTriggerPlayer takes nothing returns player
native GetLocalPlayer takes nothing returns player
native GetConvertedPlayerId takes player whichPlayer returns integer
native GetPlayerId takes player whichPlayer returns integer
native GetPlayerTeam takes player whichPlayer returns integer
native SetPlayerTechResearched takes player whichPlayer, integer techid, integer level returns nothing
```

### 3.6 单位组操作

```jass
native CreateGroup takes nothing returns group
native DestroyGroup takes group whichGroup returns nothing
native GroupAddUnit takes group whichGroup, unit whichUnit returns boolean
native GroupRemoveUnit takes group whichGroup, unit whichUnit returns boolean
native GroupEnumUnitsInRect takes group whichGroup, rect r, boolexpr filter returns nothing
native ForGroup takes group whichGroup, code callback returns nothing
native FirstOfGroup takes group whichGroup returns unit
```

### 3.7 UI/消息

```jass
native DisplayTextToPlayer takes player to, real x, real y, string message returns nothing
native DisplayTimedTextToPlayer takes player to, real x, real y, real duration, string message returns nothing
native DisplayTextToForce takes force to, string message returns nothing
native ClearTextMessages takes nothing returns nothing
```

### 3.8 特效

```jass
native AddSpecialEffect takes string modelName, real x, real y returns effect
native AddSpecialEffectLoc takes string modelName, location whichLocation returns effect
native AddSpecialEffectTarget takes string modelName, unit target, string attachmentPoint returns effect
native DestroyEffect takes effect whichEffect returns nothing
```

### 3.9 物品

```jass
native CreateItem takes integer itemId, real x, real y returns item
native CreateItemAtLoc takes integer itemId, location whichLocation returns item
native RemoveItem takes item whichItem returns nothing
native GetItemX takes item whichItem returns real
native GetItemY takes item whichItem returns real
```

### 3.10 相机

```jass
native SetCameraPosition takes real x, real y returns nothing
native SetCameraTargetController takes unit whichUnit, real x, real y, boolean inheritOrientation returns nothing
native SetCameraBounds takes real left, real bottom, real right, real top returns nothing
```

---

## 4. 触发器系统

### 4.1 触发器结构

```jass
// 1. 创建触发器
set myTrigger = CreateTrigger()

// 2. 注册事件
call TriggerRegisterGameEvent(myTrigger, EVENT_GAME_START)
call TriggerRegisterPlayerUnitEvent(myTrigger, Player(0), EVENT_UNIT_DEATH, null)

// 3. 添加条件 (可选)
call TriggerAddCondition(myTrigger, Condition(function MyConditions))

// 4. 添加动作
call TriggerAddAction(myTrigger, function MyActions)

// 5. 启用/禁用
call EnableTrigger(myTrigger)
// 或
call DisableTrigger(myTrigger)
```

### 4.2 事件常量

**游戏事件:**
- EVENT_GAME_START
- EVENT_GAME_END
- EVENT_GAME_VICTORY
- EVENT_GAME_DEFEAT

**玩家事件:**
- EVENT_PLAYER_DEFEAT
- EVENT_PLAYER_VICTORY
- EVENT_PLAYER_CHAT
- EVENT_PLAYER_LEAVE

**单位事件:**
- EVENT_UNIT_DAMAGED
- EVENT_UNIT_DEATH
- EVENT_UNIT_SELECTED
- EVENT_UNIT_ATTACKED
- EVENT_UNIT_SPELL_CAST
- EVENT_UNIT_SPELL_EFFECT

---

## 5. 已知问题与注意事项

### 5.1 关键发现

1. **HM3W 头部大小**: 必须是 **131072 字节 (128KB)**，不是 512 字节！
2. **MPQ 偏移**: 从 **131072 (0x20000)** 开始
3. **版本号**: HM3W 头部的 version 字段必须为 **0**
4. **地图 ID**: 固定值 0x149C0000

### 5.2 常见问题

- 地图显示 "地图损毁": HM3W 头部格式不正确
- 地图列表不显示: MPQ 偏移或大小错误
- JASS 不执行: war3map.j 格式或编码问题

### 5.3 调试建议

1. 使用十六进制编辑器对比官方地图
2. 检查 HM3W 签名 (0x00-0x03)
3. 验证 MPQ 偏移 (0x14-0x17)
4. 确认版本号为 0

---

## 6. 参考资源

### 官方文档
- [WC3MapSpecification (GitHub)](https://github.com/ChiefOfGxBxL/WC3MapSpecification)
- [HiveWE Wiki - war3map.w3i](https://github-wiki-see.page/m/stijnherfst/HiveWE/wiki/war3map.w3i---Map-Info)
- [HiveWE Wiki - war3map.w3e](https://github-wiki-see.page/m/stijnherfst/HiveWE/wiki/war3map.w3e-Terrain)

### JASS 参考
- [Jassbot API Search](https://lep.nrw/jassbot/)
- [JASS Manual](https://jass.sourceforge.net/doc/)

### 工具
- [War3Net](https://github.com/War3Net) - C# 地图解析库
- [wc3maptranslator](https://github.com/ChiefOfGxBxL/wc3maptranslator) - 地图转换工具

---

*本文档将持续更新...*
*最后更新: 2026-03-23*