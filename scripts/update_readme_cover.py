#!/usr/bin/env python3
"""Regenerate docs/cover-preview.png (the README's cover photo) from the
built interior PDF's title page (page 1), which carries the same photo and
title block as the wraparound cover's front panel.

Usage:
    python3 scripts/update_readme_cover.py [INTERIOR_PDF] [--repo-root DIR]

Requires the interior PDF to already be built (see build.sh).
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("error: this script needs PyMuPDF (`pip install pymupdf`)", file=sys.stderr)
    sys.exit(1)

_PREVIEW_WIDTH_PX = 900  # matches the previous hand-generated preview


def render_title_page(interior_pdf_path, out_path, width_px=_PREVIEW_WIDTH_PX):
    doc = fitz.open(interior_pdf_path)
    page = doc[0]

    zoom = width_px / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    pix.save(out_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("interior_pdf", nargs="?", default="KookboekFamilieSpoor.pdf")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", default=None, help="output PNG path (default: docs/cover-preview.png)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    interior_pdf_path = Path(args.interior_pdf)
    if not interior_pdf_path.is_absolute():
        interior_pdf_path = repo_root / interior_pdf_path
    out_path = Path(args.out) if args.out else repo_root / "docs" / "cover-preview.png"

    if not interior_pdf_path.exists():
        print(f"error: {interior_pdf_path} doesn't exist — build it first (see build.sh)", file=sys.stderr)
        sys.exit(1)

    render_title_page(interior_pdf_path, out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
