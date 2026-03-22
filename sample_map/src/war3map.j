//================================================================================
// Hello RPG - 简单的 WC3 RPG 示例地图
// 作者: RPG Project
// 版本: 1.0
//================================================================================

//============================================================================
// 全局变量
//============================================================================
globals
    // 玩家
    player user = null
    player neutral = Player(PLAYER_NEUTRAL_AGGRESSIVE)

    // 单位
    unit hero = null
    unit spawner = null
    unit chest = null

    // 触发器
    trigger game_start_trigger = null
    trigger hero_death_trigger = null
    trigger chest_trigger = null
    trigger spawn_trigger = null
    trigger timer_trigger = null

    // 计时器
    timer game_timer = null
    timer spawn_timer = null

    // 单位组
    group enemy_group = null

    // 区域
    rect spawn_area = null
    rect chest_area = null

    // 游戏状态
    integer gold = 0
    integer kill_count = 0
    real game_time = 0.0

    // 常量
    constant integer HERO_CLASS_ID = 'H001'  // 英雄单位类型
    constant integer ENEMY_CLASS_ID = 'u000' // 敌人单位类型
    constant integer CHEST_ITEM_ID = 'I000'  // 宝箱物品
    constant integer GOLD_ITEM_ID = 'I001'   // 金币物品
endglobals

//============================================================================
// 函数库
//============================================================================

// 显示消息给玩家
function ShowMessage takes string msg, real duration returns nothing
    call DisplayTimedTextToPlayer(user, 0, 0, duration, msg)
endfunction

// 创建敌人
function CreateEnemy takes real x, real y returns unit
    local unit u = CreateUnit(neutral, ENEMY_CLASS_ID, x, y, 0)
    call SetUnitState(u, UNIT_STATE_LIFE, 500.0)
    call SetUnitState(u, UNIT_STATE_MAX_LIFE, 500.0)
    call GroupAddUnit(enemy_group, u)
    return u
endfunction

// 生成波次敌人
function SpawnWave takes integer wave returns nothing
    local integer i = 0
    local real base_x = -5000.0
    local real base_y = 0.0

    // 根据波次调整难度
    local integer count = 3 + wave * 2

    loop
        exitwhen i >= count
        call CreateEnemy(base_x + i * 150, base_y + GetRandomReal(-200, 200))
        set i = i + 1
    endloop

    call ShowMessage("|cffffcc00波次 " + I2S(wave) + " 来袭!|r", 5.0)
endfunction

// 检查敌人是否全部死亡
function CheckWaveComplete returns boolean
    return CountUnitsInGroup(enemy_group) == 0
endfunction

// 奖励玩家
function RewardPlayer takes integer gold_amount, integer xp_amount returns nothing
    set gold = gold + gold_amount
    call ShowMessage("获得 " + I2S(gold_amount) + " 金币!", 3.0)

    // 简单升级逻辑
    if kill_count >= 10 and GetUnitLevel(hero) < 2 then
        call SelectHeroSkill(hero, 'A000')
        call ShowMessage("英雄升级到 2 级!", 5.0)
    endif
endfunction

//============================================================================
// 触发器条件
//============================================================================

function Trig_Game_Start_Conditions takes nothing returns boolean
    return true
endfunction

function Trig_Hero_Death_Conditions takes nothing returns boolean
    return GetTriggerUnit() == hero
endfunction

function Trig_Chest_Trigger_Conditions takes nothing returns boolean
    return GetTriggerUnit() == hero and GetRectChosenCharacter(chest_area) == hero
endfunction

function Trig_Spawn_Conditions takes nothing returns boolean
    return CheckWaveComplete()
endfunction

//============================================================================
// 触发器动作
//============================================================================

function Trig_Game_Start_Actions takes nothing returns nothing
    // 初始化游戏状态
    set gold = 0
    set kill_count = 0
    set game_time = 0.0

    // 创建玩家英雄
    set hero = CreateUnit(user, HERO_CLASS_ID, 0, 0, 0)
    call SetUnitPosition(hero, 0, 0)
    call SetHeroLevel(hero, 1, true)
    call SetUnitState(hero, UNIT_STATE_LIFE, 1000.0)
    call SetUnitState(hero, UNIT_STATE_MAX_LIFE, 1000.0)

    // 创建刷怪点
    set spawner = CreateUnit(neutral, 'n001', -5000, 0, 0)

    // 创建宝箱
    set chest = CreateUnit(neutral, 'n002', 2000, 0, 0)

    // 设置相机
    call SetCameraPosition(0, 0)
    call SetCameraBoundToRect(spawn_area)

    // 显示欢迎消息
    call DisplayTextToPlayer(user, 0, 0, "|cffffcc00=== 欢迎来到 Hello RPG ===|r")
    call DisplayTextToPlayer(user, 0, 0, "|cff00ff00击败敌人获得金币和经验!|r")
    call DisplayTextToPlayer(user, 0, 0, "|cff00ffff探索地图寻找宝箱!|r")

    // 启动刷怪计时器
    call TimerStart(spawn_timer, 30.0, true, null)

    // 启动游戏计时器
    call TimerStart(game_timer, 1.0, true, null)

    call ShowMessage("游戏开始!", 5.0)
