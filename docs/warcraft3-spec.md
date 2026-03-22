# WC3 地图技术规范文档

本文档详细描述 Warcraft 3 地图的二进制格式、内部文件结构和 JASS API 规范。

---

## 1. 地图文件格式 (.w3x / .w3m)

WC3 地图文件由三部分组成：

```
+------------------+--------------------+--------------------+
|   HM3W 头部      |    MPQ 归档        |  可选签名          |
|   (512 字节)     |   (变长)           |  (NGIS, 256字节)   |
+------------------+--------------------+--------------------+
```

### 1.1 HM3W 头部结构 (512 字节)

| 偏移 | 字段 | 类型 | 大小 | 说明 |
|------|------|------|------|------|
| 0x00 | signature | char[4] | 4 | 固定值 "HM3W" |
| 0x04 | version | uint32 | 4 | 地图版本 |
| 0x08 | map_id | uint32 | 4 | 地图 ID |
| 0x0C | name | char[64] | 64 | 地图名称 (GBK 编码, null 结尾) |
| 0x4C | author | char[64] | 64 | 作者 |
| 0x8C | description | char[128] | 128 | 描述 |
| 0x10C | width | uint16 | 2 | 地图宽度 (tiles) |
| 0x10E | height | uint16 | 2 | 地图高度 (tiles) |
| 0x110 | flags | uint32 | 4 | 标志 |
| ... | ... | ... | ... | ... |
| 0x200 | mpq_offset | uint32 | 4 | MPQ 偏移 (固定 0x200 = 512) |
| 0x204 | mpq_size | uint32 | 4 | MPQ 大小 |

### 1.2 MPQ 归档

从偏移 512 (0x200) 开始是标准 MPQ 归档格式，内部包含以下文件：

| 文件名 | 必选 | 说明 |
|--------|------|------|
| war3map.w3i | ✓ | 地图信息 |
| war3map.w3e | ✓ | 地形数据 |
| war3map.w3u | ✓ | 单位数据 |
| war3map.w3a | ✓ | 技能数据 |
| war3map.w3t | ✓ | 物品数据 |
| war3map.w3h | | 科技数据 |
| war3map.w3b | | Buff 数据 |
| war3map.w3d | | Doodad 数据 |
| war3map.w3q | | 升级数据 |
| war3map.j | ✓ | JASS 脚本 |
| war3map.doo | ✓ | Doodad 放置 |
| war3mapUnits.doo | ✓ | 单位放置 |
| war3map.wts | ✓ | 字符串表 |
| war3map.shd | | 阴影数据 |
| war3map.wtg | | 触发器数据 |
| war3map.wct | | 触发器注释 |

---

## 2. war3map.w3i - 地图信息文件

### 2.1 文件结构

| 偏移 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0x00 | format_version | uint32 | 格式版本 (18=RoC, 25=TFT) |
| 0x04 | map_version | uint32 | 地图版本 |
| 0x08 | editor_version | uint32 | 编辑器版本 |
| 0x0C | name | cstring | 地图名称 |
| ... | author | cstring | 作者 |
| ... | description | cstring | 描述 |
| ... | suggested_players | cstring | 推荐玩家数 |
| ... | camera bounds | float[8] | 相机边界 |
| ... | playable_area | uint32[2] | 可玩区域宽高 |
| 0x? | flags | uint32 | 地图标志 |
| 0x? | tileset | char | 地形类型 (L=Lordaeron, A=Ashenvale...) |
| ... | players | player[] | 玩家数据 |
| ... | forces | force[] | 势力数据 |

### 2.2 format_version 参考

| format_version | 游戏版本 |
|----------------|----------|
| 18 | RoC (Reign of Chaos) |
| 25 | TFT (The Frozen Throne) |
| 28 | 1.31 |
| 31 | 1.32 |
| 33+ | 1.33+ |

### 2.3 地形类型标识 (tileset)

