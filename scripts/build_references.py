#!/usr/bin/env python3
"""Distill scraped Zhihu content into SKILL reference files for hexin-marsggbo.
(解析抓取到的知乎内容，提炼总结为 hexin-marsggbo 个人风格库中的核心参考文件)

本脚本将遍历读取解析完毕的知乎文章/想法/回答全集数据。
通过各种规则提取其高价值部分（比如高赞回答，带有指定技术圈圈关键词的笔记等），
生成用于大模型 (LLM) “性格/能力”系统 Prompt 使用的上下文附带文档技能树 (Skill References)。

Produces (生成以下文件到 ~/.claude/skills/hexin/references/):
  writing_style_examples.md — representative openings & paragraphs (写作风格样本：包含极具代表性的高赞开场白提取)
  core_views.md             — key takes organized by theme (核心观点库：按自然语言关键词匹配归类的特定领域主题聚合)
  title_index.md            — browsable index by year (全量内容索引标题：用于人工检查或让 AI 掌握时间线概念的模型目录库)
  search_zhihu.sh           — grep helper script (基于 grep 的语料内容检索工具脚本：供大模型运行时调用查询原话)

-- Forked from https://github.com/floodsung/floodsung-skill --
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# Project root = parent of scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / "data" / "zhihu"
SKILL_DIR = Path.home() / ".claude" / "skills" / "hexin"
REF = SKILL_DIR / "references"
REF.mkdir(parents=True, exist_ok=True)


def load(name: str) -> list[dict]:
    # 通用加载器：从本地读取由前序抓取步骤（scraper.py / enrich.py）产出的完整 JSON 数据集
    path = DATA / f"{name}.json"
    if not path.exists():
        print(f"  WARNING: {path} not found, skipping")
        return []
    # 返回反序列化后的列表结构
    return json.loads(path.read_text(encoding="utf-8"))


def year(ts: int | None) -> str:
    # 辅助时间函数：将毫秒/秒级 UNIX 时间戳转换为人类和系统可读的 YYYY-MM 月度字符串
    if not ts:
        return "?"
    try:
        # 使用系统 API 抛弃天和具体时分秒精度，仅仅保留年份和月份跨度，用于月报聚合
        return datetime.fromtimestamp(ts).strftime("%Y-%m")
    except Exception:
        return "?"


def first_paragraph(md: str, max_chars: int = 600) -> str:
    # NLP 片段切割器：为了防止上下文 Token 爆炸，我们只需要抽取长长文章的“开头段落”。
    # 它反映了写作者破题、引入的最核心原始笔法（文风，起手式等）。
    if not md:
        return ""
    # 用正则表达式粗暴剔除掉所有的 Markdown 格式的图片插入节点，因为它们占用字符且包含乱码信息
    md = re.sub(r"!\[.*?\]\(.*?\)", "", md)
    # 收缩多余的换行符
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    
    parts = md.split("\n\n")
    out = []
    total = 0
    # 遍历段落拼接，直到超过设定的字符截断安全水位线 (默认 600 字符)
    for p in parts:
        if total + len(p) > max_chars:
            break
        out.append(p)
        total += len(p)
    return "\n\n".join(out).strip()


def build_style_examples(articles: list[dict], pins: list[dict], answers: list[dict]):
    # 第一篇聚合文件生成器 (writing_style_examples.md)
    # 这份文件的核心作用是教 AI “如何模仿该作者的语气以及起承转合的文字结构”
    # 我们认为“高赞”的数据更具有代表性和高质量，因此选取赞数排名最靠前的来做样板。
    
    # 获取最高赞专栏文章 Top 12 (过滤掉没有填充内容的)
    top_articles = sorted(
        [a for a in articles if a.get("content_md")],
        key=lambda a: -(a.get("voteup_count") or 0),
    )[:12]

    # 获取高赞的详细大段解答回答 Top 8 (筛选长度大于 500 字，避免筛选到一两句的抖机灵抖包袱短引流)
    top_answers = sorted(
        [a for a in answers if a.get("content_md") and len(a["content_md"]) > 500],
        key=lambda a: -(a.get("voteup_count") or 0),
    )[:8]

    # 获取稍微有些营养的想法/动态帖子 Top 15 (大于80词)
    sample_pins = [p for p in pins if len(p.get("text", "")) > 80][:15]

    # 初始化 markdown 文档抬头并写好让 AI 注意阅读理解的 Prompt 前调指引
    lines = ["# hexin 风格样本\n",
             "精选高赞文章开头、代表性回答与想法片段。模仿写作风格时请对照语气、句式、转折方式。\n"]

    lines.append("\n## 一、文章开头样本（高赞，按得票排序）\n")
    for a in top_articles:
        lines.append(f"\n### 《{a['title']}》  \n")
        lines.append(f"*{year(a.get('created'))} · {a.get('voteup_count', 0)} 赞 · {a['url']}*\n")
        # 只要前 500 个字母作为片段注入，避免全文输入带来的噪音
        lines.append("\n```text\n" + first_paragraph(a["content_md"], 500) + "\n```\n")

    lines.append("\n## 二、代表性回答摘录\n")
    for a in top_answers:
        lines.append(f"\n### 问：{a['question']}  \n")
        lines.append(f"*{year(a.get('created'))} · {a.get('voteup_count', 0)} 赞*\n")
        lines.append("\n```text\n" + first_paragraph(a["content_md"], 500) + "\n```\n")

    lines.append("\n## 三、知乎想法样本（短动态）\n")
    for p in sample_pins:
        lines.append(f"- ({year(p.get('created'))}) {p['text'][:220]}")

    out = REF / "writing_style_examples.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}: {len(top_articles)} articles + {len(top_answers)} answers + {len(sample_pins)} pins")


# Customize these keywords to match your writing topics
THEME_KEYWORDS = {
    "机器学习 / 深度学习": ["深度学习", "机器学习", "神经网络", "deep learning", "neural", "CNN", "transformer"],
    "AGI / 大模型": ["AGI", "大模型", "LLM", "GPT", "Claude", "通用人工智能", "foundation model"],
    "强化学习 RL": ["强化学习", "RL ", "DQN", "PPO", "reward", "policy"],
    "具身智能 / 机器人": ["具身", "机器人", "robot", "humanoid", "VLA", "sim2real"],
    "研究方法 / 读论文": ["论文", "paper", "研究", "实验", "ablation", "benchmark"],
    "职业 / 成长": ["求职", "实习", "读博", "career", "成长", "经验", "建议"],
    "工具 / 效率": ["工具", "效率", "workflow", "代码", "编程", "Python"],
    "思考 / 观点": ["思考", "感悟", "观点", "认为", "分享"],
}


def build_core_views(articles: list[dict], answers: list[dict]):
    # 第二篇聚合文件生成器 (core_views.md)
    # 按预设定主题标签对整个语料库分层进行基于正则表达式关键字的语义映射
    # 这主要让 AI 知道 “作者是个什么领域内的人才以及有什么观点？” 
    corpus = articles + answers
    buckets: dict[str, list[tuple[str, str, int]]] = defaultdict(list)
    
    # 暴力双层循环匹配全选文（包含问题的标题 和 文章的内容）寻找上面定义的关键词簇
    for item in corpus:
        title = item.get("title") or item.get("question") or ""
        body = item.get("content_md") or ""
        if not body:
            continue
            
        # 扫描每个主题，检查是否命中
        for theme, kws in THEME_KEYWORDS.items():
            # 只要任意一个同源关键字组出现在题目或正文中，便视为打上该主题归属标签记录
            if any(k.lower() in title.lower() or k.lower() in body.lower() for k in kws):
                score = item.get("voteup_count") or 0
                buckets[theme].append((title, item.get("url", ""), score))

    # 输出排版组合
    lines = ["# hexin 核心观点索引\n",
             "按主题聚合本人写过的相关文章/回答。生成内容前先用 grep 找原文保持一致性。\n"]
             
    # 对每一个大类话题按赞数重新内排次序，每个主题最多列举最顶尖的 20 条代表作进行索引挂载
    for theme, items in buckets.items():
        items.sort(key=lambda x: -x[2])
        lines.append(f"\n## {theme}  ({len(items)} 条)\n")
        for title, url, score in items[:20]:
            lines.append(f"- [{title}]({url}) · {score} 赞")

    out = REF / "core_views.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}: {len(buckets)} themes")


def build_title_index(articles: list[dict], answers: list[dict]):
    # 第三篇聚合文件生成器 (title_index.md)
    # 按年月为单位归档时间线，让大模型产生纵向历史视角，看看作者这些年都在聊啥
    by_year: dict[str, list[tuple[str, str, str, int]]] = defaultdict(list)
    
    # 注明该记录来自专栏 [ART] 还是问题回答 [ANS]
    for a in articles:
        y = year(a.get("created"))
        by_year[y].append(("ART", a["title"], a.get("url", ""), a.get("voteup_count") or 0))
    for a in answers:
        y = year(a.get("created"))
        by_year[y].append(("ANS", a.get("question", ""), a.get("url", ""), a.get("voteup_count") or 0))

    lines = ["# hexin 全量内容索引（按月倒序）\n"]
    # 将时间键降序排列（最近的年份最先出现）
    for y in sorted(by_year.keys(), reverse=True):
        items = by_year[y]
        # 在同一个月内，依然按热度点赞降维排序。强者为尊定律
        items.sort(key=lambda x: -x[3])
        lines.append(f"\n## {y}  ({len(items)})\n")
        for kind, title, url, score in items:
            lines.append(f"- [{kind}] [{title}]({url}) · {score}")

    out = REF / "title_index.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


def build_search_helper():
    # 生成一个方便的 shell 检索脚本工具 (search_zhihu.sh)
    # 它本身就是大模型生态的一环：在遇到问题时如果 AI 判断知识库没有详细，会自动调用该脚本对抓取下来的超大 MD 字典全文匹配查询
    data_path = DATA.resolve()
    script = f"""#!/usr/bin/env bash