endfunction

function Trig_Hero_Death_Actions takes nothing returns nothing
    call ShowMessage("|cffff0000英雄死亡! 3秒后重生...|r", 5.0)
    call PauseUnit(hero, true)
    call SetUnitPosition(hero, 0, 0)
    call SetUnitState(hero, UNIT_STATE_LIFE, 500.0)
    call TimerStart(CreateTimer(), 3.0, false, null)
    // 实际重生逻辑需要额外处理
endfunction

function Trig_Chest_Trigger_Actions takes nothing returns nothing
    // 打开宝箱
    call ShowMessage("|cffffcc00你发现了宝箱!|r", 5.0)
    call CreateItem(GOLD_ITEM_ID, GetUnitX(chest), GetUnitY(chest))
    call CreateItem(GOLD_ITEM_ID, GetUnitX(chest), GetUnitY(chest) + 50)
    call CreateItem(GOLD_ITEM_ID, GetUnitX(chest), GetUnitY(chest) + 100)
    call KillUnit(chest)
endfunction

function Trig_Spawn_Actions takes nothing returns nothing
    static integer wave = 0
    set wave = wave + 1
    call SpawnWave(wave)
endfunction

function Trig_Timer_Actions takes nothing returns nothing
    set game_time = game_time + 1.0

    // 每分钟显示游戏时间
    if ModuloInteger(R2I(game_time), 60) == 0 then
        call ShowMessage("游戏时间: " + I2S(R2I(game_time / 60)) + " 分钟", 3.0)
    endif
endfunction

function Trig_Enemy_Death_Actions takes nothing returns nothing
    local unit dying = GetDyingUnit()
    local unit killer = GetKillingUnit()

    // 只有英雄击杀才奖励
    if killer == hero then
        set kill_count = kill_count + 1
        call RewardPlayer(10, 50)

        // 掉落物品 (25% 几率)
        if GetRandomInt(1, 100) <= 25 then
            call CreateItem(GOLD_ITEM_ID, GetUnitX(dying), GetUnitY(dying))
        endif
    endif

    // 清理
    call GroupRemoveUnit(enemy_group, dying)
    call RemoveUnit(dying)
endfunction

//============================================================================
// 触发器初始化
//============================================================================

function InitTriggers takes nothing returns nothing
    // 游戏开始触发器
    set game_start_trigger = CreateTrigger()
    call TriggerRegisterGameEvent(game_start_trigger, EVENT_GAME_START)
    call TriggerAddCondition(game_start_trigger, Condition(function Trig_Game_Start_Conditions))
    call TriggerAddAction(game_start_trigger, function Trig_Game_Start_Actions)

    // 英雄死亡触发器
    set hero_death_trigger = CreateTrigger()
    call TriggerRegisterUnitEvent(hero_death_trigger, hero, EVENT_UNIT_DEATH)
    call TriggerAddCondition(hero_death_trigger, Condition(function Trig_Hero_Death_Conditions))
    call TriggerAddAction(hero_death_trigger, function Trig_Hero_Death_Actions)

    // 宝箱触发器
    set chest_trigger = CreateTrigger()
    call TriggerRegisterEnterRectSimple(chest_trigger, chest_area)
    call TriggerAddCondition(chest_trigger, Condition(function Trig_Chest_Trigger_Conditions))
    call TriggerAddAction(chest_trigger, function Trig_Chest_Trigger_Actions)

    // 敌人死亡触发器
    set trigger enemy_death = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(enemy_death, EVENT_UNIT_DEATH)
    call TriggerAddAction(enemy_death, function Trig_Enemy_Death_Actions)
endfunction

//============================================================================
// 初始化
//============================================================================

function InitGlobals takes nothing returns nothing
    // 初始化玩家
    set user = Player(0)

    // 初始化计时器
    set game_timer = CreateTimer()
    set spawn_timer = CreateTimer()

    // 初始化单位组
    set enemy_group = CreateGroup()

    // 初始化区域
    set spawn_area = Rect(-6000, -500, -4000, 500)
    set chest_area = Rect(1500, -200, 2500, 200)
endfunction

//============================================================================
// 主入口
//============================================================================

function main takes nothing returns nothing
    // 初始化全局变量
    call InitGlobals()

    // 设置地图配置
    call SetMapName("Hello RPG")
    call SetMapDescription("一个简单的 RPG 示例地图")
    call SetPlayers(1)
    call SetTeams(1)

    // 配置玩家
    call SetPlayerStartLocation(user, 0)
    call SetPlayerColor(user, PLAYER_COLOR_RED)
    call SetPlayerRacePreference(user, RACE_PREF_HUMAN)

    // 配置地图地形
    // (实际地形数据需要在 World Editor 中设置)

    // 初始化触发器
    call InitTriggers()

    // 设置视角
    call SetCameraBounds(-8000, -6000, 8000, 6000, -4000, -3000, 4000, 3000)
    call SetCameraPosition(0, 0)
endfunction

//============================================================================
// 配置文件头 (WC3 标准)
//============================================================================

// 地图配置
//========================================
// map_name: Hello RPG
// map_author: RPG Project
// map_version: 1.0
//========================================