# Wc3Forge

Warcraft 3 地图开发工具集 - 用于地图的逆向分析、改造与测试。

## 项目概述

Wc3Forge 是一个 WC3 地图开发工具集，提供地图解包、脚本分析、JASS/Lua 转译、回放解析等功能，帮助开发者逆向分析、改造和测试 Warcraft 3 地图。

## 技术栈

### 1. 地图格式与解析

**核心格式：**
- `.w3x` - Warcraft 3 地图文件（MPQ 归档 + 头部）
- `.w3m` - 魔兽世界地图文件
- `.w3g` - Replay 回放文件

**内部文件结构：**
| 文件 | 说明 |
|------|------|
| `war3map.w3i` | 地图元信息（尺寸、版本、作者） |
| `war3map.w3e` | 地形数据（高度、纹理、悬崖） |
| `war3map.w3u` | 单位数据（单位类型） |
| `war3map.w3a` | 技能数据 |
| `war3map.w3t` | 物品数据 |
| `war3map.w3h` | 科技数据 |
| `war3map.w3b` | Buff/效果数据 |
| `war3map.w3d` | Doodad（装饰物）数据 |
| `war3map.w3q` | 升级数据 |
| `war3map.j` | JASS 脚本代码 |
| `war3map.lua` | Lua 脚本代码（Reforged） |
| `war3map.doo` | 地图放置的 doodads |
| `war3mapUnits.doo` | 地图放置的单位 |
| `war3map.wts` | 字符串表 |
| `war3map.shd` | 阴影数据 |
| `war3map.wtg` | 触发器数据 |
| `war3map.wct` | 触发器注释 |

**解析工具与库：**

