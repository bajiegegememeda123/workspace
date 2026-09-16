# 新宠物接入指南（Codex Pet 雪碧图框架）

框架三层：

```
sprite_engine/   工艺层（通用，勿改）：画布/图元/描边/拼表/放大/导出/校验/节奏工具
pets/            角色层（每宠物一个模块）：色板 + 骨架 rig + 9 个状态行构建器
specs/           配置层（每交付一个 JSON）：画布/格子/网格/放大倍数/行-状态绑定/输出路径
make_spritesheet.py   构建入口 CLI
```

## 一、宠物模块接口契约

新建 `pets/<name>_v1.py`（可直接复制 `pets/blob_template.py`），必须提供：

| 成员 | 类型 | 说明 |
|---|---|---|
| `ART_SIZE` | `(w, h)` | 艺术像素单帧尺寸，必须等于 `spec.cell // spec.scale`（v1 规格为 48×52） |
| `PALETTE` | dict | 角色色板，值 `(r,g,b,255)`；建议 ≤16 色；**必须含 `outline` 描边色** |
| `ROW_BUILDERS` | dict | `{状态名: fn(n_frames) -> [Canvas]}`，覆盖 spec.rows 全部状态 |

状态词汇 v1（9 个，行序由 spec 决定）：
`idle / running-right / running-left / waving / jumping / failed / waiting / working / review`

## 二、绘制规则（保证风格统一与规格合规）

1. 只用 `sprite_engine.core` 的图元（`ell/rect/tri/limb/seg2`）+ `_stamp`（带描边部件）/`_decal`（无描边贴花）。
2. **描边顺序即遮挡顺序**：后 `_stamp` 的部件用描边切开先画者 => 天然防穿模。推荐顺序：尾/附件 → 脚 → 身 → 耳 → 头 → 五官贴花 → 道具(笔记本) → 手臂。
3. **留边 ≥1 艺术像素**：描边会外扩 1px，任何填充不得贴格子边（校验会查每行 bbox）。
4. 小部件（≤3px）**不要用 `ell`**（小半径椭圆退化为十字形），用 `rect`。
5. 节奏用 `sprite_engine.timing`（`table/sine/arc/bounce`）生成，8 帧一循环；`running-left` 直接 `canvas.mirror()` 右跑帧。
6. 比例一致性：把骨架基准写进 `BASE` 字典（姿势参数默认值），所有状态只改参数不改几何。

## 三、交付流程

```bash
# 1) 写角色模块
cp pets/blob_template.py pets/<name>_v1.py   # 改色板/骨架/状态

# 2) 写规格（几何不变时只改 name/pet/out/preview）
cp specs/blob_demo.json specs/<name>.json

# 3) 构建 + 自动校验
python3 make_spritesheet.py --spec specs/<name>.json

# 4) 目视迭代：打开预览图看透明区与动作；改角色模块重跑
#    （放大单帧检查：可用 PIL crop 单元格 resize NEAREST 看细节）
```

校验自动执行（`sprite_engine.sheet.validate`）：
尺寸=spec、RGBA、**crisp**（NEAREST 往返字节一致=无抗锯齿）、**alpha**（含全透明与不透明）、
**每行 bbox 落在单元格内**、色数统计。任一失败 CLI 返回非 0。

## 四、验收自查清单

- [ ] 9 行状态语义与 spec.rows 一一对应，行序未调换
- [ ] 8 帧循环首尾衔接（第 8 帧 → 第 1 帧无跳变）
- [ ] 角色五官/比例全 72 帧一致；无部件悬空/错位
- [ ] 背景全透明、无多余装饰像素
- [ ] 预览图目视：动作节奏自然（呼吸/步态/挥爪幅度适中）
- [ ] CLI 打印 `VALIDATION OK`
