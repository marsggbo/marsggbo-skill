#!/usr/bin/env bash
# env.sh — 解析本 skill 的 Python 解释器，跨机器可移植。
#
# 用法：
#   bash <skill_dir>/scripts/env.sh        # 确保 venv 存在，打印解释器绝对路径
#
# 该脚本自己定位所在目录（不依赖任何硬编码的家目录 / .claude / .cursor 路径），
# 因此无论 skill 被放在哪台机器、哪个路径下都能工作。
# 它会：
#   1) 找到 skill 根目录（本脚本的上一级）
#   2) 若 .venv 不存在则用系统 python3 创建，并按 requirements.txt 安装依赖
#   3) 把可用解释器的绝对路径打印到 stdout（其余日志走 stderr）
#
# 约定：调用方拿到 stdout 那一行路径后，在后续所有命令里直接用这个字面路径。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$SKILL_DIR/.venv"
REQ="$SKILL_DIR/requirements.txt"

# 选一个可用的系统 python3 来 bootstrap
sys_py="$(command -v python3 || command -v python || true)"

if [ ! -x "$VENV/bin/python3" ]; then
  if [ -z "$sys_py" ]; then
    echo "ERROR: 系统里找不到 python3，无法创建 venv。请先安装 Python 3。" >&2
    exit 1
  fi
  echo "[env.sh] .venv 不存在，正在创建：$VENV" >&2
  "$sys_py" -m venv "$VENV" >&2
  "$VENV/bin/python3" -m pip install -q --upgrade pip >&2 || true
  if [ -f "$REQ" ]; then
    echo "[env.sh] 安装依赖：$REQ" >&2
    "$VENV/bin/python3" -m pip install -q -r "$REQ" >&2
  fi
fi

# 自检：关键依赖 fitz 是否可用；不行就尝试补装一次
if ! "$VENV/bin/python3" -c "import fitz" >/dev/null 2>&1; then
  echo "[env.sh] 依赖缺失（fitz/PyMuPDF），尝试补装…" >&2
  [ -f "$REQ" ] && "$VENV/bin/python3" -m pip install -q -r "$REQ" >&2 || true
fi

echo "$VENV/bin/python3"
