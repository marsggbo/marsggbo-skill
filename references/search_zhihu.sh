#!/usr/bin/env bash
# Grep hexin's scraped Zhihu corpus. Usage: search_zhihu.sh "关键词"
# 一款对知乎三大本地落库产物(大文本 md)进行模糊多行查找的工具

set -e
# 如果用户不传参就报错终止 (-1:? 语法)
KEYWORD="${1:?need keyword}"
DATA_DIR="/Users/hex/hexin-marsggbo-skill/data/zhihu"

# 使用 grep 的 -n 显示行数, -i 忽略大小写
# 抓取每个分类匹配的前若干行，最后加上 || true 确保即便 grep 返回非0值 (没东西) 时不引发 set -e 中断崩溃
echo "=== articles hits (文章查询命中) ==="
grep -n --color=never -i "$KEYWORD" "$DATA_DIR/articles.md" 2>/dev/null | head -40 || true
echo
echo "=== answers hits (回答查询命中) ==="
grep -n --color=never -i "$KEYWORD" "$DATA_DIR/answers.md" 2>/dev/null | head -30 || true
echo
echo "=== pins hits (想法查询命中) ==="
grep -n --color=never -i "$KEYWORD" "$DATA_DIR/pins.md" 2>/dev/null | head -20 || true
