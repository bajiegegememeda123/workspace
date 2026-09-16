#!/usr/bin/env bash
# init_workspace.sh — 把任意空白环境一键初始化为 Codex Pet 雪碧图生产线
#
# 用法（二选一）:
#   bash init_workspace.sh <私有git仓库url> [目标目录]      # 有网络: clone 正本
#   bash init_workspace.sh --zip <框架zip路径> [目标目录]   # 无网络/无git: zip 恢复
#
# 自动步骤: 获取框架 -> MANIFEST 完整性校验 -> 依赖检查/安装 -> 冒烟构建+校验 -> 打印 READY
set -euo pipefail

TARGET_DEFAULT="codex_pet_workspace"

usage() { sed -n '2,10p' "$0"; exit 1; }
[ $# -ge 1 ] || usage

MODE="" SRC="" TARGET=""
if [ "$1" = "--zip" ]; then
  MODE="zip"; SRC="${2:?缺少 zip 路径}"; TARGET="${3:-$TARGET_DEFAULT}"
else
  MODE="git"; SRC="$1"; TARGET="${2:-$TARGET_DEFAULT}"
fi

echo "== [1/4] 获取框架 ($MODE) -> $TARGET"
mkdir -p "$TARGET"
if [ "$MODE" = "git" ]; then
  git clone --depth 1 "$SRC" "$TARGET"
else
  TMP="$(mktemp -d)"
  python3 - "$SRC" "$TMP" <<'PY'
import sys, zipfile
zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])
PY
  # zip 内有一层 codex_pet_framework/ 前缀，剥离后移入 TARGET
  INNER="$TMP/codex_pet_framework"
  [ -d "$INNER" ] || INNER="$TMP"
  cp -a "$INNER/." "$TARGET/"
  rm -rf "$TMP"
fi

cd "$TARGET"

echo "== [2/4] 完整性校验"
sha256sum -c MANIFEST.sha256 --quiet && echo "FRAMEWORK_OK" || { echo "FRAMEWORK_CORRUPT"; exit 1; }

echo "== [3/4] 依赖检查/安装"
if python3 -c "import PIL" 2>/dev/null; then
  echo "Pillow 已安装，跳过 pip"
else
  python3 -m pip install -r requirements.txt
fi

echo "== [4/4] 冒烟构建（blob 演示 + 自动校验）"
python3 make_spritesheet.py --spec specs/blob_demo.json | grep -E "VALIDATION|sheet size"

echo
echo "READY ✔  生产线就绪于: $(pwd)"
echo "下一步: 阅读 BOOTSTRAP.md §1-§3；新会话提示词模板见 BOOTSTRAP.md §4"
