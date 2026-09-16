# Codex Pet 像素雪碧图生成框架

> **新会话入口：先读 `BOOTSTRAP.md`**（完整性自检 → 最小读取 → 生产流程 → 提示词模板）。
> 框架完整性校验：`sha256sum -c MANIFEST.sha256 --quiet && echo FRAMEWORK_OK`；
> 工作区内备份：`codex_pet_framework.zip`（空白环境恢复用）；
> 跨平台持久化：`init_workspace.sh` + `docs/GIT_PERSISTENCE.md`（私有 git 正本，一键初始化任意环境）。

程序化生成透明背景像素雪碧图（Sprite Sheet）的三层框架：**工艺层通用、角色层插件化、规格层配置化**。
v1 交付物：`codex_pet_spritesheet.webp`（1536×1872，192×208 单元格，8 列 × 9 行，无损 WebP，全透明背景，无抗锯齿）。

## 目录结构

```
make_spritesheet.py        构建入口 CLI（spec + pet -> webp + 预览 + 校验）
sprite_engine/             工艺层（与角色无关，可复用）
  core.py                    Canvas / 图元(ell,rect,tri,limb,seg2) / stamp(自动描边) / decal / mirror
  sheet.py                   Spec(JSON) / assemble / upscale(NEAREST=关AA) / export_webp / checker_preview / validate
  timing.py                  节奏工具 table / sine / arc / bounce
pets/                      角色层（每宠物一个模块）
  cat_v1.py                  v1 角色：奶油橘虎斑猫（ref uploads/cat.webp），9 状态完整 rig
  panda_v1.py                角色：大熊猫幼崽（ref uploads/panda.png），9 状态完整 rig
  blob_template.py           新宠物模板 + 框架演示角色（果冻 Blob）
specs/                     配置层
  v1.json                    官方 v1 规格：1536x1872 / 192x208 / 8x9 / scale4 / 9 状态行序
  panda_v1.json              熊猫交付规格（几何同 v1）
  blob_demo.json             模板演示规格
docs/HOWTO_new_pet.md      新宠物接入指南（接口契约 + 绘制规则 + 验收清单）
examples/                  模板演示产物（blob_demo_*）
```

## 快速开始

```bash
python3 make_spritesheet.py                          # 猫 v1 -> codex_pet_spritesheet.webp
python3 make_spritesheet.py --spec specs/blob_demo.json   # 模板演示 -> examples/
python3 make_spritesheet.py --pet <module> --spec <spec.json> --out x.webp --preview x.png
```

## 设计要点

- **艺术像素工作流**：角色在 48×52 艺术网格绘制，×4 NEAREST 整数放大 => 像素边缘锐利、天然无抗锯齿。
- **描边即遮挡**：`stamp` 用 8 邻域外描边，后画部件自动切开先画部件 => 内部轮廓线 + 防穿模。
- **姿势参数化 rig**：`BASE` 默认参数 + 每帧覆盖 => 72 帧五官/比例零漂移。
- **镜像复用**：`running-left` = `running-right` 逐帧 `Canvas.mirror()`。
- **交付即校验**：尺寸/RGBA/crisp(NEAREST 往返字节一致)/alpha/逐行 bbox/色数，CLI 失败即非 0 退出。
- **可复现**：同 spec + 同 pet 重跑产物字节一致（v1 重构前后哈希不变）。

## 扩展

- 新宠物：见 `docs/HOWTO_new_pet.md`（复制 `pets/blob_template.py` 起步）。
- 新规格（如 16 列、新状态行）：复制 spec JSON 改几何与 `rows`，角色模块补对应状态构建器即可。
