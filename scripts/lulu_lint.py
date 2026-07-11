#!/usr/bin/env python3
"""Check the built cookbook PDF (and its LaTeX source) against Lulu.com print
requirements as documented in Lulu's Book Creation Guide: trim size, embedded
fonts, image resolution (300-600 PPI), PDF encryption, full-bleed safety,
safety/gutter margins, page count, single-step widow pages, and (when the
wraparound cover PDF is present) cover-specific checks including hardcover
spine width against Lulu's page-count-to-spine table.

Usage:
    python3 scripts/lulu_lint.py [PDF] [--cover PDF] [--repo-root DIR] [--strict]

Errors are things that will actually break a Lulu print job (wrong trim
size, unembedded fonts, encrypted PDF, full-bleed art without a bleed
margin, margins below Lulu's minimum, page count over Lulu's cap).
Warnings are things worth knowing about but that are expected while the
book is still a work in progress (unfinished recipes, low- or high-DPI
art, an odd page count, an inner margin below the recommended gutter for
the current page count). Pass --strict to also fail on warnings, e.g.
right before uploading to Lulu.
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

# Lulu Crown Quarto text-block trim, per the "Book Trim Sizes" table on
# page 11 of Lulu's Book Creation Guide (also cross-referenced in
# CLAUDE.md / README). The "with bleed" pair is the same row's Interior
# File Dimensions - With Bleed column, accepted as an alternative trim
# for the case where the interior file adds Lulu's bleed to the page size.
TRIM_WIDTH_MM = 189.0
TRIM_HEIGHT_MM = 246.0
TRIM_WIDTH_MM_WITH_BLEED = 195.0
TRIM_HEIGHT_MM_WITH_BLEED = 252.0

SAFETY_MARGIN_MM = 12.7  # Lulu's 0.5 in minimum safety margin (guide p8, p23)
BLEED_MM = 3.18  # Lulu's 0.125 in bleed (guide p10, p24)
MIN_GUTTER_MM = 2.08  # Lulu's 0.2 in absolute minimum gutter (guide p23)

MIN_PAGES_HARDCOVER = 24  # Lulu Book Creation Guide p13
MIN_PAGES_PAPERBACK = 32
MAX_PAGES = 800  # Lulu's hardcover spine table (guide p14) tops out at 800
MAX_SPINE_TEXT_PAGES = 80  # guide p17: no spine text if the book is ≤ 80 pages
MIN_DPI = 300  # Lulu Book Creation Guide p4, p23
MAX_DPI = 600  # guide p23, p24: "Embedded images ... not exceeding 600 PPI resolution"
EDGE_TOLERANCE_PT = 1.0
PAPER_COLOR_TOLERANCE = 10  # per-channel, out of 255 — a flattened page's
# blank margin renders as a solid image touching the trim edge, which looks
# identical to real full-bleed art unless we check whether that edge is
# actually just the paper background colour.

# Lulu Book Creation Guide p9, "Gutter Additions" table. Each entry is
# (max_pages_in_bucket, gutter_added_to_safety_mm,
#  recommended_total_inside_margin_mm). The book's `geometry` `inner`
# value is compared to the recommended total inside for its page count.
GUTTER_TABLE = [
    (60, 0, 13),
    (150, 3, 16),
    (400, 13, 25),
    (600, 16, 29),
    (float("inf"), 19, 32),
]

# Lulu Book Creation Guide p14, "Hardcover Covers" spine width table.
# Each entry is (min_pages, max_pages, spine_mm). Books with fewer than
# 24 pages are ineligible for a hardcover binding (spine "N/A" row).
HARDCOVER_SPINE_TABLE = [
    (24, 84, 6),
    (85, 140, 13),
    (141, 168, 16),
    (169, 194, 17),
    (195, 222, 19),
    (223, 250, 21),
    (251, 278, 22),
    (279, 306, 24),
    (307, 334, 25),
    (335, 360, 27),
    (361, 388, 29),
    (389, 416, 30),
    (417, 444, 32),
    (445, 472, 33),
    (473, 500, 35),
    (501, 528, 37),
    (529, 556, 38),
    (557, 582, 40),
    (583, 610, 41),
    (611, 638, 43),
    (639, 666, 44),
    (667, 694, 46),
    (695, 722, 48),
    (723, 750, 49),
    (751, 778, 51),
    (779, 799, 52),
    (800, 800, 54),
]

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


def _matches_size(page, w_mm, h_mm):
    expected_w = w_mm * PT_PER_MM
    expected_h = h_mm * PT_PER_MM
    return abs(page.rect.width - expected_w) <= 1 and abs(page.rect.height - expected_h) <= 1


def _check_encryption(pdf_path, doc, report):
    """Lulu Book Creation Guide p23/p24 (Interior + Cover File Specifications):
    "Do NOT use any security/password file protection". Fail loudly rather than
    letting an encrypted PDF get uploaded and rejected downstream."""
    if doc.is_encrypted or doc.needs_pass:
        report.error(
            f"{pdf_path}: PDF is encrypted or password-protected — Lulu forbids "
            "security/password file protection on print-ready files"
        )
        return True
    return False


def _check_fonts_embedded(pdf_path, doc, report):
    unembedded = set()
    for page in doc:
        for _xref, ext, _ftype, basefont, _name, _encoding in page.get_fonts(full=False):
            if ext == "n/a":
                unembedded.add(basefont)
    if unembedded:
        report.error(f"{pdf_path}: font(s) not embedded: " + ", ".join(sorted(unembedded)))


def check_pdf(pdf_path, report, paper_rgb=(255, 255, 255)):
    doc = fitz.open(pdf_path)
    try:
        if _check_encryption(pdf_path, doc, report):
            return 0
        if doc.page_count == 0:
            report.error(f"{pdf_path}: PDF has no pages")
            return 0

        # Trim size — accept either the exact text-block trim (guide p11
        # "Interior File Dimensions - No Bleed") or the with-bleed size
        # (same row's "Interior File Dimensions - With Bleed" column).
        # Every page must use the SAME size; Lulu won't accept a mixed
        # trim within one file.
        mismatched = []
        pages_no_bleed = 0
        pages_with_bleed = 0
        for i, page in enumerate(doc, start=1):
            if _matches_size(page, TRIM_WIDTH_MM, TRIM_HEIGHT_MM):
                pages_no_bleed += 1
                continue
            if _matches_size(page, TRIM_WIDTH_MM_WITH_BLEED, TRIM_HEIGHT_MM_WITH_BLEED):
                pages_with_bleed += 1
                continue
            mismatched.append((i, mm(page.rect.width), mm(page.rect.height)))
        if mismatched:
            sample = ", ".join(f"page {i} ({w:.1f}x{h:.1f}mm)" for i, w, h in mismatched[:5])
            report.error(
                f"{len(mismatched)} page(s) don't match the Lulu Crown Quarto trim size "
                f"({TRIM_WIDTH_MM:.0f}x{TRIM_HEIGHT_MM:.0f}mm no-bleed or "
                f"{TRIM_WIDTH_MM_WITH_BLEED:.0f}x{TRIM_HEIGHT_MM_WITH_BLEED:.0f}mm with bleed): "
                f"{sample}"
            )
        if pages_no_bleed > 0 and pages_with_bleed > 0:
            report.error(
                f"PDF mixes {pages_no_bleed} page(s) at exact trim "
                f"({TRIM_WIDTH_MM:.0f}x{TRIM_HEIGHT_MM:.0f}mm) with {pages_with_bleed} "
                f"page(s) at with-bleed size "
                f"({TRIM_WIDTH_MM_WITH_BLEED:.0f}x{TRIM_HEIGHT_MM_WITH_BLEED:.0f}mm) — "
                "Lulu requires every page to be the same size within one file"
            )
        # Only treat the file as "using bleed" (and skip the bleed-touching
        # error below) when every page uniformly uses the with-bleed size.
        file_has_bleed = pages_with_bleed > 0 and pages_no_bleed == 0 and not mismatched

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
        if n > MAX_PAGES:
            report.error(
                f"{n} pages exceeds Lulu's hardcover binding maximum of {MAX_PAGES} pages "
                f"(guide p14 spine table tops out at {MAX_PAGES} pages)"
            )

        _check_fonts_embedded(pdf_path, doc, report)

        low_dpi = []
        high_dpi = []
        bleed_risk_pages = set()
        for pno, page in enumerate(doc, start=1):
            pw, ph = page.rect.width, page.rect.height
            for info in page.get_image_info(xrefs=True):
                bbox = fitz.Rect(info["bbox"])
                iw, ih = info.get("width", 0), info.get("height", 0)
                if iw and ih and bbox.width > 0 and bbox.height > 0:
                    dpi_x = iw / (bbox.width / 72)
                    dpi_y = ih / (bbox.height / 72)
                    effective_dpi_min = min(dpi_x, dpi_y)
                    effective_dpi_max = max(dpi_x, dpi_y)
                    if effective_dpi_min < MIN_DPI:
                        low_dpi.append((pno, effective_dpi_min))
                    if effective_dpi_max > MAX_DPI:
                        high_dpi.append((pno, effective_dpi_max))

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

        if high_dpi:
            worst = sorted(high_dpi, key=lambda t: -t[1])[:5]
            detail = ", ".join(f"page {p} (~{d:.0f} dpi)" for p, d in worst)
            report.warn(
                f"{len(high_dpi)} image placement(s) above Lulu's {MAX_DPI} dpi ceiling at "
                f"printed size (guide p23/p24: images should not exceed {MAX_DPI} PPI): {detail}"
            )

        if bleed_risk_pages and not file_has_bleed and not mismatched:
            # Page size matches exact trim (no bleed margin added) but art
            # touches the edge — Lulu will trim into that art.
            pages = ", ".join(str(p) for p in sorted(bleed_risk_pages)[:5])
            report.error(
                f"full-bleed image(s) touch the page edge on page(s) {pages}, but pages are sized "
                f"to exact trim ({TRIM_WIDTH_MM:.0f}x{TRIM_HEIGHT_MM:.0f}mm) with no "
                f"{BLEED_MM:.2f}mm bleed margin — Lulu needs bleed added to the page size for "
                "full-bleed artwork (page grows to "
                f"{TRIM_WIDTH_MM_WITH_BLEED:.0f}x{TRIM_HEIGHT_MM_WITH_BLEED:.0f}mm), or the "
                "image should be inset from the edge"
            )

        return n
    finally:
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


def _recommended_gutter(page_count):
    """Return (recommended_total_inside_mm, bucket_label) for page_count,
    per the Lulu Book Creation Guide p9 "Gutter Additions" table."""
    for i, (max_pages, _add, total) in enumerate(GUTTER_TABLE):
        if page_count <= max_pages:
            prev_max = GUTTER_TABLE[i - 1][0] if i > 0 else 0
            if max_pages == float("inf"):
                label = f"over {prev_max} pages"
            elif i == 0:
                label = f"less than {max_pages + 1} pages"
            else:
                label = f"{prev_max + 1}-{max_pages} pages"
            return total, label
    return None, None


def check_geometry(sty_path, page_count, report):
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

    # Lulu's Interior File Specifications (guide p23) call for at least a
    # 2.08mm gutter added to the safety margin. In a twoside book class the
    # `inner` value IS the binding-side (gutter) margin, so it must clear
    # safety + minimum gutter to satisfy Lulu's absolute floor — and it
    # SHOULD meet the recommended total inside margin for the page count
    # bucket in the p9 "Gutter Additions" table.
    inner_mm = float(opts["inner"]) * 10 if "inner" in opts else None
    if inner_mm is not None:
        floor = SAFETY_MARGIN_MM + MIN_GUTTER_MM
        if inner_mm < floor:
            report.error(
                f"{sty_path}: inner (gutter-side) margin is {inner_mm:.1f}mm, below Lulu's "
                f"{floor:.2f}mm absolute floor (safety {SAFETY_MARGIN_MM:.1f}mm + minimum "
                f"gutter {MIN_GUTTER_MM:.2f}mm, guide p23)"
            )
        if page_count:
            recommended, bucket = _recommended_gutter(page_count)
            if recommended is not None and inner_mm < recommended:
                report.warn(
                    f"{sty_path}: inner margin is {inner_mm:.1f}mm; Lulu's Book Creation "
                    f"Guide p9 recommends at least {recommended}mm total inside margin for "
                    f"books in the {bucket} bucket (this book has {page_count} pages)"
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


def _hardcover_spine_mm(page_count):
    """Return the Lulu-specified spine width (mm) for a hardcover with this
    page count, per the Book Creation Guide p14 table. None if the book is
    too thin (< 24 pages, hardcover N/A) or too thick (> 800 pages)."""
    if page_count < HARDCOVER_SPINE_TABLE[0][0] or page_count > HARDCOVER_SPINE_TABLE[-1][1]:
        return None
    for lo, hi, spine in HARDCOVER_SPINE_TABLE:
        if lo <= page_count <= hi:
            return spine
    return None


def check_cover_pdf(cover_pdf_path, report):
    """Cover File Specifications (Lulu Book Creation Guide p24): fonts
    embedded, images 300-600 PPI, no encryption. Trim size and bleed are
    tied to the specific hardcover casewrap template rather than the
    generic paperback bleed (0.125 in), so they're covered separately by
    check_cover_spine's page-count-to-spine-table check on cover/cover.tex."""
    if not cover_pdf_path.exists():
        return
    doc = fitz.open(cover_pdf_path)
    try:
        if _check_encryption(cover_pdf_path, doc, report):
            return
        if doc.page_count == 0:
            report.error(f"{cover_pdf_path}: cover PDF has no pages")
            return
        if doc.page_count != 1:
            # Lulu's cover spec (guide p24): "a single-page integrated
            # spread PDF (back cover, spine, and front cover)".
            report.error(
                f"{cover_pdf_path}: cover PDF has {doc.page_count} pages, but Lulu requires "
                "a single-page integrated spread (back cover + spine + front cover on one page)"
            )
        _check_fonts_embedded(cover_pdf_path, doc, report)
        low_dpi = []
        high_dpi = []
        for pno, page in enumerate(doc, start=1):
            for info in page.get_image_info(xrefs=True):
                bbox = fitz.Rect(info["bbox"])
                iw, ih = info.get("width", 0), info.get("height", 0)
                if iw and ih and bbox.width > 0 and bbox.height > 0:
                    dpi_min = min(iw / (bbox.width / 72), ih / (bbox.height / 72))
                    dpi_max = max(iw / (bbox.width / 72), ih / (bbox.height / 72))
                    if dpi_min < MIN_DPI:
                        low_dpi.append((pno, dpi_min))
                    if dpi_max > MAX_DPI:
                        high_dpi.append((pno, dpi_max))
        if low_dpi:
            worst = sorted(low_dpi, key=lambda t: t[1])[:5]
            detail = ", ".join(f"page {p} (~{d:.0f} dpi)" for p, d in worst)
            report.warn(
                f"{cover_pdf_path}: {len(low_dpi)} cover image(s) below {MIN_DPI} dpi at "
                f"printed size: {detail}"
            )
        if high_dpi:
            worst = sorted(high_dpi, key=lambda t: -t[1])[:5]
            detail = ", ".join(f"page {p} (~{d:.0f} dpi)" for p, d in worst)
            report.warn(
                f"{cover_pdf_path}: {len(high_dpi)} cover image(s) above Lulu's {MAX_DPI} dpi "
                f"ceiling (guide p24): {detail}"
            )
    finally:
        doc.close()


