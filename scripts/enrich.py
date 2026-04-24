#!/usr/bin/env python3
"""Fetch full content for each article/answer/pin from Zhihu detail APIs.
(从知乎详情 API 中获取每一个短文章、回答、想法的完整长内容)

由于在 scraper.py 中通过用户动态列表或时间线抓取的内容有时是被截断的（例如长文本仅包含前几十个字或摘要），
本脚本的任务是读取已经持久化在磁盘上的 JSON 列表文件，提取其中每一个内容的独立 id 并向 API 发起详情查询。
这种单独请求机制非常耗时，但只有这样才能拿到无损的高清完整内容用于后续处理。

Usage (用法):
    export ZHIHU_COOKIE="d_c0=...; z_c0=...; _xsrf=..."
    python3 enrich.py --dir ../data/zhihu

-- Forked from https://github.com/floodsung/floodsung-skill --
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# 将同级目录下的脚本添加到系统查找路径，以便导入 scraper 中的网络客户端和通用清洗库
sys.path.insert(0, str(Path(__file__).parent))
from scraper import ZhihuClient, clean_html_to_md, dump_markdown  # noqa: E402

from bs4 import BeautifulSoup


def enrich_articles(client: ZhihuClient, items: list[dict]) -> list[dict]:
    # 请求文章的独立详情 API，填充 content_md 字段和 excerpt 截取内容
    out = []
    # 逐条检索 articles.json 中的文章条目，打印处理进度提示
    for i, a in enumerate(items):
        aid = a["id"]
        # 请求专属该 id 的公开 API 端点
        url = f"https://www.zhihu.com/api/v4/articles/{aid}"
        try:
            # 拿到原始 JSON 树形结构
            d = client.get(url)
            # 使用提取器把纯 html 解析成我们要的带排版的 markdown 文本覆盖现有缩减字段
            a["content_md"] = clean_html_to_md(d.get("content", ""))
            # 同时也保持提取出一份最新的摘要，如果没拿到就继续保持它旧有的 excerpt 值
            a["excerpt"] = d.get("excerpt", a.get("excerpt", ""))
        except Exception as e:
            # 如果某次请求遭遇被服务端挂断、超时、或 404 就捕捉报错，脚本不会立刻白给崩溃
            print(f"  [{i+1}/{len(items)}] FAIL {aid}: {e}")
        else:
            # 成功记录字数状态，证明爬虫运转良好
            print(f"  [{i+1}/{len(items)}] {a['title'][:50]} → {len(a['content_md'])} chars")
        
        # 不管成功或失败，都在新列表中予以保留，然后睡眠一定间隔（极其关键的防限流护身符）
        out.append(a)
        time.sleep(0.6)
    return out


def enrich_answers(client: ZhihuClient, items: list[dict]) -> list[dict]:
    # 请求回答的完整详情，因为前置列表中常常会对过长字数的内容进行截断
    out = []
    for i, a in enumerate(items):
        ans_id = a["id"]
        # 请求带 include パラメータ以明确告知服务端把完整的原初 content html 下发给我们
        url = f"https://www.zhihu.com/api/v4/answers/{ans_id}?include=content,excerpt"
        try:
            d = client.get(url)
            # 通过 BeautifulSoup 转换为清晰明了的 markdown 笔记样式文本
            a["content_md"] = clean_html_to_md(d.get("content", ""))
            a["excerpt"] = d.get("excerpt", "")
        except Exception as e:
            # 捕捉异常并打印
            print(f"  [{i+1}/{len(items)}] FAIL ans{ans_id}: {e}")
        else:
            print(f"  [{i+1}/{len(items)}] {a['question'][:50]} → {len(a['content_md'])} chars")
        
        out.append(a)
        # 固定时延策略，对知乎爬虫至关重要 (低于 0.5s 非常容易遭受反爬触发验证码盾)
        time.sleep(0.6)
    return out


def enrich_pins(client: ZhihuClient, items: list[dict]) -> list[dict]:
    # 请求想法（短图文动态）详情，提取完整的纯文本结构。在个人主页往往只能看到省略的点图，详情可以拿到完整段落。
    out = []
    for i, p in enumerate(items):
        pid = p["id"]
        url = f"https://www.zhihu.com/api/v4/pins/{pid}"
        try:
            d = client.get(url)
            blocks = d.get("content", []) or []
            texts = []
            # 遍历动态组成的 blocks 积木堆（知乎想法的 content 返回的是一个由图片、文本、链接组成的混合数组结构）
            for b in blocks:
                # 我们过滤掉其他类型的展示位，只关心作者亲自码字的“文本类型”段落
                if b.get("type") == "text":
                    html = b.get("content", "")
                    # 一部分文字里面还残留 \u003Cbr\u003E 这类 html 符号，顺便把它们脱掉皮取直观纯本文
                    texts.append(BeautifulSoup(html, "lxml").get_text(" ", strip=True))
            # 拼合所有的自然语言段落覆写回去；若真的提取不出来哪怕半点就暂时用旧的内容兜底
            p["text"] = "\n".join(t for t in texts if t) or p.get("text", "")
        except Exception as e:
            print(f"  [{i+1}/{len(items)}] FAIL pin{pid}: {e}")
        else:
            print(f"  [{i+1}/{len(items)}] pin{pid} → {len(p['text'])} chars")
            
        out.append(p)
        time.sleep(0.4)
    return out


def main():
    # 脚本入口：加载现有 JSON 文件，对列表挨个请求补充完整文本内容后再覆盖保存原文件。
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="path to data/zhihu dir (必传参数：源数据读取和覆盖落地的对应相对或绝对路径)")
    ap.add_argument("--kinds", default="articles,pins,answers", help="需要完善的数据种类")
    args = ap.parse_args()

    # 查收必要凭据：ZHIHU_COOKIE 能保证可以顺利跨越防爬安全盾 
    cookie = os.environ.get("ZHIHU_COOKIE", "").strip()
    if not cookie:
        print("ERROR: export ZHIHU_COOKIE", file=sys.stderr)
        sys.exit(1)

    client = ZhihuClient(cookie)
    d = Path(args.dir)
    # 支持自定义选择想刷入哪些表（articles、pins）、默认是全盘大洗牌，按逗号切分出列表
    kinds = [k.strip() for k in args.kinds.split(",")]

    for kind in kinds:
        # 指向之前用 scraper.py 产出的预制源 json 信息流大文件
        path = d / f"{kind}.json"
        
        # 不存在目标文件就忽略进行到下个类别
        if not path.exists():
            print(f"skip {kind}, no file at {path}")
            continue
            
        items = json.loads(path.read_text(encoding="utf-8"))
        print(f"\n=== enrich {kind} ({len(items)}) ===")
        
        # 定义一个方便的路由映射字典，直接找到对应功能指针挂载进去运转
        fn = {"articles": enrich_articles, "pins": enrich_pins, "answers": enrich_answers}[kind]
        # 发射！遍历跑全量富化内容
        items = fn(client, items)
        
        # 所有列表中的元素被注入完毕后，统一写入覆盖原有的初版体积较小的 JSON 
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        # 并基于最新获取到的详细长内容再次重新生成对应的大集合 Markdown 文档排版
        dump_markdown(items, d / f"{kind}.md", kind)
        print(f"saved {kind} (抓取及覆盖入库操作结束成功)")


if __name__ == "__main__":
    main()
