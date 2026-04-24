#!/usr/bin/env python3
"""Zhihu scraper for hexin_marsggbo's articles, pins, and answers.
(知乎数据爬虫，用于抓取 hexin_marsggbo 的文章、想法和回答)

该脚本是一个基于 Requests 库和 BeautifulSoup 的知乎爬虫。
它模拟了浏览器行为，逆向并实现了知乎的关键接口校验（如 x-zse-96 签名计算），
可以将知乎个人主页的各种内容分门别类地获取并整理成 JSON 和 Markdown 文件。

Usage (用法):
    export ZHIHU_COOKIE="d_c0=...; z_c0=...; _xsrf=..."
    python3 scraper.py --user hexin_marsggbo --out ../data/zhihu

Requires a logged-in cookie because Zhihu blocks anonymous API access.
(由于知乎禁止匿名访问API，获取大部分数据必须携带带有身份信息的 Cookie)
Hashes the `d_c0` value to compute the x-zse-96 signature for stable paging.
(通过对 `d_c0` 值进行特定的 MD5 加盐哈希计算，生成 x-zse-96 接口签名，以保证分页请求能够成功且不被风控拦截)

-- Forked from https://github.com/floodsung/floodsung-skill --
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

ZHIHU_USER = "hexin_marsggbo"


def parse_cookie(raw: str) -> dict[str, str]:
    # 解析从浏览器中复制出来的原始 Cookie 字符串，将其转换为字典，方便塞进 Requests 会话中
    jar: dict[str, str] = {}
    for part in raw.split(";"):
        part = part.strip()
        # 跳过空字符串和格式不对的字符串块
        if not part or "=" not in part:
            continue
        # 按照第一个等号切分键值对，例如 "d_c0=abcde" -> k: "d_c0", v: "abcde"
        k, v = part.split("=", 1)
        jar[k.strip()] = v.strip()
    return jar


def get_dc0(cookie: dict[str, str]) -> str:
    # 从解析完成的字典里提取关键字段 d_c0，这个值相当于浏览器的指纹，是后续 API 签名的关键依赖
    dc0 = cookie.get("d_c0", "")
    if not dc0:
        raise SystemExit("cookie missing d_c0; re-login to zhihu and copy a fresh cookie (未能找到 d_c0，请重新登录知乎并复制完整的 cookie)")
    return dc0


def sign(url: str, dc0: str) -> str:
    # 核心加密逻辑：计算请求头的 x-zse-96 签名，这是知乎防爬虫的核心手段。没有正确的签名会返回 403。
    # 抽取请求 URL 中的相对路径以及附带的 query 参数。例如 /api/v4/articles?limit=20
    parsed = urlparse(url)
    path_q = parsed.path + ("?" + parsed.query if parsed.query else "")
    
    # 将协议版本 (101_3_3.0)、路径和 d_c0 值以加号拼接成特定盐值加密字符串
    raw = f"101_3_3.0+{path_q}+{dc0}"
    # 计算拼接字符串的 MD5 摘要值
    md5 = hashlib.md5(raw.encode()).hexdigest()
    # 签名格式固定为 2.0_ 加上 32 位的 md5 结果
    return "2.0_" + md5


class ZhihuClient:
    # 知乎自定义网络客户端，持久化会话级信息，自动处理反爬请求头和 API 签名
    def __init__(self, cookie: str):
        self.cookie = parse_cookie(cookie)
        self.dc0 = get_dc0(self.cookie)
        self.s = requests.Session()
        
        # 覆写会话级别 headers 去伪装为一个正常的 Chrome 浏览器环境和 XHR 异步请求流
        self.s.headers.update({
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.zhihu.com/",      # Referer 欺骗检测服务器来源
            "x-requested-with": "fetch",              # 表示这是一个数据抓取请求类型
            "x-zse-93": "101_3_3.0",                  # 版本标识配合 x-zse-96 使用
        })
        # 挂载解析好的 cookie 到后续的所有 Request 中
        self.s.cookies.update(self.cookie)

    def get(self, url: str, **params) -> dict[str, Any]:
        # 统一 GET 接口：在此处将 URL 及查询参数拼装，动态计算每一次的 x-zse-96 签名
        full = url
        if params:
            # 手动把 dict 转换成 param 字符串，确保加密原串与 requests 发出的保持 100% 同步
            q = "&".join(f"{k}={v}" for k, v in params.items())
            full = url + ("&" if "?" in url else "?") + q
            
        # 根据动态拼接的完整 url 以及该会话自己的 dc0 生成签名 header
        headers = {"x-zse-96": sign(full, self.dc0)}
        # 执行带有 30s 超时时间设定的 request
        r = self.s.get(full, headers=headers, timeout=30)
        
        if r.status_code != 200:
            # 捕获封禁或是校验失败异常
            raise RuntimeError(f"HTTP {r.status_code} on {full}: {r.text[:300]}")
        # 解析知乎 API 返回的标准 JSON 结构对象并返回
        return r.json()

    def paginate(self, url: str, page_size: int = 20) -> Iterable[dict[str, Any]]:
        # 分页获取列表数据生成器，处理长列表抓取（如用户的多页文章列表）并负责自动下翻获取下一页偏移量 (offsets)
        offset = 0
        while True:
            # 发起带 offset 和 limit 的列表请求
            data = self.get(url, offset=offset, limit=page_size)
            items = data.get("data", []) or []
            
            # 使用 yield 生成器语法，让调用端可以对分页数据进行流式 for 循环遍历
            for it in items:
                yield it
                
            paging = data.get("paging", {}) or {}
            
            # 如果到达尽头 "is_end": true 或者本页没有包含任何元素则结束死循环
            if paging.get("is_end") or not items:
                break
                
            # 移动指针至下一页起点
            offset += page_size
            # 睡眠 0.8s 非常重要！！这样能够大幅减少短时间高频爬虫引起的账号临时控制封禁动作
            time.sleep(0.8)


def clean_html_to_md(html: str) -> str:
    # 核心转换管道：负责将知乎返回的复杂带样式的 HTML 原文，清洗并转换为干净易读的 Markdown 纯本文格式
    if not html:
        return ""
    # 用 BeautifulSoup 解析并重构 DOM 树 
    soup = BeautifulSoup(html, "lxml")
    
    # 特别处理图片：知乎返回的 figure img 中 src 通常是小缩略图或是空的，
    # 而高清原图的实际链接往往被存放在其 data-original 自定义属性中。
    for fig in soup.find_all("figure"):
        img = fig.find("img")
        if img and img.get("data-original"):
            # 将 src 直接替换成真实大图链接，以便后续转换为 Markdown 正确的图片声明
            img["src"] = img["data-original"]
            
    # markdownify: 将上面修补完成的 dom html 内容全部转变为 markdown 结构
    # heading_style="ATX" 确保标题是用 ### Name 写法而不是带下划线的旧写法
    return md(str(soup), heading_style="ATX").strip()


def scrape_articles(client: ZhihuClient, user: str, out_dir: Path) -> list[dict]:
    # 抓取用户发布的文章列表 (专栏与常规文章)。通过 paginate 不断请求下一页，直至穷尽
    out = []
    # 这个 endpoint 指向用户主页的 "文章" 分栏，我们用 include 参数要求返回文章的原始内容以及点赞数量等额外细节
    url = f"https://www.zhihu.com/api/v4/members/{user}/articles?include=content,voteup_count,comment_count,created,updated"
    
    for it in client.paginate(url):
        # 将原始冗杂的响应过滤结构，只筛选所需和清洗后的干净属性
        out.append({
            "id": it.get("id"),
            "title": it.get("title"),
            "url": it.get("url", f"https://zhuanlan.zhihu.com/p/{it.get('id')}"), 
            "created": it.get("created"),
            "updated": it.get("updated"),
            "voteup_count": it.get("voteup_count"),      # 赞同数
            "comment_count": it.get("comment_count"),    # 评论数
            "content_md": clean_html_to_md(it.get("content", "")),  # 即时将详情 html 转换为 markdown
            "excerpt": it.get("excerpt", ""),          # 文章简短摘要
        })
        # 控制台打印进度提示用户还活着
        print(f"  article: {it.get('title')}", flush=True)
    return out


def scrape_pins(client: ZhihuClient, user: str) -> list[dict]:
    # 抓取用户的 "想法（即：类似 Twitter/朋友圈 的片段内容动态）"。由于知乎想法有新老 API 版本差异，
    # 我们首选用支持结构化富文本提取的 v2 接口，失败或报错了再使用老版 Fallback 接口兜底。
    out = []
    
    # 尝试访问新版 API (以 v2 开头)
    url = f"https://www.zhihu.com/api/v4/v2/pins/profile/{user}"
    try:
        for it in client.paginate(url):
            content_blocks = it.get("content", []) or []
            texts = []
            
            # 由于想法包含了照片、外部链接图文卡片和纯文本，因此我们将类型严格锁定 "type": "text" 获取作者手敲字符
            for b in content_blocks:
                if b.get("type") == "text":
                    # 使用 get_text 去除 <br> 等冗余标签
                    texts.append(BeautifulSoup(b.get("content", ""), "lxml").get_text(" ", strip=True))
            
            out.append({
                "id": it.get("id"),
                "url": f"https://www.zhihu.com/pin/{it.get('id')}",
                "created": it.get("created"),
                "text": "\n".join(t for t in texts if t),  # 将多段提取出来的文本合并为一份自然字符
                "like_count": it.get("like_count"),
                "comment_count": it.get("comment_count"),
            })
            print(f"  pin: {out[-1]['text'][:60]}", flush=True)
            
    except RuntimeError as e:
        # 抛出封禁或是权限错误说明部分账号使用不了 v2，这很常见，降配去请求无版本号的基础旧 API
        print(f"  pins v2 failed ({e}); trying fallback (新版接口请求失败，进入备用旧版接口请求流程)", flush=True)
        url2 = f"https://www.zhihu.com/api/v4/members/{user}/pins"
        
        for it in client.paginate(url2):
            out.append({
                "id": it.get("id"),
                "url": f"https://www.zhihu.com/pin/{it.get('id')}",
                "created": it.get("created"),
                # 老版本接口直接吐给你 html 或者 excerpt_title 字典碎片，依然得用 soup 包一把进行提纯
                "text": BeautifulSoup(it.get("excerpt_title", "") or it.get("content_html", ""), "lxml").get_text(" ", strip=True),
                "like_count": it.get("like_count"),
                "comment_count": it.get("comment_count"),
            })
    return out


def scrape_answers(client: ZhihuClient, user: str) -> list[dict]:
    # 遍历并抓取目标用户参与回答的所有问题清单及填写的原文
    out = []
    
    # 携带 include 可以一次性把答案原本的内容和隶属原问题的标题一块带离接口，不用发二次嵌套请求浪费资源
    url = (
        f"https://www.zhihu.com/api/v4/members/{user}/answers"
        "?include=content,voteup_count,comment_count,created_time,updated_time,question.title"
    )
    for it in client.paginate(url):
        # 提取问题实体，为了避免其是 null 我们给了一个 fallback {}
        q = it.get("question", {}) or {}
        out.append({
            "id": it.get("id"),
            "question": q.get("title", ""),
            "question_id": q.get("id"),
            "url": f"https://www.zhihu.com/question/{q.get('id')}/answer/{it.get('id')}",
            "created": it.get("created_time"),
            "updated": it.get("updated_time"),
            "voteup_count": it.get("voteup_count"),
            "comment_count": it.get("comment_count"),
            "content_md": clean_html_to_md(it.get("content", "")), # 因为长短可能不一样需要转换为 markdown
        })
        print(f"  answer: {q.get('title', '')[:60]}", flush=True)
    return out


def dump_markdown(items: list[dict], path: Path, kind: str, display_name: str = "hexin"):
    # 为了方便 AI 大模型读取或者作为 Markdown 本地知识库笔记索引检索
    # 我们遍历所有的条目，为它们统一套上一层带 `---` 分隔的大文本聚合格式。
    lines = [f"# {display_name} — {kind}\n", f"Total: {len(items)}\n"]
    
    for it in items:
        # title 对于专栏叫 'title'，对于回答叫 'question'，如果它是随想就只能取内容当成临时标题展示前60个字符
        title = it.get("title") or it.get("question") or (it.get("text", "")[:60])
        lines.append(f"\n---\n\n## {title}\n")
        meta = []
        
        # 拼接一些 Meta 头信息（时间、链接、赞）到每一篇开头，并将其用反转破折引号包裹表示高亮代码段
        if "url" in it: meta.append(f"link: {it['url']}")
        if it.get("created"): meta.append(f"created: {it['created']}")
        if it.get("voteup_count") is not None: meta.append(f"voteup: {it['voteup_count']}")
        if meta:
            lines.append("`" + " · ".join(str(m) for m in meta) + "`\n")
            
        # 选择已经准备好的干净 md 文本或原本文本
        body = it.get("content_md") or it.get("text") or ""
        if body:
            lines.append("\n" + body + "\n")
            
    # 将包含所有数据信息的行阵列全部拼装合拢使用文件 utf-8 保存到本地磁盘中        
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    # 启动抓取工作流的主承接函数：处理用户命令行指令，进行环境校验，按模块下发爬虫任务。
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=ZHIHU_USER, help="zhihu url_token (知乎主页URL中的那个自定义用户名)")
    ap.add_argument("--out", required=True, help="output dir (存放抓取到的所有文件的产物存储文件夹目标地址)")
    ap.add_argument("--kinds", default="articles,pins,answers", help="comma sep (逗号分割的目标列表类型，控制是只抓文章还是全抓)")
    args = ap.parse_args()

    # 尝试从系统环境变量里提取带有鉴权信息的 ZHIHU_COOKIE，必须填写
    cookie = os.environ.get("ZHIHU_COOKIE", "").strip()
    if not cookie:
        print("ERROR: export ZHIHU_COOKIE before running (必须通过环境变量定义全局 ZHIHU_COOKIE 才能继续执行)", file=sys.stderr)
        sys.exit(1)

    # 安全创建结果文件夹层次，当文件夹早已存在时候也不会触发崩溃
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 实体化携带了这个鉴权信息的全自动客户端
    client = ZhihuClient(cookie)
    # 按逗号切割出数组形式如：["articles", "pins"]
    kinds = [k.strip() for k in args.kinds.split(",") if k.strip()]

    results: dict[str, list[dict]] = {}
    
    # 根据用户选项按需依次调度调用各种抓取接口
    if "articles" in kinds:
        print("\n=== articles ===")
        results["articles"] = scrape_articles(client, args.user, out_dir)
    if "pins" in kinds:
        print("\n=== pins (想法) ===")
        results["pins"] = scrape_pins(client, args.user)
    if "answers" in kinds:
        print("\n=== answers ===")
        results["answers"] = scrape_answers(client, args.user)

    # 后置处理器：将抓取的 Dict 数据结构进行落库整理输出
    for kind, items in results.items():
        # 写一份结构化的 .json 文件，方便代码后续二次利用或加载分析
        (out_dir / f"{kind}.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # 写一份平易近人的 .md 文件，可以直接发给 Claude LLM 或者普通人阅览
        dump_markdown(items, out_dir / f"{kind}.md", kind)
        print(f"saved {len(items)} {kind} → {out_dir / f'{kind}.json'}")

    # 将所有过程量与执行时刻记录在 summary.json 中产生本次离线分析的溯源痕迹，这是一种极好的工程归档习惯
    summary = {
        "user": args.user,
        "counts": {k: len(v) for k, v in results.items()},
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nDONE (所有的内容均已在本地存储归档完成):", summary)


if __name__ == "__main__":
    main()
