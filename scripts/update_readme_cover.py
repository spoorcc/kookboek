#!/usr/bin/env python3
"""Regenerate docs/cover-preview.png (the README's cover photo) from the
built wraparound cover PDF's front panel — the mosaic of every recipe's
hero photo behind the title block, cropped out of the back/spine/front
spread (see cover/cover.tex).

Usage:
    python3 scripts/update_readme_cover.py [COVER_PDF] [--repo-root DIR]

Requires the cover PDF to already be built (see build.sh).
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("error: this script needs PyMuPDF (`pip install pymupdf`)", file=sys.stderr)
    sys.exit(1)

_PREVIEW_WIDTH_PX = 900  # matches the previous hand-generated preview

# Fixed by the Lulu hardcover casewrap trim this book uses (see the header
# comment block in cover/cover.tex) — doesn't change with page count, unlike
# \spinew, which is read straight from cover.tex below to stay in sync with
# whatever hardcover spine-width bucket the current page count falls into.
_TRIMW_MM = 195.33
_BLEED_MM = 15.87
_PANELW_MM = _TRIMW_MM + _BLEED_MM


def _read_spinew_mm(cover_tex_path):
    text = cover_tex_path.read_text(encoding="utf-8")
    m = re.search(r"\\setlength\\spinew\{([\d.]+)mm\}", text)
    if not m:
        raise ValueError(f"couldn't find \\setlength\\spinew{{...mm}} in {cover_tex_path}")
    return float(m.group(1))


def render_front_panel(cover_pdf_path, cover_tex_path, out_path, width_px=_PREVIEW_WIDTH_PX):
    spinew_mm = _read_spinew_mm(cover_tex_path)
    spread_mm = 2 * _PANELW_MM + spinew_mm
    front_left_frac = (_PANELW_MM + spinew_mm) / spread_mm

    doc = fitz.open(cover_pdf_path)
    page = doc[0]
    front_rect = fitz.Rect(page.rect.width * front_left_frac, 0, page.rect.width, page.rect.height)

    zoom = width_px / front_rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=front_rect)
    pix.save(out_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cover_pdf", nargs="?", default="KookboekFamilieSpoor-cover.pdf")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--cover-tex", default=None, help="path to cover/cover.tex (default: <repo-root>/cover/cover.tex)")
    parser.add_argument("--out", default=None, help="output PNG path (default: docs/cover-preview.png)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    cover_pdf_path = Path(args.cover_pdf)
    if not cover_pdf_path.is_absolute():
        cover_pdf_path = repo_root / cover_pdf_path
    cover_tex_path = Path(args.cover_tex) if args.cover_tex else repo_root / "cover" / "cover.tex"
    out_path = Path(args.out) if args.out else repo_root / "docs" / "cover-preview.png"

    if not cover_pdf_path.exists():
        print(f"error: {cover_pdf_path} doesn't exist — build it first (see build.sh)", file=sys.stderr)
        sys.exit(1)
    if not cover_tex_path.exists():
        print(f"error: {cover_tex_path} doesn't exist", file=sys.stderr)
        sys.exit(1)

    render_front_panel(cover_pdf_path, cover_tex_path, out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
