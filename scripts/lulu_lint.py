#!/usr/bin/env python3
"""Check the built cookbook PDF (and its LaTeX source) against Lulu.com print
requirements: trim size, embedded fonts, image resolution, full-bleed safety,
margins, page count, and single-step widow pages.

Usage:
    python3 scripts/lulu_lint.py [PDF] [--repo-root DIR] [--strict]

Errors are things that will actually break a Lulu print job (wrong trim
size, unembedded fonts, full-bleed art without a bleed margin, margins
below Lulu's minimum). Warnings are things worth knowing about but that
are expected while the book is still a work in progress (unfinished
recipes, low-resolution art, an odd page count). Pass --strict to also
fail on warnings, e.g. right before uploading to Lulu.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("error: this script needs PyMuPDF (`pip install pymupdf`)", file=sys.stderr)
    sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_transparency import find_transparent_pages

MM_PER_INCH = 25.4
PT_PER_MM = 72 / MM_PER_INCH

TRIM_WIDTH_MM = 189.0  # Lulu Crown Quarto, per CLAUDE.md / README
TRIM_HEIGHT_MM = 246.0
SAFETY_MARGIN_MM = 12.7  # Lulu's 0.5 in minimum safety margin
BLEED_MM = 3.18  # Lulu's 0.125 in bleed requirement
MIN_PAGES_HARDCOVER = 24
MIN_PAGES_PAPERBACK = 32
MIN_DPI = 300
EDGE_TOLERANCE_PT = 1.0
PAPER_COLOR_TOLERANCE = 10  # per-channel, out of 255 — a flattened page's
# blank margin renders as a solid image touching the trim edge, which looks
# identical to real full-bleed art unless we check whether that edge is
# actually just the paper background colour.

PLACEHOLDER_MACROS = {
    r"\heroplaceholder": "hero illustration not finished",
    r"\ingredientsketch": "ingredient sketch not finished",
    r"\writelines": "method not written yet",
}

# Bookmark titles that mark front/back matter rather than a category chapter.
NON_CHAPTER_TITLES = {"Inhoud", "Register", "Voorwoord", "Kookboek", "Index"}

BOILERPLATE_LINE_RE = re.compile(r"^(Kookboek van onze familie|—\s*\d+\s*—|\d+)$")
# A rendered \begin{steps} item: "8 Zet de oven..." — digits, then a capital
# letter starting the sentence. Deliberately excludes ingredient lines like
# "397 ml gezoete..." (unit abbreviations are lowercase in this book).
STEP_LINE_RE = re.compile(r"^\d{1,2}\s+[A-ZÀ-ÖØ-Þ]")


def mm(pt):
    return pt / PT_PER_MM


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def _paper_rgb(sty_path):
    """Parse kookboek.sty's `\\definecolor{paper}{HTML}{XXXXXX}` so the
    bleed check can tell blank paper-coloured margin apart from real
    artwork touching the trim edge. Falls back to white if not found."""
    try:
        text = sty_path.read_text(encoding="utf-8")
    except OSError:
        return (255, 255, 255)
    match = re.search(r"\\definecolor\{paper\}\{HTML\}\{([0-9A-Fa-f]{6})\}", text)
    if not match:
        return (255, 255, 255)
    hex_color = match.group(1)
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _touching_edge_is_blank(page, pw, ph, touches, paper_rgb):
    """Render the page at low resolution and sample its touching edge(s) —
    a flattened page (see scripts/flatten_transparency.py) always produces
    one image spanning the full page, even where the actual content is
    just blank paper-coloured margin, so the raw bbox-touches-edge check
    alone can't distinguish that from real full-bleed art."""
    touches_left, touches_right, touches_top, touches_bottom = touches
    pix = page.get_pixmap(dpi=72)
    w, h = pix.width, pix.height
    if w == 0 or h == 0:
        return False
    samples = []
    step = max(1, w // 40)
    if touches_top:
        samples += [pix.pixel(x, 0) for x in range(0, w, step)]
    if touches_bottom:
        samples += [pix.pixel(x, h - 1) for x in range(0, w, step)]
    step = max(1, h // 40)
    if touches_left:
        samples += [pix.pixel(0, y) for y in range(0, h, step)]
    if touches_right:
        samples += [pix.pixel(w - 1, y) for y in range(0, h, step)]
    return all(
        all(abs(c - p) <= PAPER_COLOR_TOLERANCE for c, p in zip(px[:3], paper_rgb)) for px in samples
    )


def check_pdf(pdf_path, report, paper_rgb=(255, 255, 255)):
    doc = fitz.open(pdf_path)
    if doc.page_count == 0:
        report.error(f"{pdf_path}: PDF has no pages")
        return

    expected_w = TRIM_WIDTH_MM * PT_PER_MM
    expected_h = TRIM_HEIGHT_MM * PT_PER_MM
    mismatched = [
        (i, mm(page.rect.width), mm(page.rect.height))
        for i, page in enumerate(doc, start=1)
        if abs(page.rect.width - expected_w) > 1 or abs(page.rect.height - expected_h) > 1
    ]
    if mismatched:
        sample = ", ".join(f"page {i} ({w:.1f}x{h:.1f}mm)" for i, w, h in mismatched[:5])
        report.error(
            f"{len(mismatched)} page(s) don't match the "
            f"{TRIM_WIDTH_MM:.0f}x{TRIM_HEIGHT_MM:.0f}mm trim size: {sample}"
        )

    n = doc.page_count
    if n < MIN_PAGES_HARDCOVER:
        report.error(f"only {n} page(s) — below Lulu's {MIN_PAGES_HARDCOVER}-page hardcover minimum")
    elif n < MIN_PAGES_PAPERBACK:
        report.warn(
            f"only {n} page(s) — below Lulu's {MIN_PAGES_PAPERBACK}-page paperback minimum "
            f"(the {MIN_PAGES_HARDCOVER}-page hardcover minimum is met)"
        )
    elif n % 4 != 0:
        report.warn(f"{n} pages is not a multiple of 4 — Lulu may pad with blank pages")

    unembedded = set()
    for page in doc:
        for _xref, ext, _ftype, basefont, _name, _encoding in page.get_fonts(full=False):
            if ext == "n/a":
                unembedded.add(basefont)
    if unembedded:
        report.error("font(s) not embedded: " + ", ".join(sorted(unembedded)))

    low_dpi = []
    bleed_risk_pages = set()
    for pno, page in enumerate(doc, start=1):
        pw, ph = page.rect.width, page.rect.height
        for info in page.get_image_info(xrefs=True):
            bbox = fitz.Rect(info["bbox"])
            iw, ih = info.get("width", 0), info.get("height", 0)
            if iw and ih and bbox.width > 0 and bbox.height > 0:
                dpi_x = iw / (bbox.width / 72)
                dpi_y = ih / (bbox.height / 72)
                effective_dpi = min(dpi_x, dpi_y)
                if effective_dpi < MIN_DPI:
                    low_dpi.append((pno, effective_dpi))

            touches_left = bbox.x0 <= EDGE_TOLERANCE_PT
            touches_right = bbox.x1 >= pw - EDGE_TOLERANCE_PT
            touches_top = bbox.y0 <= EDGE_TOLERANCE_PT
            touches_bottom = bbox.y1 >= ph - EDGE_TOLERANCE_PT
            touches = (touches_left, touches_right, touches_top, touches_bottom)
            if (touches_left and touches_right) or (touches_top and touches_bottom):
                if not _touching_edge_is_blank(page, pw, ph, touches, paper_rgb):
                    bleed_risk_pages.add(pno)

    if low_dpi:
        worst = sorted(low_dpi, key=lambda t: t[1])[:5]
        detail = ", ".join(f"page {p} (~{d:.0f} dpi)" for p, d in worst)
        report.warn(f"{len(low_dpi)} image placement(s) below {MIN_DPI} dpi at printed size: {detail}")

    if bleed_risk_pages and not mismatched:
        # Page size matches exact trim (no bleed margin) but art touches the edge.
        pages = ", ".join(str(p) for p in sorted(bleed_risk_pages)[:5])
        report.error(
            f"full-bleed image(s) touch the page edge on page(s) {pages}, but pages are sized "
            f"to exact trim ({TRIM_WIDTH_MM:.0f}x{TRIM_HEIGHT_MM:.0f}mm) with no "
            f"{BLEED_MM:.2f}mm bleed margin — Lulu needs bleed added to the page size for "
            "full-bleed artwork, or the image should be inset from the edge"
        )

    doc.close()


def check_transparency(pdf_path, report):
    doc = fitz.open(pdf_path)
    try:
        pages = find_transparent_pages(doc)
    finally:
        doc.close()
    if pages:
        detail = ", ".join(str(p) for p in pages[:10])
        report.warn(
            f"{len(pages)} page(s) paint with PDF transparency (soft masks / transparency "
            f"groups) — Lulu strongly recommends flattening all transparency before upload: "
            f"{detail}. Run scripts/flatten_transparency.py on the PDF to fix it (build.sh "
            "does this automatically before this check runs)"
        )


def check_geometry(sty_path, report):
    if not sty_path.exists():
        report.warn(f"{sty_path}: not found, skipped margin check")
        return
    text = sty_path.read_text(encoding="utf-8")
    match = re.search(r"\\RequirePackage\[(.*?)\]\{geometry\}", text, re.S)
    if not match:
        report.warn(f"{sty_path}: couldn't find a geometry configuration to check margins")
        return
    opts = dict(re.findall(r"(top|bottom|inner|outer)\s*=\s*([\d.]+)cm", match.group(1)))
    for side in ("top", "bottom", "inner", "outer"):
        if side not in opts:
            continue
        value_mm = float(opts[side]) * 10
        if value_mm < SAFETY_MARGIN_MM:
            report.error(
                f"{sty_path}: {side} margin is {value_mm:.1f}mm, below Lulu's "
                f"{SAFETY_MARGIN_MM:.1f}mm safety margin minimum"
            )


def _recipe_kinds(main_tex_path):
    """Read main.tex and return, in document order, 'subchapter' or 'recipe'
    for each \\subchapter{...} and \\input{recipes/...} line. Mirrors
    scripts/extract_index.py's extract_depth1_kinds — needed because the PDF
    bookmark tree doesn't itself distinguish a subchapter divider from a
    recipe, both showing up as depth-1 (level-2) entries under a chapter."""
    kinds = []
    if not main_tex_path.exists():
        return kinds
    for line in main_tex_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        if re.search(r"\\subchapter\{", stripped):
            kinds.append("subchapter")
        elif re.search(r"\\input\{recipes/", stripped):
            kinds.append("recipe")
    return kinds


def _recipe_page_ranges(doc, main_tex_path):
    """Return [{"title", "page", "endPage"}, ...] for every recipe, using the
    PDF's own bookmark outline (chapters = level 1, recipes/subchapters =
    level 2). A lighter-weight reimplementation of extract_index.py's
    extract_recipes that uses PyMuPDF instead of pypdf, so this script keeps
    its single existing dependency."""
    kinds = iter(_recipe_kinds(main_tex_path))
    chapter = None
    recipes = []
    boundaries = []
    for level, title, page in doc.get_toc(simple=True):
        title = title.strip()
        if level == 1:
            if page:
                boundaries.append(page)
            if title not in NON_CHAPTER_TITLES:
                chapter = title
        elif level >= 2 and chapter and page:
            kind = next(kinds, "recipe")
            if kind == "subchapter":
                boundaries.append(page)
            else:
                recipes.append({"title": title, "page": page})

    total_pages = doc.page_count
    for i, recipe in enumerate(recipes):
        sp = recipe["page"]
        candidates = [b for b in boundaries if b > sp]
        if i + 1 < len(recipes):
            candidates.append(recipes[i + 1]["page"])
        recipe["endPage"] = (min(candidates) - 1) if candidates else total_pages
    return recipes


def check_orphan_pages(pdf_path, main_tex_path, report):
    """Flag recipes whose text spills onto a next page that ends up holding
    only a single leftover step — a typographic widow that reads as a
    mistake (a near-blank page with one sentence on it) rather than a
    deliberate two-page recipe."""
    doc = fitz.open(pdf_path)
    try:
        recipes = _recipe_page_ranges(doc, main_tex_path)
        if not recipes:
            return
        widows = []
        for recipe in recipes:
            if recipe["endPage"] <= recipe["page"]:
                continue
            page = doc[recipe["endPage"] - 1]
            lines = [l.strip() for l in page.get_text().split("\n") if l.strip()]
            content = [l for l in lines if not BOILERPLATE_LINE_RE.match(l)]
            step_count = sum(1 for l in content if STEP_LINE_RE.match(l))
            # Require at least one recognizable step line before trusting this
            # page belongs to the recipe at all — guards against the page
            # range spilling into the next chapter/Register's own opening
            # page (a known quirk of the bookmark-derived page boundaries).
            if step_count == 1:
                widows.append((recipe["title"], recipe["page"], recipe["endPage"]))
        if widows:
            detail = "; ".join(f"{t!r} (p.{sp}–{ep})" for t, sp, ep in widows[:8])
            report.warn(
                f"{len(widows)} recipe(s) leave just one step behind on their last page "
                f"— consider tightening the text so it fits on one page, or breaking the "
                f"page differently: {detail}"
            )
    finally:
        doc.close()


def check_placeholders(recipes_dir, report):
    if not recipes_dir.exists():
        return
    todo = []
    for path in sorted(recipes_dir.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        for macro, description in PLACEHOLDER_MACROS.items():
            if macro in text:
                todo.append(f"{path.name}: {description}")
    if todo:
        report.warn(
            f"{len(todo)} recipe file(s) still contain print-readiness placeholders:\n    - "
            + "\n    - ".join(todo)
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", nargs="?", default="main.pdf", help="path to the built PDF (default: main.pdf)")
    parser.add_argument("--repo-root", default=".", help="repository root (default: current directory)")
    parser.add_argument(
        "--strict", action="store_true", help="also fail on warnings (use before a real Lulu upload)"
    )
    args = parser.parse_args()

    root = Path(args.repo_root)
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"error: {pdf_path} not found — build the book first (./build.sh)", file=sys.stderr)
        return 2

    report = Report()
    check_pdf(pdf_path, report, paper_rgb=_paper_rgb(root / "kookboek.sty"))
    check_transparency(pdf_path, report)
    check_geometry(root / "kookboek.sty", report)
    check_orphan_pages(pdf_path, root / "main.tex", report)
    check_placeholders(root / "recipes", report)

    if report.errors:
        print(f"{len(report.errors)} error(s):")
        for e in report.errors:
            print(f"  ERROR: {e}")
    if report.warnings:
        print(f"{len(report.warnings)} warning(s):")
        for w in report.warnings:
            print(f"  WARNING: {w}")
    if not report.errors and not report.warnings:
        print("Lulu print check passed with no issues.")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