def _parse_length_mm(text, name):
    """Pull the value from a `\\setlength\\name{X mm}` declaration."""
    match = re.search(rf"\\setlength\\{name}\s*\{{\s*([\d.]+)\s*mm\s*\}}", text)
    return float(match.group(1)) if match else None


def check_cover_spine(cover_tex_path, interior_page_count, report):
    """Warn if the wraparound cover's hardcoded interior page count is
    stale, or if its spine width is outside the Lulu hardcover-spine
    bucket for the current interior page count (guide p14 table).

    The hardcover spine width isn't a formula — it comes from Lulu's own
    Project Creation Tool template, keyed on page count via an internal
    lookup table. The guide's p14 table is coarser than that internal
    lookup (which is why cover.tex hardcodes a slightly different value,
    e.g. 17.48mm instead of the table's 17mm for the 169-194 bucket),
    so we only flag a mismatch when the deviation is larger than one
    table bucket."""
    if not cover_tex_path.exists() or not interior_page_count:
        return
    text = cover_tex_path.read_text(encoding="utf-8")

    interior_match = re.search(r"\\newcommand\{?\\interiorpagecount\}?\s*\{\s*(\d+)\s*\}", text)
    if interior_match:
        declared = int(interior_match.group(1))
        if declared != interior_page_count:
            report.warn(
                f"{cover_tex_path}: \\interiorpagecount is {declared} but the built interior "
                f"PDF has {interior_page_count} pages — regenerate the cover template from "
                f"Lulu's Project Creation Tool for the current page count and update "
                f"\\interiorpagecount and \\spinew to match (see cover.tex header note)"
            )

    spine_mm = _parse_length_mm(text, "spinew")
    expected = _hardcover_spine_mm(interior_page_count)
    if spine_mm is not None and expected is not None:
        # The p14 table uses 1mm-precision buckets; Lulu's own template can
        # differ by up to a bucket. Warn only when the value is more than
        # one bucket off, which usually means the wrong page count was
        # used to regenerate the template.
        if abs(spine_mm - expected) > 3:
            report.warn(
                f"{cover_tex_path}: spine width \\spinew={spine_mm:.2f}mm is far from Lulu's "
                f"guide p14 hardcover-spine table value ({expected}mm) for "
                f"{interior_page_count} pages — regenerate the cover template from Lulu's "
                f"Project Creation Tool and update \\spinew"
            )
    elif spine_mm is not None and expected is None and interior_page_count > MAX_PAGES:
        report.error(
            f"{cover_tex_path}: interior has {interior_page_count} pages, above Lulu's "
            f"hardcover binding maximum of {MAX_PAGES} pages"
        )