| 字符 | 地形名称 |
|------|----------|
| A | Ashenvale |
| B | Barrens |
| C | Felwood |
| D | Dungeon |
| F | Lordaeron Fall |
| G | Underground |
| L | Lordaeron Summer |
| N | Northrend |
| Q | Village Fall |
| V | Village |
| W | Lordaeron Winter |
| X | Dalaran |
| Y | Cityscape |
| Z | Sunken Ruins |
| I | Icecrown |
| O | Outland |

---

## 3. war3map.w3e - 地形数据文件

### 3.1 文件头 (44 字节 + 可变)

| 偏移 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 0x00 | magic | char[4] | 固定值 "W3E!" |
| 0x04 | version | int32 | 版本 (固定 11) |
| 0x08 | main_tileset | char | 主地形类型 |
| 0x0C | uses_custom | int32 | 1=自定义, 0=预定义 |
| 0x10 | ground_count | int32 | 地面纹理数量 |
| 0x14 | ground_ids | char[4][] | 地面纹理 ID 数组 |
| ... | cliff_count | int32 | 悬崖纹理数量 |
| ... | cliff_ids | char[4][] | 悬崖纹理 ID 数组 |
| ... | width | int32 | 宽度 (+1) |
| ... | height | int32 | 高度 (+1) |
| ... | offset_x | float | 水平偏移 |
| ... | offset_y | float | 垂直偏移 |

### 3.2 Tilepoint 数据 (每个 7 字节)

每个 tilepoint 包含：
- ground_height: int16 (2 字节) - 地面高度 -8192 到 +8192
- water_height + boundary: int16 (2 字节) - 水位 + 边界标志
- flags: 4 bits - ramp, blight, water, boundary
- ground_texture: 4 bits - 地面纹理索引
- cliff_variation: 3 bits - 悬崖变体
- ground_variation: 5 bits - 地面变体
- cliff_texture: 4 bits - 悬崖纹理索引
- layer_height: 4 bits - 层高度

### 3.3 常见纹理 ID

地面纹理:
- "Ldrt" - Lordaeron Summer Dirt
- "Ldrg" - Lordaeron Summer Grass
- "Ldvl" - Lordaeron Summer Village
- "Qdrt" - Village Fall Dirt

悬崖纹理:
- "CLdi" - Cliff Dirt
- "CLgr" - Cliff Grass

---

## 4. JASS 触发器系统 API

### 4.1 核心触发器函数

```jass
// 创建与销毁
native CreateTrigger takes nothing returns trigger
native DestroyTrigger takes trigger whichTrigger returns nothing
native EnableTrigger takes trigger whichTrigger returns nothing
native DisableTrigger takes trigger whichTrigger returns nothing
native IsTriggerEnabled takes trigger whichTrigger returns boolean
native ResetTrigger takes trigger whichTrigger returns nothing

// 执行
native TriggerEvaluate takes trigger whichTrigger returns boolean
native TriggerExecute takes trigger whichTrigger returns nothing
native TriggerExecuteWait takes trigger whichTrigger returns nothing

// 查询
native GetTriggeringTrigger takes nothing returns trigger
native GetTriggerEvalCount takes trigger whichTrigger returns integer
native GetTriggerExecCount takes trigger whichTrigger returns integer
```

### 4.2 条件管理

```jass
native TriggerAddCondition takes trigger whichTrigger, boolexpr condition returns condition
native TriggerRemoveCondition takes trigger whichTrigger, condition whichCondition returns nothing
native TriggerClearConditions takes trigger whichTrigger returns nothing
```

### 4.3 动作管理

```jass
native TriggerAddAction takes trigger whichTrigger, code actionFunc returns action
native TriggerRemoveAction takes trigger whichTrigger, action whichAction returns nothing
native TriggerClearActions takes trigger whichTrigger returns nothing
```

### 4.4 事件注册

