#!/Users/hex/miniforge3/bin/python3
"""
paper_assets.py — Extract figures, tables, and page renders from academic papers.

Standalone tool. Works as a CLI or importable module.
Designed for /hexin skill but intentionally generic.

Extraction strategies (tried in 'auto' order):
  html  — parse arXiv HTML version (best quality: has captions + clean images)
  pdf   — extract raster images embedded in PDF via PyMuPDF
  pages — render specific PDF pages at high DPI (always works, broadest coverage)

─────────────────────────────────────────────────────────────────
CLI usage:
  paper_assets.py <url-or-path> [options]

  Arguments:
    source                  arXiv URL/ID, HTTP PDF URL, or local PDF path

  Options:
    --output-dir DIR        where to save assets (default: ./paper_assets/)
    --strategy auto|html|pdf|pages
                            extraction strategy (default: auto)
    --dpi N                 DPI for page renders (default: 150)
    --min-width N           skip embedded images narrower than N px (default: 80)
    --min-height N          skip embedded images shorter than N px (default: 80)
    --render-pages SPEC     also render specific pages, e.g. "1,3-5,8"
    --cache-dir DIR         cache downloaded PDFs here (default: system temp)
    --format json|summary|md
                            output format (default: json)

  Examples:
    paper_assets.py https://arxiv.org/abs/2604.07144
    paper_assets.py 2604.07144 --output-dir ~/Desktop/paper_assets --format summary
    paper_assets.py paper.pdf --strategy pages --render-pages 1-4 --dpi 200
    paper_assets.py https://arxiv.org/abs/2604.07144 --render-pages 3,5,7

─────────────────────────────────────────────────────────────────
Import usage:
  from paper_assets import extract_assets

  assets = extract_assets(
      source="https://arxiv.org/abs/2604.07144",
      output_dir="/tmp/my_paper",
      render_pages="3,5",       # also render pages 3 and 5
  )
  print(assets.summary())
  print(assets.to_json())
  print(assets.md_snippets())   # ready-to-paste markdown image refs
  for fig in assets.figures:
      print(fig.rel_path, fig.label, fig.caption[:60])
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from PIL import Image


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class FigureAsset:
    path: str       # absolute path to saved image file
    rel_path: str   # path relative to output_dir — use this in markdown
    label: str      # "Figure 1", "Table 2", "Algorithm 1", etc.
    caption: str    # caption text extracted from the paper
    category: str   # figure | table | algorithm | page
    source: str     # html | pdf_embedded | page_render
    page: int       # 0-indexed PDF page number (-1 if unknown)
    width: int      # image width in pixels
    height: int     # image height in pixels

    def md_ref(self) -> str:
        """Return a Markdown image reference ready to embed in an article."""
        alt = (self.caption[:120] if self.caption else self.label) or self.rel_path
        return f"![{alt}]({self.rel_path})"


@dataclass
class PaperAssets:
    source: str          # original input (URL or path)
    arxiv_id: str        # e.g. "2604.07144v1", empty if not an arXiv paper
    title: str           # paper title (best-effort)
    pdf_path: str        # local PDF path
    output_dir: str      # root directory where assets were saved
    strategy_used: str   # which strategy produced the figures
    figures: list[FigureAsset] = field(default_factory=list)
    error: Optional[str] = None

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    def summary(self) -> str:
        lines = [
            f"Paper    : {self.title or self.source}",
            f"Assets   : {self.output_dir}",
            f"Extracted: {len(self.figures)} items  [strategy={self.strategy_used}]",
            "",
        ]
        for f in self.figures:
            cap = (f.caption[:70] + "…") if len(f.caption) > 70 else f.caption
            lines.append(f"  [{f.category:9}] {f.label:14}  {f.rel_path}")
            if cap:
                lines.append(f"              {cap}")
        return "\n".join(lines)

    def md_snippets(self) -> str:
        """All figures as markdown image references, newline-separated."""
        return "\n\n".join(f.md_ref() for f in self.figures)


# ─── Internal helpers ──────────────────────────────────────────────────────────

_ARXIV_ID_RE = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf|html)/|^arxiv:?)?"
    r"((?:\d{4}\.\d{4,5}|\w+/\d{7})(?:v\d+)?)",
    re.IGNORECASE,
)


def _extract_arxiv_id(source: str) -> str:
    """Extract bare arXiv ID (with optional version) from a URL or ID string."""
    m = _ARXIV_ID_RE.search(source)
    return m.group(1) if m else ""


def _parse_page_spec(spec: str) -> list[int]:
    """Convert "1,3-5,8" → [0, 2, 3, 4, 7] (0-indexed)."""
    result: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            result.extend(range(int(a) - 1, int(b)))
        else:
            result.append(int(part) - 1)
    return sorted(set(result))


def _save_pil(img_bytes: bytes, dest: Path) -> Optional[tuple[int, int]]:
    """Save raw image bytes to dest as PNG. Returns (width, height) or None on error."""
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("CMYK", "P", "LA"):
            img = img.convert("RGBA" if "A" in img.mode else "RGB")
        img.save(dest, format="PNG")
        return img.width, img.height
    except Exception:
        return None


def _download_pdf(url: str, cache_dir: Path) -> Path:
    """Download a PDF from `url` into `cache_dir`, return local Path. Cached."""
    safe = re.sub(r"[^\w.-]", "_", urlparse(url).path.lstrip("/")) or "paper"
    if not safe.endswith(".pdf"):
        safe += ".pdf"
    dest = cache_dir / safe
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    r = requests.get(url, headers={"User-Agent": "paper-assets/1.0"}, timeout=90, stream=True)
    r.raise_for_status()
    with dest.open("wb") as fh:
        for chunk in r.iter_content(1 << 16):
            fh.write(chunk)
    return dest


def _pdf_metadata_title(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    return (doc.metadata or {}).get("title", "") or ""


# ─── Strategy 1: arXiv HTML ───────────────────────────────────────────────────

def _strategy_html(arxiv_id: str, output_dir: Path, flat: bool = False) -> tuple[str, list[FigureAsset]]:
    """
    Fetch the arXiv HTML version of a paper and extract all <figure> elements.
    Returns (title, figures). Raises requests.HTTPError / RuntimeError on failure.
    """
    # arXiv HTML lives at /html/<id>  (e.g. /html/2604.07144v1)
    # Trailing slash is critical for urljoin: without it, relative image paths
    # like "x1.png" resolve to /html/x1.png instead of /html/<id>/x1.png
    base_url = f"https://arxiv.org/html/{arxiv_id}/"
    r = requests.get(base_url, headers={"User-Agent": "paper-assets/1.0"}, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # title
    title_tag = (
        soup.find("h1", class_=re.compile(r"ltx_title_document"))
        or soup.find("title")
    )
    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    # Strip "arXiv:XXXX - " prefix common in <title>
    title = re.sub(r"^\[?\d{4}\.\d+\]?\s*[-–—]?\s*", "", title).strip()

    figs_dir = output_dir if flat else output_dir / "assets"
    figs_dir.mkdir(parents=True, exist_ok=True)

    assets: list[FigureAsset] = []
    seen_srcs: set[str] = set()

    for fig_tag in soup.find_all("figure"):
        cap_tag = fig_tag.find("figcaption")
        caption = cap_tag.get_text(" ", strip=True) if cap_tag else ""

        # label
        label_tag = fig_tag.find(class_=re.compile(r"ltx_tag_(figure|table)"))
        label = label_tag.get_text(strip=True).rstrip(".:") if label_tag else ""

        # category heuristic
        cap_lower = caption.lower()
        if re.search(r"\btable\b", cap_lower[:30]):
            category = "table"
        elif re.search(r"\balgorithm\b|\balg\.\b", cap_lower[:30]):
            category = "algorithm"
        else:
            category = "figure"

        imgs = fig_tag.find_all("img")
        if not imgs:
            continue  # vector-only or pure-table figure — skip (page render covers it)

        for img_tag in imgs:
            src = img_tag.get("src", "").strip()
            if not src or src in seen_srcs:
                continue
            seen_srcs.add(src)

            img_url = urljoin(base_url, src)
            try:
                ir = requests.get(
                    img_url,
                    headers={"User-Agent": "paper-assets/1.0"},
                    timeout=20,
                )
                ir.raise_for_status()
                img_bytes = ir.content
            except Exception:
                continue

            idx = len(assets) + 1
            safe_label = re.sub(r"\W+", "_", label or f"fig{idx}").strip("_")
            dest = figs_dir / f"{idx:03d}_{safe_label}.png"
            dims = _save_pil(img_bytes, dest)
            if dims is None:
                continue
            w, h = dims

            assets.append(FigureAsset(
                path=str(dest),
                rel_path=str(dest.relative_to(output_dir)),
                label=label,
                caption=caption,
                category=category,
                source="html",
                page=-1,
                width=w,
                height=h,
            ))

    if not assets:
        raise RuntimeError("arXiv HTML: no figure images found")

    return title, assets


# ─── Strategy 2: PDF embedded images ──────────────────────────────────────────

def _strategy_pdf_embedded(
    pdf_path: Path,
    output_dir: Path,
    min_width: int = 80,
    min_height: int = 80,
    flat: bool = False,
) -> list[FigureAsset]:
    """Extract raster images embedded in the PDF via PyMuPDF."""
    doc = fitz.open(str(pdf_path))
    figs_dir = output_dir if flat else output_dir / "assets"
    figs_dir.mkdir(parents=True, exist_ok=True)

    assets: list[FigureAsset] = []
    seen_xrefs: set[int] = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base = doc.extract_image(xref)
            except Exception:
                continue

            w0, h0 = base["width"], base["height"]
            if w0 < min_width or h0 < min_height:
                continue

            idx = len(assets) + 1
            dest = figs_dir / f"emb_{idx:03d}_p{page_num + 1}.png"
            dims = _save_pil(base["image"], dest)
            if dims is None:
                continue
            w, h = dims

            assets.append(FigureAsset(
                path=str(dest),
                rel_path=str(dest.relative_to(output_dir)),
                label=f"Figure {idx}",
                caption="",
                category="figure",
                source="pdf_embedded",
                page=page_num,
                width=w,
                height=h,
            ))

    return assets


# ─── Strategy 3: page render ──────────────────────────────────────────────────

def _strategy_page_render(
    pdf_path: Path,
    output_dir: Path,
    page_indices: list[int],
    dpi: int = 150,
    flat: bool = False,
) -> list[FigureAsset]:
    """Render listed PDF pages (0-indexed) as PNG images."""
    doc = fitz.open(str(pdf_path))
    pages_dir = output_dir if flat else output_dir / "assets"
    pages_dir.mkdir(parents=True, exist_ok=True)

    mat = fitz.Matrix(dpi / 72, dpi / 72)
    assets: list[FigureAsset] = []
    valid = [i for i in page_indices if 0 <= i < len(doc)]

    for page_num in valid:
        page = doc[page_num]
        pix = page.get_pixmap(matrix=mat)
        dest = pages_dir / f"page_{page_num + 1:03d}.png"
        pix.save(str(dest))

        assets.append(FigureAsset(
            path=str(dest),
            rel_path=str(dest.relative_to(output_dir)),
            label=f"Page {page_num + 1}",
            caption="",
            category="page",
            source="page_render",
            page=page_num,
            width=pix.width,
            height=pix.height,
        ))

    return assets


# ─── Strategy 4: figure crop (caption-anchored, v2) ──────────────────────────

_CAPTION_RE = re.compile(
    r"^\s*(Figure|Fig\.?|Table|Algorithm|Alg\.?)\s*([0-9]+)\s*[:.\u2236]?",
    re.IGNORECASE,
)


def _detect_columns(
    lines: list[tuple],
    page_rect,
) -> list[tuple[float, float]]:
    """
    Detect 1- or 2-column layout from line bboxes.
    Strategy: separate lines whose x-range lies clearly in left vs. right half.
    - left-only : starts in left half (x0 < mid) AND ends before mid + 20 pt
    - right-only: starts after mid - 20 pt AND x1 > mid
    Full-width lines (spanning both halves) are ignored for column detection.
    Require >= 2 lines in each half to call it two-column.

    Accepts line tuples of length >= 4 (only the bbox coordinates are used).
    """
    page_w = page_rect.width
    mid = page_rect.x0 + page_w / 2
    # Minimum line width: 12% of page (avoids tick marks, short labels)
    min_w = page_w * 0.12

    wide = [(ln[0], ln[2]) for ln in lines if (ln[2] - ln[0]) > min_w]
    if not wide:
        return [(page_rect.x0, page_rect.x1)]

    # left-only: clearly in left half (doesn't cross far into right side)
    left_only  = [(x0, x1) for x0, x1 in wide if x0 < mid and x1 < mid + 20]
    # right-only: clearly in right half (doesn't start too far into left side)
    right_only = [(x0, x1) for x0, x1 in wide if x0 > mid - 20 and x1 > mid]

    # Require a meaningful number of lines in each half. A real two-column
    # paper has many such lines; <8 usually means we're seeing figure-internal
    # text that happens to sit on one side, not actual column layout.
    if len(left_only) >= 8 and len(right_only) >= 8:
        col_l = (min(x0 for x0, _ in left_only)  - 2,
                 max(x1 for _, x1 in left_only)  + 4)
        col_r = (min(x0 for x0, _ in right_only) - 4,
                 max(x1 for _, x1 in right_only) + 2)
        return [col_l, col_r]

    # Single column fallback
    return [(min(x0 for x0, _ in wide) - 2,
             max(x1 for _, x1 in wide) + 2)]


def _get_column(
    x_center: float,
    col_bounds: list[tuple[float, float]],
    page_rect,
) -> tuple[float, float]:
    """
    Return (x0, x1) of the column that contains x_center.
    When only one "column" was detected (single-column fallback), use page
    midpoint to split: captions clearly on one side stay in that half.
    """
    for c0, c1 in col_bounds:
        if c0 - 10 <= x_center <= c1 + 10:
            return c0, c1

    # Fallback: if we have exactly one col entry (full-page single column)
    # but the caption center is clearly to the left or right of midpoint,
    # constrain crop to that half to avoid capturing both columns.
    if len(col_bounds) == 1:
        c0, c1 = col_bounds[0]
        mid = page_rect.x0 + page_rect.width / 2
        if x_center < mid - 20:
            return c0, mid - 5          # left half only
        elif x_center > mid + 20:
            return mid + 5, c1          # right half only
        return c0, c1                   # truly centred → full width

    return col_bounds[0] if col_bounds else (page_rect.x0, page_rect.x1)


def _overlaps_column(lx0: float, lx1: float, col_x0: float, col_x1: float) -> bool:
    """True if the line bbox overlaps the column by at least 30%."""
    overlap = min(lx1, col_x1) - max(lx0, col_x0)
    return overlap / max(1.0, lx1 - lx0) > 0.30


def _strategy_figure_crop(
    pdf_path: Path,
    output_dir: Path,
    dpi: int = 200,
    flat: bool = False,
    pad: float = 6.0,
    min_content_pt: float = 30.0,
) -> list[FigureAsset]:
    """
    v2 — Robust caption-anchored crop with proper column detection.

    Key improvements over v1:
    - Crop x-range uses full COLUMN width (not narrow caption text width).
    - Caption is INCLUDED in the crop (bottom = cap_y1 + pad).
    - Body-text boundary filter threshold uses column width (40%) not caption width (55%).
    - Tables/algorithms try content ABOVE the caption first, then BELOW.
    - If content height is too small either way, fall back to a generous
      full-column slice between surrounding body paragraphs.
    """
    doc = fitz.open(str(pdf_path))
    figs_dir = output_dir if flat else output_dir / "assets"
    figs_dir.mkdir(parents=True, exist_ok=True)

    mat = fitz.Matrix(dpi / 72, dpi / 72)
    assets: list[FigureAsset] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_rect = page.rect
        try:
            page_dict = page.get_text("dict")
        except Exception:
            continue

        # ── Collect all text lines ──────────────────────────────────────────
        # Tuple shape: (x0, y0, x1, y1, text, dominant_font_size)
        lines: list[tuple[float, float, float, float, str, float]] = []
        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for ln in block.get("lines", []):
                spans = ln.get("spans", [])
                if not spans:
                    continue
                txt = "".join(s.get("text", "") for s in spans).strip()
                if not txt:
                    continue
                bx0, by0, bx1, by1 = ln.get("bbox", (0, 0, 0, 0))
                sizes = [s.get("size", 0.0) for s in spans if s.get("size")]
                size = max(sizes) if sizes else 0.0
                lines.append((bx0, by0, bx1, by1, txt, size))

        # ── Detect column layout ────────────────────────────────────────────
        col_bounds = _detect_columns(lines, page_rect)

        # ── Process each caption ────────────────────────────────────────────
        for idx, (lx0, ly0, lx1, ly1, ltxt, lsize) in enumerate(lines):
            m = _CAPTION_RE.match(ltxt)
            if not m:
                continue

            kind = m.group(1).lower().rstrip(".")
            category = ("figure" if kind.startswith("fig")
                        else "algorithm" if kind.startswith("alg")
                        else "table")
            label_num = m.group(2)
            label = f"{category.capitalize()} {label_num}"

            # ── Collect full multi-line caption ─────────────────────────────
            # Stop conditions (any of):
            #   - vertical gap to next line > 8pt
            #   - next line is itself a caption / numbered section heading
            #   - next line's x range diverges from caption's
            #   - next line's font size differs significantly
            #   - next line ends with sentence-final punctuation followed by a
            #     line that starts capitalized AND looks like body prose (>=10
            #     words, no figure-labelish punctuation)
            #   - caption has already grown past 10 lines (sanity ceiling —
            #     real captions in papers basically never exceed this)
            cap_x0, cap_y0, cap_x1, cap_y1 = lx0, ly0, lx1, ly1
            cap_parts = [ltxt]
            prev_y1 = ly1
            cap_font = lsize
            prev_txt = ltxt
            for j in range(idx + 1, len(lines)):
                jx0, jy0, jx1, jy1, jtxt, jsize = lines[j]
                if jy0 - prev_y1 > 8:
                    break
                if _CAPTION_RE.match(jtxt):
                    break
                if re.match(r"^\d+(\.\d+)*\s+[A-Z]", jtxt):
                    break
                if jx1 < lx0 - 4 or jx0 > lx1 + 4:
                    break
                if cap_font > 0 and jsize > 0 and abs(jsize - cap_font) > 0.6:
                    break
                if len(cap_parts) >= 10:
                    break
                # Body-prose start after sentence-final punctuation: if the
                # previous line ends a sentence and this line looks like a
                # new paragraph (>=8 words), treat it as body prose, not
                # caption continuation. Don't require the new line to start
                # with a capital — papers often continue with lowercase
                # ("selection of...") after a figure caption.
                if prev_txt.rstrip().endswith((".", "。", "!", "?")) and len(jtxt.split()) >= 8:
                    break
                cap_x0 = min(cap_x0, jx0)
                cap_x1 = max(cap_x1, jx1)
                cap_y1 = jy1
                cap_parts.append(jtxt)
                prev_y1 = jy1
                prev_txt = jtxt
            cap_text = re.sub(r"\s+", " ", " ".join(cap_parts).strip())

            # ── Determine column x-range ────────────────────────────────────
            cap_cx = (cap_x0 + cap_x1) / 2
            col_x0, col_x1 = _get_column(cap_cx, col_bounds, page_rect)
            col_w = max(1.0, col_x1 - col_x0)

            # Lines that act as a hard boundary: other captions or numbered
            # section headings ("3 Experiments", "4.1 Setup"). These prevent
            # one figure's crop from swallowing a neighboring figure or the
            # surrounding section.
            def _is_boundary(text: str) -> bool:
                if _CAPTION_RE.match(text):
                    return True
                # Section heading: "N", "N.", "N.N", optionally followed by title.
                return bool(re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", text))

            # ── Find body-text / boundary line ABOVE caption ────────────────
            # Body text = line spans >= 40% of column width (avoids axis labels,
            # subfig letters, tick marks that belong to the figure itself).
            top_y = page_rect.y0 + 4
            for ox0, oy0, ox1, oy1, otxt, _osize in lines:
                if oy1 >= cap_y0 - 2:
                    continue
                if not _overlaps_column(ox0, ox1, col_x0, col_x1):
                    continue
                wide_enough = (ox1 - ox0) / col_w >= 0.40
                is_boundary = _is_boundary(otxt)
                if not (wide_enough or is_boundary):
                    continue
                if oy1 > top_y:
                    top_y = oy1

            # Refine top_y: if there's narrow content (table cells, axis ticks,
            # in-figure labels) BETWEEN top_y and our caption, those belong to
            # a SEPARATE figure / table that sits between us and the boundary.
            # In that case, slide top_y DOWN past that interloping content.
            # Detect this as the largest vertical gap inside [top_y, cap_y0]
            # — that gap is usually the whitespace between two figures.
            inter = []
            for ox0, oy0, ox1, oy1, _otxt, _osize in lines:
                if not _overlaps_column(ox0, ox1, col_x0, col_x1):
                    continue
                if oy0 < top_y - 1 or oy1 > cap_y0 + 1:
                    continue
                inter.append((oy0, oy1))
            if inter:
                inter.sort()
                largest_gap = 0.0
                gap_end = None
                cursor = top_y
                # The gap immediately before the caption is usually the gap
                # between the figure body and its own caption — we must NOT
                # treat that as a figure separator. Skip the final gap by
                # only considering gaps that are followed by at least one
                # more in-figure line below them (i.e. they're internal).
                for k, (oy0, oy1) in enumerate(inter):
                    is_internal = oy0 < (cap_y0 - 60)  # not the gap before caption
                    if is_internal and (oy0 - cursor) > largest_gap:
                        largest_gap = oy0 - cursor
                        gap_end = oy0
                    if oy1 > cursor:
                        cursor = oy1
                # Slide top_y only when we see a clearly figure-separating
                # whitespace band (> 40pt). Tighter than before to avoid
                # cutting into figures that have sparse internal text.
                if largest_gap > 40.0 and gap_end is not None:
                    top_y = gap_end - 2

            # Crop for content ABOVE caption — includes caption at bottom
            crop_above = fitz.Rect(
                col_x0 - pad, top_y + 2,
                col_x1 + pad, cap_y1 + pad,
            ).intersect(page_rect)

            # ── Find body-text / boundary line BELOW caption ────────────────
            bottom_y = page_rect.y1 - 4
            for ox0, oy0, ox1, oy1, otxt, _osize in lines:
                if oy0 <= cap_y1 + 2:
                    continue
                if not _overlaps_column(ox0, ox1, col_x0, col_x1):
                    continue
                wide_enough = (ox1 - ox0) / col_w >= 0.40
                is_boundary = _is_boundary(otxt)
                if not (wide_enough or is_boundary):
                    continue
                if oy0 < bottom_y:
                    bottom_y = oy0

            # Crop for content BELOW caption — includes caption at top
            crop_below = fitz.Rect(
                col_x0 - pad, cap_y0 - pad,
                col_x1 + pad, bottom_y - 2,
            ).intersect(page_rect)

            # ── Choose best crop ────────────────────────────────────────────
            if category == "figure":
                # Figures typically have caption below content
                crop = crop_above if crop_above.height >= min_content_pt else crop_below
            else:
                # Tables / algorithms: caption can be above or below content
                if crop_above.height >= min_content_pt and crop_above.height >= crop_below.height:
                    crop = crop_above
                elif crop_below.height >= min_content_pt:
                    crop = crop_below
                else:
                    # Combine both (caption in middle)
                    crop = fitz.Rect(
                        min(crop_above.x0, crop_below.x0),
                        min(crop_above.y0, crop_below.y0),
                        max(crop_above.x1, crop_below.x1),
                        max(crop_above.y1, crop_below.y1),
                    ).intersect(page_rect)

            if crop.width < 30 or crop.height < min_content_pt:
                continue

            try:
                pix = page.get_pixmap(matrix=mat, clip=crop, alpha=False)
            except Exception:
                continue

            slug = label.lower().replace(" ", "")
            dest = figs_dir / f"{slug}_p{page_num + 1}.png"
            if dest.exists():
                dest = figs_dir / f"{slug}_p{page_num + 1}_{len(assets):02d}.png"
            pix.save(str(dest))

            assets.append(FigureAsset(
                path=str(dest),
                rel_path=str(dest.relative_to(output_dir)),
                label=label,
                caption=cap_text,
                category=category,
                source="figure_crop",
                page=page_num,
                width=pix.width,
                height=pix.height,
            ))

    return assets


def _auto_detect_figure_pages(pdf_path: Path) -> list[int]:
    """
    Heuristically find pages that likely contain figures or tables.
    Returns 0-indexed page list.
    """
    keywords = ("Figure", "Fig.", "Table", "Algorithm", "Alg.")
    doc = fitz.open(str(pdf_path))
    result: list[int] = []
    for i, page in enumerate(doc):
        text = page.get_text()
        count = sum(text.count(kw) for kw in keywords)
        if count >= 2:
            result.append(i)
    return result


# ─── Public API ───────────────────────────────────────────────────────────────

def extract_assets(
    source: str,
    output_dir: str = "./paper_assets",
    strategy: str = "auto",
    dpi: int = 150,
    min_width: int = 80,
    min_height: int = 80,
    render_pages: Optional[str] = None,
    cache_dir: Optional[str] = None,
    flat: bool = False,
) -> PaperAssets:
    """
    Extract figures, tables, and page renders from an academic paper.

    Parameters
    ----------
    source : str
        Any of:
          - arXiv abstract URL  (https://arxiv.org/abs/2604.07144)
          - arXiv PDF URL       (https://arxiv.org/pdf/2604.07144v1)
          - arXiv bare ID       (2604.07144  or  2604.07144v1)
          - Any HTTP/S PDF URL
          - Local PDF file path
    output_dir : str
        Root directory where extracted images + assets.json will be saved.
    strategy : str
        "auto"  — try html → pdf_embedded → page_render in order
        "html"  — arXiv HTML only (fails for non-arXiv sources)
        "pdf"   — PDF embedded images only
        "pages" — page renders only
    dpi : int
        Render resolution for page_render strategy (default 150).
    min_width / min_height : int
        Skip embedded images smaller than this (default 80 px each side).
    render_pages : str or None
        Page spec to additionally render, e.g. "1,3-5,8".
        Appended on top of whatever the main strategy produced.
    cache_dir : str or None
        Where to cache downloaded PDFs. Default: system temp.

    Returns
    -------
    PaperAssets
        .figures     — list of FigureAsset
        .to_json()   — full manifest as JSON string
        .summary()   — human-readable summary
        .md_snippets()  — ready-to-paste markdown image refs
        assets.json is also written to output_dir
    """
    out = Path(output_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    arxiv_id = _extract_arxiv_id(source)
    _cache = (
        Path(cache_dir).expanduser()
        if cache_dir
        else Path(tempfile.gettempdir()) / "paper_assets_cache"
    )
    _cache.mkdir(parents=True, exist_ok=True)

    # ── Resolve PDF path ──────────────────────────────────────────────────────
    src_path = Path(source).expanduser()
    if src_path.is_file():
        pdf_path = src_path.resolve()
    else:
        if arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        else:
            pdf_url = source
        try:
            pdf_path = _download_pdf(pdf_url, _cache)
        except Exception as exc:
            return PaperAssets(
                source=source, arxiv_id=arxiv_id, title="", pdf_path="",
                output_dir=str(out), strategy_used="", error=str(exc),
            )

    title = _pdf_metadata_title(pdf_path)
    figures: list[FigureAsset] = []
    strategy_used = ""

    # ── Run strategies ────────────────────────────────────────────────────────
    strat_order = {
        "auto":   ["html", "figures", "pdf", "pages"],
        "html":   ["html"],
        "pdf":    ["pdf"],
        "pages":  ["pages"],
        "figures": ["figures"],
    }.get(strategy, ["html", "figures", "pdf", "pages"])

    for strat in strat_order:
        if strat == "html":
            if not arxiv_id:
                continue
            try:
                t, figs = _strategy_html(arxiv_id, out, flat=flat)
                if figs:
                    figures = figs
                    title = title or t
                    strategy_used = "html"
                    break
            except Exception:
                continue

        elif strat == "figures":
            figs = _strategy_figure_crop(pdf_path, out, dpi=max(dpi, 180), flat=flat)
            if figs:
                figures = figs
                strategy_used = "figure_crop"
                break

        elif strat == "pdf":
            figs = _strategy_pdf_embedded(pdf_path, out, min_width, min_height, flat=flat)
            if figs:
                figures = figs
                strategy_used = "pdf_embedded"
                break

        elif strat == "pages":
            pages = _auto_detect_figure_pages(pdf_path)
            if not pages:
                doc = fitz.open(str(pdf_path))
                pages = list(range(len(doc)))
            figs = _strategy_page_render(pdf_path, out, pages, dpi, flat=flat)
            if figs:
                figures = figs
                strategy_used = "page_render"
                break

    # ── Optional explicit page renders (additive) ─────────────────────────────
    if render_pages:
        page_indices = _parse_page_spec(render_pages)
        extra = _strategy_page_render(pdf_path, out, page_indices, dpi, flat=flat)
        # Avoid duplicating pages already rendered
        existing_pages = {f.page for f in figures if f.source == "page_render"}
        extra = [f for f in extra if f.page not in existing_pages]
        figures.extend(extra)
        if not strategy_used:
            strategy_used = "page_render"

    # ── Save manifest ─────────────────────────────────────────────────────────
    result = PaperAssets(
        source=source,
        arxiv_id=arxiv_id,
        title=title,
        pdf_path=str(pdf_path),
        output_dir=str(out),
        strategy_used=strategy_used or "none",
        figures=figures,
    )
    (out / "assets.json").write_text(result.to_json(), encoding="utf-8")
    return result


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="paper_assets",
        description=(
            "Extract figures, tables, and page renders from academic papers.\n"
            "Supports arXiv URLs, arXiv IDs, HTTP PDF URLs, and local PDF paths."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  paper_assets.py https://arxiv.org/abs/2604.07144\n"
            "  paper_assets.py 2604.07144v1 --output-dir ~/Desktop/assets --format summary\n"
            "  paper_assets.py paper.pdf --strategy pages --render-pages 2-5 --dpi 200\n"
            "  paper_assets.py https://arxiv.org/abs/2604.07144 --render-pages 3,5,7\n"
        ),
    )
    p.add_argument("source", help="arXiv URL/ID, HTTP PDF URL, or local PDF path")
    p.add_argument(
        "--output-dir", default="./paper_assets", metavar="DIR",
        help="Directory to save assets (default: ./paper_assets)",
    )
    p.add_argument(
        "--strategy", choices=["auto", "html", "pdf", "pages", "figures"], default="auto",
        help="Extraction strategy (default: auto tries html→figures→pdf→pages)",
    )
    p.add_argument("--dpi", type=int, default=150, help="DPI for page renders (default: 150)")
    p.add_argument(
        "--min-width", type=int, default=80, dest="min_width",
        help="Min image width to keep in px (default: 80)",
    )
    p.add_argument(
        "--min-height", type=int, default=80, dest="min_height",
        help="Min image height to keep in px (default: 80)",
    )
    p.add_argument(
        "--render-pages", metavar="SPEC", dest="render_pages",
        help='Also render specific pages, e.g. "1,3-5,8". Stacks with --strategy.',
    )
    p.add_argument(
        "--cache-dir", metavar="DIR", dest="cache_dir",
        help="Cache downloaded PDFs here (default: system temp)",
    )
    p.add_argument(
        "--format", choices=["json", "summary", "md"], default="json",
        help="Output format: json (default), summary (human), or md (image refs)",
    )
    p.add_argument(
        "--flat", action="store_true", default=False,
        help="Save all images directly to output-dir (no figures/ or pages/ subdirs)",
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()
    result = extract_assets(
        source=args.source,
        output_dir=args.output_dir,
        strategy=args.strategy,
        dpi=args.dpi,
        min_width=args.min_width,
        min_height=args.min_height,
        render_pages=args.render_pages,
        cache_dir=args.cache_dir,
        flat=args.flat,
    )
    if result.error:
        print(f"ERROR: {result.error}", file=sys.stderr)
        sys.exit(1)

    if args.format == "summary":
        print(result.summary())
    elif args.format == "md":
        print(result.md_snippets())
    else:
        print(result.to_json())


if __name__ == "__main__":
    main()
