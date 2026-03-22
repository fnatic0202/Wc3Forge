# Wc3Forge - Warcraft 3 地图开发工具集

## 快速开始

### 1. 安装依赖

```bash
# Python 依赖
pip install pympq pillow

# 或者安装所有依赖
pip install -r requirements.txt
```

### 2. 构建示例地图

```bash
cd /home/nx/rpg

# 构建示例地图
python scripts/convert/build_map.py --src sample_map/src --output sample_map/hello_rpg.w3x

# 或使用压缩
python scripts/convert/build_map.py --src sample_map/src --output sample_map/hello_rpg.w3x --compress
```

### 3. 测试地图

将 `sample_map/hello_rpg.w3x` 复制到 Warcraft III 地图目录：
- Classic: `C:\Program Files\Warcraft III\Maps\`
- Reforged: `C:\Program Files (x86)\Warcraft III\_ret_\`

在 WC3 中创建游戏并选择地图测试。

### 4. 分析现有地图

```bash
# 解包地图
python scripts/extract/extract_map.py maps/source/example.w3x

# 分析 JASS 脚本
python scripts/analyze/count_api.py extracted/example/war3map.j
```

## 脚本说明

### scripts/extract/extract_map.py
- 功能：解包 .w3x 地图文件
- 用法：`python extract_map.py <map.w3x> [output_dir]`

### scripts/analyze/count_api.py
- 功能：分析 JASS 脚本，统计 API 调用
- 用法：`python count_api.py <war3map.j>`

### scripts/test/replay_parse.py
- 功能：解析 .w3g 回放文件
- 用法：`python replay_parse.py <replay.w3g>`

### scripts/transpile/jass_to_lua.py
- 功能：JASS 转 Lua
- 用法：`python jass_to_lua.py <input.j> [output.lua]`

### scripts/convert/build_map.py
- 功能：构建 WC3 地图
- 用法：`python build_map.py --src <src_dir> --output <output.w3x>`

## 示例地图

`sample_map/` 目录包含一个简单的 RPG 示例：

- `hello_rpg.w3x` - 编译后的地图文件
- `src/war3map.j` - JASS 源码
- `src/trigger_data.txt` - 触发器数据

### 示例地图功能

1. **创建英雄** - 玩家进入游戏时生成英雄单位
2. **刷怪系统** - 每30秒生成一波敌人
3. **击杀奖励** - 击杀敌人获得金币和经验
4. **宝箱** - 探索地图可开启宝箱获得奖励
5. **死亡重生** - 英雄死亡后自动重生

## 项目结构

```
Wc3Forge/
├── maps/              # 原始地图
│   └── source/        # .w3x 文件
├── extracted/         # 解包后的地图
├── analysis/          # 分析报告
├── converted/         # 转换资源
├── scripts/           # 工具脚本
│   ├── extract/       # 解包
│   ├── analyze/       # 分析
│   ├── convert/       # 转换
│   ├── transpile/     # 转译
│   └── test/          # 测试
├── tests/             # 测试用例
├── sample_map/        # 示例地图
│   ├── hello_rpg.w3x  # 地图文件
│   └── src/           # 源码
├── docs/              # 文档
└── CLAUDE.md          # 本文件
```

## 注意事项

1. 地图文件格式：使用 ZIP 格式的 .w3x
2. 地图需要 JASS 脚本才能运行完整功能
3. 完整地图需要 World Editor 编辑地形