# Grep hexin's scraped Zhihu corpus. Usage: search_zhihu.sh "关键词"
# 一款对知乎三大本地落库产物(大文本 md)进行模糊多行查找的工具

set -e
# 如果用户不传参就报错终止 (-1:? 语法)
KEYWORD="${{1:?need keyword}}"
DATA_DIR="{data_path}"

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
"""
    p = REF / "search_zhihu.sh"
    p.write_text(script, encoding="utf-8")
    # 设置 linux 执行权限 0o755 让脚本具有运行能级
    p.chmod(0o755)
    print(f"wrote {p}")


def main():
    # 集中调度编排生成四种目标参考文件
    print(f"Loading data from: {DATA}")
    print(f"Writing references to: {REF}")
    articles = load("articles")
    pins = load("pins")
    answers = load("answers")
    total = len(articles) + len(pins) + len(answers)
    if total == 0:
        print("\nNo data found. Run scraper.py first:\n")
        print(f"  cd {PROJECT_ROOT}/scripts")
        print(f"  export ZHIHU_COOKIE='...'")
        print(f"  python3 scraper.py --user hexin_marsggbo --out ../data/zhihu")
        return
    print(f"Loaded: {len(articles)} articles, {len(pins)} pins, {len(answers)} answers")
    build_style_examples(articles, pins, answers)
    build_core_views(articles, answers)
    build_title_index(articles, answers)
    build_search_helper()
    print("\nDONE. References written to:", REF)


if __name__ == "__main__":
    main()
