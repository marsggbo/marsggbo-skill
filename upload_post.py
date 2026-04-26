#!/usr/bin/env python3
"""
upload_post.py — Upload a marsggbo blog post to GitHub Pages repo via GitHub API.

Usage:
    python3 upload_post.py <post_dir>

    post_dir: ~/Desktop/posts/<paper_slug>/
    Must contain:
      - YYYY-MM-DD-<slug>.md   (the article, images referenced as assets/xxx.png)
      - assets/                (image files)

Uploads to https://github.com/marsggbo/marsggbo.github.io:
  - md   → _posts/YYYY-MM-DD-<slug>.md  (with assets/ paths rewritten to /assets/img/posts/<slug>/)
  - imgs → assets/img/posts/<slug>/

GitHub token read from:
  1. GH_TOKEN env var
  2. ~/.claude/skills/marsggbo/github_token
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
from pathlib import Path

import requests

REPO = "marsggbo/marsggbo.github.io"
API_BASE = "https://api.github.com"


def get_token() -> str:
    token = os.environ.get("GH_TOKEN", "")
    if token:
        return token
    token_file = Path.home() / ".claude/skills/marsggbo/github_token"
    if token_file.exists():
        return token_file.read_text().strip()
    raise RuntimeError(
        "No GitHub token. Set GH_TOKEN env var or create ~/.claude/skills/marsggbo/github_token"
    )


def get_file_sha(session: requests.Session, path: str) -> str | None:
    """Return the SHA of an existing file, or None if not found."""
    r = session.get(f"{API_BASE}/repos/{REPO}/contents/{path}")
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def upload_file(session: requests.Session, repo_path: str, content: bytes, message: str) -> bool:
    """Create or update a file in the repo. Returns True on success."""
    sha = get_file_sha(session, repo_path)
    payload: dict = {
        "message": message,
        "content": base64.b64encode(content).decode(),
    }
    if sha:
        payload["sha"] = sha

    r = session.put(f"{API_BASE}/repos/{REPO}/contents/{repo_path}", json=payload)
    if r.status_code in (200, 201):
        print(f"  OK  {repo_path}")
        return True
    else:
        print(f"  FAIL {repo_path}: {r.status_code} {r.json().get('message', '')}")
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <post_dir>", file=sys.stderr)
        sys.exit(1)

    post_dir = Path(sys.argv[1]).expanduser().resolve()
    if not post_dir.is_dir():
        print(f"ERROR: {post_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    slug = post_dir.name

    # Find markdown file
    md_files = sorted(post_dir.glob("*.md"))
    if not md_files:
        print(f"ERROR: No .md file found in {post_dir}", file=sys.stderr)
        sys.exit(1)
    md_file = md_files[0]
    md_name = md_file.name

    assets_dir = post_dir / "assets"

    token = get_token()
    session = requests.Session()
    session.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    })

    print(f"=== Uploading post: {slug} ===")

    # 1. Upload markdown — rewrite image paths
    print("--- Uploading markdown ---")
    md_content = md_file.read_text(encoding="utf-8")
    # Replace relative `assets/xxx.png` with absolute `/assets/img/posts/<slug>/xxx.png`
    remote_img_base = f"/assets/img/posts/{slug}"
    md_content_remote = re.sub(
        r"\]\(assets/",
        f"]({remote_img_base}/",
        md_content,
    )
    upload_file(session, f"_posts/{md_name}", md_content_remote.encode("utf-8"),
                f"Add post: {slug}")

    # 2. Upload images
    if assets_dir.is_dir():
        print("--- Uploading images ---")
        imgs = sorted(
            f for f in assets_dir.iterdir()
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")
        )
        for img in imgs:
            upload_file(session, f"assets/img/posts/{slug}/{img.name}",
                        img.read_bytes(), f"Add image: {slug}/{img.name}")
    else:
        print("--- No assets/ directory, skipping images ---")

    print()
    print("=== Done! ===")
    print(f"View at: https://marsggbo.github.io/blog/")


if __name__ == "__main__":
    main()