| 语言 | 库/工具 | 用途 | 安装 |
|------|---------|------|------|
| C# | [War3Net](https://github.com/War3Net) | 地图格式解析、JASS 转 Lua | `dotnet add package War3Net.Build` |
| TypeScript | [war3-model](https://github.com/4eb0da/war3-model) | MDX/MDL 模型解析 | `npm install war3-model` |
| TypeScript | [mdx-m3-viewer](https://github.com/flowtsohg/mdx-m3-viewer) | WebGL 模型查看器 | `npm install mdx-m3-viewer` |
| Java | [Retera's Model Studio](https://github.com/Retera/ReterasModelStudio) | 模型编辑器 | 下载 JAR |
| Python | [w3g](https://git.hubp.de/scopatz/w3g) | Replay 解析 | `pip install w3g` |
| Python | [pympq](https://pypi.org/project/py-mpq/) | MPQ 归档操作 | `pip install pympq` |
| Node.js | [wc3maptranslator](https://www.npmjs.com/package/wc3maptranslator) | 地图文件转换 | `npm install wc3maptranslator` |
| C++ | [wc3lib](https://github.com/tdauth/wc3lib) | 通用格式库 | 编译安装 |

### 2. 脚本语言

**JASS (JASS3):**
- WC3 原始脚本语言
- 官方文档: [Jassbot](https://lep.duckdns.org/jassbot/), [JASS Manual](https://jass.sourceforge.net/doc/)
- 核心文件: `common.j`, `blizzard.j`, `common.ai`

**vJASS:**
- JASS 扩展，支持结构体、命名空间等
- 需 [JassHelper](https://github.com/Acry/CommonJ) 编译

**Lua (Reforged):**
- 1.32+ 版本支持
- 转译工具: [cjass2lua](https://github.com/goshante/cjass2lua), [War3Net.Transpilers](https://www.nuget.org/packages/War3Net.Build)

### 3. 地图编辑工具

| 工具 | 说明 | 平台 |
|------|------|------|
| [YDWE](https://github.com/actboy168/YDWE) | 开源地图编辑器 | Windows |
| [HiveWE](https://github.com/stijnherfst/HiveWE) | 现代 World Editor 替代 | 跨平台 |
| [WurstScript](https://wurstlang.org/) | 高阶语言编译器 | JVM |
| [Better Triggers](https://thelazzoro.github.io/BetterTriggersGuide/) | 外部触发器编辑器 | - |
| [Ladik's MPQ Editor](https://www.hiveworkshop.com/threads/ladiks-mpq-editor.338449/) | MPQ 归档编辑 | Windows |

### 4. 资源转换

**模型转换流程：**
```
MDX/MDL → war3-model / Retera → Blender → glTF
```

**纹理格式：**
- BLP (Battle.net Legacy Texture)
- 转换工具: wc3lib, ImageMagick

### 5. 测试与验证

**自动化测试：**
- Lockstep 确定性验证
- Desync 检测（多客户端状态比对）
- Replay 录制与回放分析

**回放分析工具：**
| 工具 | 语言 | 用途 |
|------|------|------|
| [w3gjs](https://www.skypack.dev/view/w3gjs) | JavaScript | Replay 解析 |
| [W3GNET](https://libraries.io/nuget/W3GNET) | C# | Replay 解析 |
| [warcrumb](https://pkg.go.dev/github.com/efskap/warcrumb) | Go | Replay 解析 |
| [wc3v](https://github.com/jblanchette/wc3v) | TypeScript | Web Replay 查看器 |

**静态分析：**
- JASS 语法检查: pJass / JassHelper
- 触发器依赖分析: War3Net.CodeAnalysis

## 项目结构

```
/home/nx/rpg/
├── maps/                          # 原始地图文件
│   ├── source/                    # 原始 .w3x / .w3m 文件
│   └── backup/                    # 原始文件备份
│
├── extracted/                     # 解压后的地图内容
│   └── {map_name}/                # 按地图名分目录
│       ├── war3map.w3i            # 地图信息
│       ├── war3map.w3e            # 地形数据
│       ├── war3map.w3u            # 单位数据
│       ├── war3map.w3a            # 技能数据
│       ├── war3map.w3t            # 物品数据
│       ├── war3map.j              # JASS脚本
│       └── assets/                # 地图内置资源
│
├── analysis/                      # 分析报告
│   └── {map_name}/
│       ├── summary.md             # 地图概要
│       ├── jass/                  # JASS 脚本分析
│       │   ├── overview.md        # 脚本整体结构
│       │   ├── functions.md       # 函数列表
│       │   └── api_usage.md       # API 调用统计
│       ├── objects/               # 对象数据分析
│       │   ├── units.md
│       │   ├── abilities.md
│       │   └── items.md
│       └── triggers/              # 触发器分析
│
├── converted/                     # 转换后的资源
│   ├── models/                    # glTF/GLB 模型
│   │   ├── units/
│   │   ├── heroes/
│   │   └── effects/
│   ├── textures/                  # 转换后的贴图
│   └── audio/                     # 音频文件
│
├── scripts/                       # 工具脚本
│   ├── extract/
│   │   └── extract_map.py         # 地图解包
│   ├── analyze/
│   │   ├── parse_jass.py          # JASS 解析
│   │   ├── count_api.py           # API 调用统计
│   │   └── gen_dependency.py      # 依赖图生成
│   ├── convert/
│   │   ├── mdx_to_gltf.py         # 模型转换
│   │   └── blp_to_png.py          # 纹理转换
│   ├── transpile/
│   │   └── jass_to_lua.py         # JASS 转 Lua
│   └── test/
│       ├── replay_parse.py        # 回放解析
│       └── desync_check.py        # 同步检测
│
├── tests/                         # 测试用例
│   ├── unit/
│   │   └── jass_test.py           # JASS 函数测试
│   ├── integration/
│   │   └── sync_test.py           # 同步测试
│   └── data/
│       ├── maps/                  # 测试用小地图
│       └── replays/               # 测试用回放
│
├── docs/                          # 文档
│   ├── format_spec.md             # 地图格式规范
│   ├── jass_api.md                # JASS API 参考
│   └── troubleshooting.md         # 问题排查
│
├── config/                        # 配置文件
│   └── settings.yaml              # 全局设置
│
├── sample_map/                    # 示例地图
│   ├── hello_rpg.w3x              # 示例地图文件
│   └── src/                       # 地图源码
│       ├── war3map.j              # 源码
│       └── trigger_data.txt       # 触发器数据
│
├── logs/                          # 运行日志
│   ├── analysis/
│   └── convert/
│
└── temp/                          # 临时文件
    ├── extracted/
    └── cache/
```

## 常用命令

### 地图解包
```bash
# 使用 Python 解包
python scripts/extract/extract_map.py maps/source/my_map.w3x

# 使用 MPQ Editor (GUI)
# Ladik's MPQ Editor → Open → Extract All
```

### 分析 JASS 脚本
```bash
# 统计 API 调用
python scripts/analyze/count_api.py extracted/my_map/war3map.j

# 生成函数依赖
python scripts/analyze/gen_dependency.py extracted/my_map/war3map.j

# 语法检查
pjass extracted/my_map/war3map.j
```

### 资源转换
```bash
# 模型转换
python scripts/convert/mdx_to_gltf.py extracted/my_map/assets/models/hero.mdx

# 纹理转换
python scripts/convert/blp_to_png.py extracted/my_map/assets/textures/
```

### 测试
```bash
# 解析回放
python scripts/test/replay_parse.py tests/data/replays/game.w3g

# 同步检测
python scripts/test/desync_check.py
```

## 开发规范

### 分析阶段
1. 先解包地图，分析内部文件结构
2. 识别地图使用的脚本语言（JASS/vJASS/Lua）
3. 分析对象数据与触发器依赖
4. 生成 API 调用图谱
5. 统计 JASS API 使用频率，优先实现高频 API

### 改造阶段
1. 保持原有架构兼容，非必要不重写
2. 修改前备份原始文件
3. 使用版本控制管理地图变更
4. 遵循 WC3 触发器命名规范

### 测试阶段
1. 单元测试：验证 JASS 函数行为
2. 集成测试：多客户端同步测试
3. Replay 测试：录制并验证回放一致性

## JASS API 优先级（基于 wowr4.6 分析）

### Tier 1: 核心 API (1000+ 调用)
| 函数 | 调用次数 |
|------|---------|
| GetTriggerUnit | 1532 |
| GetTriggerPlayer | 1201 |
| GetOwningPlayer | 781 |

### Tier 2: 高频 API (500-1000)
| 函数 | 调用次数 |
|------|---------|
| h__DisplayTextToForce | 722 |
| GetForceOfPlayer | 710 |
| DisableTrigger | 658 |
| GetConvertedPlayerId | 645 |

### Tier 3: 常用 API (200-500)
| 函数 | 调用次数 |
|------|---------|
| CreateQuestItem | 330 |
| ForForce | 256 |
| DestroyEffectBJ | 248 |
| ForGroupBJ | 203 |

## 参考资源

### 格式规范
- [WC3MapSpecification](https://github.com/ChiefOfGxBxL/WC3MapSpecification) - 地图格式规范
- [XGM: W3M and W3X Files Format](https://xgm.guru/p/wc3/warcraft-3-map-files-format)
- [HiveWE Wiki](https://github-wiki-see.page/m/stijnherfst/HiveWE/wiki) - 各文件格式详解

### JASS 文档
- [Jassbot](https://lep.duckdns.org/jassbot/) - API 搜索
- [JASS Manual](https://jass.sourceforge.net/doc/)
- [Warcraft Wiki: JASS](https://warcraft.wiki.gg/wiki/JASS)

### 社区
- [Hive Workshop](https://www.hiveworkshop.com/) - 地图制作资源
- [WC3 Modding Info Center](https://wc3modding.info/)

### 工具
- [AMAI](https://github.com/SMUnlimited/AMAI) - AI 系统参考
- [WurstScript](https://wurstlang.org/) - 高阶语言

## 注意事项

1. **Lockstep 同步**: WC3 使用确定性 lockstep，改造时必须确保所有客户端状态一致
2. **对象数据**: 使用 SLK/CSV 表格可方便批量修改平衡性数据
3. **Reforged 兼容性**: 1.32+ 版本变化较大，需考虑版本兼容
4. **MPQ 签名**: 部分地图有数字签名，修改后需移除签名