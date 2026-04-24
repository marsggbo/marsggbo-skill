#!/usr/bin/env bash
# Grep hexin's scraped Zhihu corpus. Usage: search_zhihu.sh "关键词"
set -e
KEYWORD="${1:?need keyword}"
DATA_DIR="/Users/hex/marsggbo-skill/data/zhihu"
echo "=== articles hits ==="
grep -n --color=never -i "$KEYWORD" "$DATA_DIR/articles.md" 2>/dev/null | head -40 || true
echo
echo "=== answers hits ==="
grep -n --color=never -i "$KEYWORD" "$DATA_DIR/answers.md" 2>/dev/null | head -30 || true
echo
echo "=== pins hits ==="
grep -n --color=never -i "$KEYWORD" "$DATA_DIR/pins.md" 2>/dev/null | head -20 || true
