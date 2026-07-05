#!/usr/bin/env python3
"""Flatten PDF transparency (soft masks / transparency groups) in place.

Lulu's print check strongly recommends flattening all transparency before
upload. This project's only source of transparency is the TikZ `path
fading` used for the cover art's soft-edged fade bands (see kookboek.sty /
cover/cover.tex, both under `\\tikzfading[name=fade-vanish-*]`). Rather than
flattening the whole document — which forces Ghostscript to rasterize
every page, including all body text, once the target PDF version drops
transparency support — this extracts only the pages that actually contain
transparency, flattens just those through Ghostscript, and splices them
back into the original PDF. Pages with no transparency keep their
embedded vector text untouched.

Usage:
    python3 scripts/flatten_transparency.py PDF [--dpi 450]

Requires `qpdf` and Ghostscript (`gs`) on PATH. A no-op if the PDF has no
transparency, or if either tool is missing (build.sh treats that as
non-fatal, matching how it treats a missing PyMuPDF for the lint step).
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import fitz
except ImportError:
    fitz = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_transparency import find_transparent_pages

DEFAULT_DPI = 450


def _run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed:\n{result.stdout.decode(errors='replace')}")


def _contiguous_runs(pages):
    runs = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
        else:
            runs.append((start, prev))
            start = prev = p
    runs.append((start, prev))
    return runs


def flatten(pdf_path, dpi):
    if fitz is None:
        print("note: skipping transparency flatten — install pymupdf", file=sys.stderr)
        return
    if not shutil.which("qpdf") or not shutil.which("gs"):
        print("note: skipping transparency flatten — needs qpdf and ghostscript (gs)", file=sys.stderr)
        return

    doc = fitz.open(pdf_path)
    total = doc.page_count
    transparent = find_transparent_pages(doc)
    toc = doc.get_toc(simple=True)
    doc.close()
    if not transparent:
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        parts = []  # (source_path, page_range_in_that_source), in final page order
        cursor = 1
        for start, end in _contiguous_runs(transparent):
            if start > cursor:
                parts.append((pdf_path, f"{cursor}-{start - 1}"))
            extracted = tmp / f"pages-{start}-{end}.pdf"
            _run(["qpdf", "--empty", "--pages", str(pdf_path), f"{start}-{end}", "--", str(extracted)])
            flattened = tmp / f"flat-{start}-{end}.pdf"
            _run([
                "gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.3",
                f"-r{dpi}",
                f"-sOutputFile={flattened}",
                str(extracted),
            ])
            parts.append((flattened, "1-z"))
            cursor = end + 1
        if cursor <= total:
            parts.append((pdf_path, f"{cursor}-{total}"))

        merged = tmp / "merged.pdf"
        merge_cmd = ["qpdf", "--empty", "--pages"]
        for source, page_range in parts:
            merge_cmd += [str(source), page_range]
        merge_cmd += ["--", str(merged)]
        _run(merge_cmd)

        if toc:
            # qpdf's --pages merge drops document-level bookmarks even when,
            # as here, the page count and order are unchanged — restore them
            # by page index rather than relying on qpdf to carry them over.
            merged_doc = fitz.open(merged)
            merged_doc.set_toc(toc)
            with_toc = tmp / "with_toc.pdf"
            merged_doc.save(with_toc)
            merged_doc.close()
            merged = with_toc

        shutil.copyfile(merged, pdf_path)

    print(f"flattened transparency on page(s) {', '.join(str(p) for p in transparent)} of {pdf_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="flatten resolution (default: %(default)s)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"error: {pdf_path} not found", file=sys.stderr)
        return 2
    flatten(pdf_path, args.dpi)
    return 0


if __name__ == "__main__":
    sys.exit(main())
