#!/usr/bin/env python3
"""Produce a low-resolution copy of the print PDF for the website viewer.

The print PDF (`KookboekFamilieSpoor.pdf`) embeds images at 300-600 PPI to
meet Lulu's print requirements (see `scripts/lulu_lint.py`). That's far more
than a browser needs to render pages into a canvas at screen resolution, so
`docs/index.html` fetches this downsampled copy instead for the in-browser
viewer and the per-recipe "Recept" download — only the "Volledig boek" button
links straight to the full-resolution print PDF. Downsampling images and
re-compressing with Ghostscript's `pdfwrite` device cuts file size sharply
with no visible loss at screen zoom levels, so the book loads and page-flips
much faster online.

Usage:
    python3 scripts/make_web_pdf.py PDF_IN PDF_OUT [--dpi 120] [--quality 60]

Requires Ghostscript (`gs`) on PATH.
"""

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_DPI = 120
DEFAULT_JPEG_QUALITY = 60


def make_web_pdf(src: Path, dst: Path, dpi: int, quality: int) -> None:
    cmd = [
        "gs",
        "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        "-dAutoRotatePages=/None",
        "-dDownsampleColorImages=true",
        "-dColorImageDownsampleType=/Bicubic",
        f"-dColorImageResolution={dpi}",
        "-dDownsampleGrayImages=true",
        "-dGrayImageDownsampleType=/Bicubic",
        f"-dGrayImageResolution={dpi}",
        "-dDownsampleMonoImages=true",
        "-dMonoImageDownsampleType=/Bicubic",
        f"-dMonoImageResolution={max(dpi, 300)}",
        "-dColorImageFilter=/DCTEncode",
        "-dGrayImageFilter=/DCTEncode",
        f"-dJPEGQ={quality}",
        "-dEmbedAllFonts=true",
        "-dSubsetFonts=true",
        "-dCompressFonts=true",
        f"-sOutputFile={dst}",
        str(src),
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise RuntimeError(f"ghostscript failed:\n{result.stdout.decode(errors='replace')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("src", type=Path, help="print-resolution source PDF")
    parser.add_argument("dst", type=Path, help="output path for the web PDF")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help=f"target image resolution (default {DEFAULT_DPI})")
    parser.add_argument("--quality", type=int, default=DEFAULT_JPEG_QUALITY, help=f"JPEG quality 0-100 (default {DEFAULT_JPEG_QUALITY})")
    args = parser.parse_args()

    if not args.src.exists():
        print(f"error: {args.src} does not exist", file=sys.stderr)
        return 1

    make_web_pdf(args.src, args.dst, args.dpi, args.quality)

    before = args.src.stat().st_size
    after = args.dst.stat().st_size
    pct = 100 * (1 - after / before) if before else 0
    print(f"{args.src} -> {args.dst}: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB ({pct:.0f}% smaller)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
