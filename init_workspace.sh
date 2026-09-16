#!/usr/bin/env bash
# init_workspace.sh — 把任意空白环境初始化为 Codex Pet 雪碧图生产线
#
# 用法（三模式）:
#   bash init_workspace.sh <私有git仓库url> [目标目录]        # 有 git: clone + 校验 + 依赖 + 冒烟
#   bash init_workspace.sh --zip <框架zip路径> [目标目录]     # 无 git: zip 恢复 + 校验 + 依赖 + 冒烟
#   bash init_workspace.sh --here                            # 框架已在当前目录(如刚 git clone / unzip 过):
#                                                            #   仅 校验 + 依赖 + 冒烟
# 说明: 本脚本本身住在仓库/zip 内; 空白环境的"种子"只需一条 git clone / curl / 一次 zip 附件,
#       种子落地后由本脚本完成剩余初始化(--here 模式)。
set -euo pipefail

TARGET_DEFAULT="codex_pet_workspace"

usage() { sed -n '2,9p' "$0"; exit 1; }
[ $# -ge 1 ] || usage

MODE=""; SRC=""; TARGET=""
case "$1" in
  --here) MODE=here; TARGET="." ;;
  --zip)  MODE=zip; SRC="${2:?缺少 zip 路径}"; TARGET="${3:-$TARGET_DEFAULT}" ;;
  -h|--help) usage ;;
  *)      MODE=git; SRC="$1"; TARGET="${2:-$TARGET_DEFAULT}" ;;
esac

echo "== [1/4] 获取框架 ($MODE) -> $TARGET"
if [ "$MODE" = "here" ]; then
  cd "$TARGET"
  [ -f MANIFEST.sha256 ] || { echo "NOT_FRAMEWORK_ROOT: 当前目录缺少 MANIFEST.sha256"; exit 1; }
elif [ "$MODE" = "git" ]; then
  mkdir -p "$TARGET"
  git clone --depth 1 "$SRC" "$TARGET"
  cd "$TARGET"
else
  mkdir -p "$TARGET"
  TMP="$(mktemp -d)"
  python3 - "$SRC" "$TMP" <<'PY'
import sys, zipfile
zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])
PY
  INNER="$TMP/codex_pet_framework"
  [ -d "$INNER" ] || INNER="$TMP"
  cp -a "$INNER/." "$TARGET/"
  rm -rf "$TMP"
  cd "$TARGET"
fi

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