```jass
// 游戏事件
native TriggerRegisterGameEvent takes trigger whichTrigger, gameevent whichGameEvent returns event

// 计时器事件
native TriggerRegisterTimerEvent takes trigger whichTrigger, real timeout, boolean periodic returns event
native TriggerRegisterTimerExpireEvent takes trigger whichTrigger, timer whichTimer returns event

// 玩家事件
native TriggerRegisterPlayerEvent takes trigger whichTrigger, player whichPlayer, playerevent whichPlayerEvent returns event
native TriggerRegisterPlayerUnitEvent takes trigger whichTrigger, player whichPlayer, playerunitevent whichPlayerUnitEvent, boolexpr filter returns event

// 单位事件
native TriggerRegisterUnitEvent takes trigger whichTrigger, unit whichUnit, unitevent whichEvent returns event
native TriggerRegisterDeathEvent takes trigger whichTrigger, widget whichWidget returns event
native TriggerRegisterEnterRegion takes trigger whichTrigger, region whichRegion, boolexpr filter returns event
native TriggerRegisterLeaveRegion takes trigger whichTrigger, region whichRegion, boolexpr filter returns event

// 变量事件
native TriggerRegisterVariableEvent takes trigger whichTrigger, string varName, limitop opcode, real limitval returns event

// 玩家聊天事件
native TriggerRegisterPlayerChatEvent takes trigger whichTrigger, player whichPlayer, string chatMessageToDetect, boolean exactMatchOnly returns event
```

### 4.5 常用游戏事件常量

```jass
// 游戏事件
EVENT_GAME_START
EVENT_GAME_END
EVENT_GAME_VICTORY
EVENT_GAME_DEFEAT
EVENT_GAME_TURN_START
EVENT_GAME_TURN_END
EVENT_GAME_LIMIT_EXCEEDED

// 玩家事件
EVENT_PLAYER_STATE_LIMIT
EVENT_PLAYER_ALLIANCE_CHANGED
EVENT_PLAYER_DEFEAT
EVENT_PLAYER_VICTORY
EVENT_PLAYER_CHAT
EVENT_PLAYER_LEAVE
EVENT_PLAYER_UNIT_PICKUP
EVENT_PLAYER_UNIT_DROP

// 单位事件
EVENT_UNIT_DAMAGED
EVENT_UNIT_DEATH
EVENT_UNIT_DECAY
EVENT_UNIT_DETECTED
EVENT_UNIT_HIDDEN
EVENT_UNIT_SELECTED
EVENT_UNIT_TARGET_IN_RANGE
EVENT_UNIT_ATTACKED
EVENT_UNIT_SPELL_CAST
EVENT_UNIT_SPELL_EFFECT
EVENT_UNIT_SPELL_FINISH
EVENT_UNIT_SPELL_CHANNEL
EVENT_UNIT_SPELL_ENDCAST
```

### 4.6 单位操作 API

```jass
// 创建单位
native CreateUnit takes player whichPlayer, integer unitId, real x, real y, real face returns unit
native CreateUnitAtLoc takes player whichPlayer, integer unitId, location whichLocation, real face returns unit
native CreateUnitByName takes player whichPlayer, string unitName, real x, real y, real face returns unit

// 删除单位
native RemoveUnit takes unit whichUnit returns nothing
native KillUnit takes unit whichUnit returns nothing

// 单位属性
native GetUnitX takes unit whichUnit returns real
native GetUnitY takes unit whichUnit returns real
native SetUnitPosition takes unit whichUnit, real x, real y returns nothing
native GetUnitFacing takes unit whichUnit returns real
native SetUnitFacing takes unit whichUnit, real facingAngle returns nothing
native GetUnitMoveSpeed takes unit whichUnit returns real
native SetUnitMoveSpeed takes unit whichUnit, real speed returns nothing
native GetUnitState takes unit whichUnit, unitstate whichUnitState returns real
native SetUnitState takes unit whichUnit, unitstate whichUnitState, real value returns nothing

// 生命值/魔法值
native GetUnitLife takes unit whichUnit returns real
native SetUnitLife takes unit whichUnit, real life returns nothing
native GetUnitMaxLife takes unit whichUnit returns real
native SetUnitMana takes unit whichUnit, real mana returns nothing
native GetUnitMana takes unit whichUnit returns real
native GetUnitMaxMana takes unit whichUnit returns real

// 所属玩家
native GetOwningPlayer takes unit whichUnit returns player

// 单位类型
native GetUnitTypeId takes unit whichUnit returns integer
native GetUnitName takes unit whichUnit returns string

// 显示/隐藏
native ShowUnit takes unit whichUnit, boolean show returns nothing
native SetUnitVisible takes unit whichUnit, boolean visible returns nothing
native IsUnitVisible takes unit whichUnit, player whichPlayer returns boolean

// 技能/物品
native UnitAddAbility takes unit whichUnit, integer abilityId returns boolean
native UnitRemoveAbility takes unit whichUnit, integer abilityId returns boolean
native UnitMakeAbilityPermanent takes unit whichUnit, boolean permanent, integer abilityId returns boolean
native UnitAddItem takes unit whichUnit, item whichItem returns boolean
native UnitRemoveItem takes unit whichUnit, item whichItem returns nothing
```

