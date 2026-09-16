# BOOTSTRAP — 新会话引导文件（宠物雪碧图生产线）

> 新对话第一动作：读本文件（约 2k token），然后按 §1 最小读取、§3 流程执行。
> 本文件 + `pets/blob_template.py` 即完整契约，**无需读引擎源码/README/全量 HOWTO**。

## 0. 完整性自检（<0.2k token）

```bash
cd /home/user && sha256sum -c MANIFEST.sha256 --quiet && echo FRAMEWORK_OK
```

- `FRAMEWORK_OK` → 继续 §1。
- 文件缺失/损坏 → `python3 -m zipfile -e codex_pet_framework.zip .` 恢复（工作区内备份）后重检。
- 连 zip 也不在（空白环境）→ 请用户上传 `codex_pet_framework.zip` 或提供 git 地址 clone，解压后重检。

## 1. 最小读取清单（合计约 5k token，禁止超读）

1. `BOOTSTRAP.md`（本文件）
2. `pets/blob_template.py`（代码骨架，复制后改写）

## 2. 契约精要（浓缩版）

- 模块接口：`ART_SIZE=(48,52)`；`PALETTE` ≤16 色且必含 `outline`；`ROW_BUILDERS={状态名: fn(n)->[Canvas]}`
- 9 状态（行序由 spec 决定）：idle / running-right / running-left / waving / jumping / failed / waiting / working / review
- 绘制只用 `sprite_engine.core` 图元；`_stamp`=带描边部件，**绘制顺序=遮挡顺序**：尾/附件→脚→身→耳→头→五官贴花→道具→手臂；`_decal`=无描边贴花
- 硬规则：留边≥1px（描边外扩 1px）；≤3px 小部件用 `rect` 禁 `ell`（防十字退化）；`running-left`=右跑帧 `mirror()`；倾斜/突出像素必须并入 `_stamp` 点集（防缺描边）
- 节奏用 `sprite_engine.timing`（table/sine/arc/bounce），8 帧循环首尾衔接
- 道具：working/review 用笔记本（配色可角色主题化）；jumping 用 `arm='up'/'none'` 表达举爪/收臂
- 黑白/高对比角色：控制深色面积（参考 panda_v1 迭代教训：眼斑/肩带过大糊成块）

## 3. 生产流程

```bash
cp specs/v1.json specs/<name>.json        # 改 name/pet/out/preview
cp pets/blob_template.py pets/<name>_v1.py # 改色板/骨架/状态节奏
python3 make_spritesheet.py --spec specs/<name>.json   # 构建+自动校验(尺寸/RGBA/crisp/alpha/bbox/色数)
```

目视协议（省 token 关键）：每轮只看 **半尺寸全图 1 张 + 关键帧 zoom 1 张（4–6 格）**；几何错误优先信 `validate` 断言，不靠眼睛；迭代 ≤2 轮为正常，超 3 轮先查契约硬规则。

## 4. 新会话提示词模板

> 读取 /home/user/BOOTSTRAP.md 并严格执行：附图为形象参考，角色命名 `<name>`。
> 只做最小读取清单；按 §3 构建校验；目视按目视协议；交付 webp+预览+模块文件。

## 5. 换 Key / 换环境 Playbook

| 场景 | 动作 |
|---|---|
| 同账号新对话 | 工作区已持久化：直接 §0 自检后开工，零上传 |
| 新账号/新工作区 | 首会话上传 `codex_pet_framework.zip`（23KB）一次 → 解压 → §0 → 之后持久 |
| 裸 API（无工作区） | 自建持久：私有 git 仓库存框架，会话首命令 clone；或 system prompt 内嵌本文件（~2k）+ 附件 blob_template.py（~3k） |

## 6. 成本基线（单只宠物/会话）

图像 1–2k + 读取 ~5k + 模块输出 4–5k + 构建/校验 ~1k + 目视 4–6k ≈ **15–20k token**；
对比无框架从零写（70–90k）省 4–5 倍；对比每次传 zip 再省 1–3k 且无缺件风险。