def check_spine_text(cover_tex_path, interior_page_count, report):
    """Lulu Book Creation Guide p17: "If your book is 80 pages or fewer, do
    not include spine text." The cover template contains a SPINE section
    with a rotated text node — flag its presence for thin books."""
    if not cover_tex_path.exists() or not interior_page_count:
        return
    if interior_page_count > MAX_SPINE_TEXT_PAGES:
        return
    text = cover_tex_path.read_text(encoding="utf-8")
    # cover.tex marks the spine section with a "SPINE" banner comment and
    # sets a rotated text node inside it. Any rotated node paired with the
    # spine banner is spine text worth flagging.
    if re.search(r"SPINE.*?rotate\s*=\s*90", text, re.S):
        report.warn(
            f"{cover_tex_path}: interior is {interior_page_count} pages "
            f"(≤ {MAX_SPINE_TEXT_PAGES}); Lulu Book Creation Guide p17 says "
            f"no spine text on books this thin — the slightest shift in spine "
            f"placement will run the text onto the front or back cover"
        )


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
    parser.add_argument("pdf", nargs="?", default="main.pdf", help="path to the built interior PDF (default: main.pdf)")
    parser.add_argument(
        "--cover", default=None,
        help="path to the built wraparound cover PDF (default: auto-detect "
             "KookboekFamilieSpoor-cover.pdf next to the interior PDF)",
    )
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

    if args.cover is not None:
        cover_pdf_path = Path(args.cover)
    else:
        # Auto-detect the sibling cover PDF alongside the interior file.
        cover_pdf_path = pdf_path.with_name(pdf_path.stem + "-cover.pdf")

    report = Report()
    page_count = check_pdf(pdf_path, report, paper_rgb=_paper_rgb(root / "kookboek.sty"))
    check_transparency(pdf_path, report)
    check_geometry(root / "kookboek.sty", page_count, report)
    check_orphan_pages(pdf_path, root / "main.tex", report)
    check_placeholders(root / "recipes", report)
    if cover_pdf_path.exists():
        check_cover_pdf(cover_pdf_path, report)
        check_transparency(cover_pdf_path, report)
    check_cover_spine(root / "cover" / "cover.tex", page_count, report)
    check_spine_text(root / "cover" / "cover.tex", page_count, report)

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