### 4.7 玩家 API

```jass
native Player takes integer playerNumber returns player
native GetTriggerPlayer takes nothing returns player
native GetOwningPlayer takes unit whichUnit returns player
native GetLocalPlayer takes nothing returns player
native GetConvertedPlayerId takes player whichPlayer returns integer
native GetPlayerId takes player whichPlayer returns integer
native GetPlayerTeam takes player whichPlayer returns integer
native GetPlayerController takes player whichPlayer returns mapcontrol
native GetPlayerRace takes player whichPlayer returns race
native SetPlayerTechResearched takes player whichPlayer, integer techid, integer level returns nothing
native SetPlayerUnitAvailable takes player whichPlayer, integer unitid, boolean avialable returns nothing
```

### 4.8 单位组 API

```jass
native CreateGroup takes nothing returns group
native DestroyGroup takes group whichGroup returns nothing
native GroupAddUnit takes group whichGroup, unit whichUnit returns boolean
native GroupRemoveUnit takes group whichGroup, unit whichUnit returns boolean
native GroupClear takes group whichGroup returns nothing
native GroupEnumUnitsInRect takes group whichGroup, rect r, boolexpr filter returns nothing
native GroupEnumUnitsInRangeOfLoc takes group whichGroup, location whichLocation, real radius, boolexpr filter returns nothing
native ForGroup takes group whichGroup, code callback returns nothing
native FirstOfGroup takes group whichGroup returns unit
```

### 4.9 UI/消息 API

```jass
native DisplayTextToPlayer takes player to, real x, real y, string message returns nothing
native DisplayTimedTextToPlayer takes player to, real x, real y, real duration, string message returns nothing
native DisplayTextToForce takes force to, string message returns nothing
native ClearTextMessages takes nothing returns nothing
native SubText takes string source, integer start, integer end returns string
native GetLocalizedString takes string source returns string
```

### 4.10 特效 API

```jass
native AddSpecialEffect takes string modelName, real x, real y returns effect
native AddSpecialEffectLoc takes string modelName, location whichLocation returns effect
native AddSpecialEffectTarget takes string modelName, unit target, string attachmentPoint returns effect
native DestroyEffect takes effect whichEffect returns nothing
native GetEffectName takes effect whichEffect returns string
```

### 4.11 物品 API

```jass
native CreateItem takes integer itemId, real x, real y returns item
native CreateItemAtLoc takes integer itemId, location whichLocation returns item
native RemoveItem takes item whichItem returns nothing
native GetItemX takes item whichItem returns real
native GetItemY takes item whichItem returns real
native GetItemTypeId takes item whichItem returns integer
native GetItemName takes item whichItem returns string
native SetItemCharges takes item whichItem, integer charges returns nothing
native GetItemCharges takes item whichItem returns integer
```

### 4.12 区域/相机 API

