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


def _api(session: requests.Session, method: str, path: str, **kw) -> requests.Response:
    url = f"{API_BASE}/repos/{REPO}"
    if path:
        url += f"/{path}"
    r = session.request(method, url, **kw)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code} {r.json().get('message', r.text)}")
    return r


def commit_files(session: requests.Session, files: list[tuple[str, bytes]], message: str) -> str:
    """Commit multiple files in a SINGLE commit via the Git Data API.

    files: list of (repo_path, content_bytes). Returns the new commit SHA.
    """
    # 1. Resolve default branch + its tip commit
    default_branch = _api(session, "GET", "").json()["default_branch"]
    ref = _api(session, "GET", f"git/ref/heads/{default_branch}").json()
    base_commit_sha = ref["object"]["sha"]
    base_tree_sha = _api(session, "GET", f"git/commits/{base_commit_sha}").json()["tree"]["sha"]

    # 2. Create a blob per file
    tree_entries = []
    for repo_path, content in files:
        blob = _api(session, "POST", "git/blobs", json={
            "content": base64.b64encode(content).decode(),
            "encoding": "base64",
        }).json()
        tree_entries.append({
            "path": repo_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"],
        })
        print(f"  staged  {repo_path}")

    # 3. Build a tree, commit, and move the branch ref
    new_tree = _api(session, "POST", "git/trees", json={
        "base_tree": base_tree_sha,
        "tree": tree_entries,
    }).json()
    new_commit = _api(session, "POST", "git/commits", json={
        "message": message,
        "tree": new_tree["sha"],
        "parents": [base_commit_sha],
    }).json()
    _api(session, "PATCH", f"git/refs/heads/{default_branch}", json={"sha": new_commit["sha"]})
    print(f"  committed {new_commit['sha'][:7]} to {default_branch}")
    return new_commit["sha"]


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

    # Collect ALL files (markdown + images) so they go in one commit
    files: list[tuple[str, bytes]] = []

    # 1. Markdown — rewrite relative `assets/xxx.png` to absolute repo path
    md_content = md_file.read_text(encoding="utf-8")
    remote_img_base = f"/assets/img/posts/{slug}"
    md_content_remote = re.sub(r"\]\(assets/", f"]({remote_img_base}/", md_content)
    files.append((f"_posts/{md_name}", md_content_remote.encode("utf-8")))

    # 2. Images
    if assets_dir.is_dir():
        imgs = sorted(
            f for f in assets_dir.iterdir()
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp")
        )
        for img in imgs:
            files.append((f"assets/img/posts/{slug}/{img.name}", img.read_bytes()))

    # 3. One commit for everything
    commit_files(session, files, f"Add post: {slug} ({len(files)} files)")

    print()
    print("=== Done! ===")
    print(f"View at: https://marsggbo.github.io/blog/")


if __name__ == "__main__":
    main()