```jass
native GetRectCenter takes rect whichRect returns location
native GetRectMinX takes rect whichRect returns real
native GetRectMaxX takes rect whichRect returns real
native GetRectMinY takes rect whichRect returns real
native GetRectMaxY takes rect whichRect returns real

native SetCameraPosition takes real x, real y returns nothing
native SetCameraTargetController takes unit whichUnit, real x, real y, boolean inheritOrientation returns nothing
native SetCameraField takes camera whichCamera, camerafield whichField, real value, real duration returns nothing
native SetCameraBounds takes real left, real bottom, real right, real top, real left2, real bottom2, real right2, real top2 returns nothing
native ResetCamera takes player whichPlayer returns nothing
```

### 4.13 数学/工具函数

```jass
native GetRandomInt takes integer min, integer max returns integer
native GetRandomReal takes real min, real max returns real
native Sin takes real radians returns real
native Cos takes real radians returns real
native Tan takes real radians returns real
native ASin takes real radians returns real
native ACos takes real radians returns real
native ATan takes real radians returns real
native ATan2 takes real y, real x returns real
native SquareRoot takes real x returns real
native Pow takes real x, real power returns real
native Deg2Rad takes real degrees returns real
native Rad2Deg takes real radians returns real
native I2R takes integer i returns real
native R2I takes real r returns integer
native I2S takes integer i returns string
native S2I takes string s returns integer
native R2S takes real r returns string
native S2R takes string s returns real
```

---

## 5. 触发器结构

WC3 触发器由三部分组成：

### 5.1 事件 (Event)
- 触发器执行的条件
- 示例：单位死亡、玩家聊天、计时器到期

### 5.2 条件 (Condition)
- 返回 boolean 值的表达式
- 所有条件为 AND 关系

### 5.3 动作 (Action)
- 触发后执行的代码
- 顺序执行

### 5.4 典型触发器结构

```jass
// 全局变量
globals
    trigger myTrigger = null
    unit hero = null
endglobals

// 初始化函数
function InitTriggers takes nothing returns nothing
    set myTrigger = CreateTrigger()

    // 注册事件：单位死亡
    call TriggerRegisterAnyUnitEventBJ(myTrigger, EVENT_UNIT_DEATH)

    // 添加条件
    call TriggerAddCondition(myTrigger, Condition(function Trig_Death_Conditions))

    // 添加动作
    call TriggerAddAction(myTrigger, function Trig_Death_Actions)
endfunction

// 条件函数
function Trig_Death_Conditions takes nothing returns boolean
    return GetTriggerUnit() == hero
endfunction

// 动作函数
function Trig_Death_Actions takes nothing returns nothing
    call DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Hero died!")
    // 复活逻辑
endfunction
```

---

## 6. 地图加载流程

1. **读取 HM3W 头部** - 验证签名，获取 MPQ 偏移
2. **打开 MPQ 归档** - 读取内部文件列表
3. **解析 war3map.w3i** - 获取地图信息、玩家数据
4. **解析 war3map.w3e** - 加载地形数据
5. **加载单位/物品** - 从 war3mapUnits.doo 放置单位
6. **执行 war3map.j** - 初始化触发器、创建单位
7. **显示游戏** - 进入游戏循环

---

## 参考资源

- [WC3MapSpecification (GitHub)](https://github.com/ChiefOfGxBxL/WC3MapSpecification)
- [HiveWE Wiki - war3map.w3i](https://github-wiki-see.page/m/stijnherfst/HiveWE/wiki/war3map.w3i---Map-Info)
- [HiveWE Wiki - war3map.w3e](https://github-wiki-see.page/m/stijnherfst/HiveWE/wiki/war3map.w3e-Terrain)
- [Jassbot API Search](https://lep.nrw/jassbot/)
- [JASS Manual](https://jass.sourceforge.net/doc/)
- [XGM: W3M and W3X Files Format](https://xgm.guru/p/wc3/warcraft-3-map-files-format)