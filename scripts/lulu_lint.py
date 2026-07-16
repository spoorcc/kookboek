#!/usr/bin/env python3
"""Check a book PDF (and its LaTeX source) against Lulu.com's print
requirements as documented in Lulu's Book Creation Guide.

The trim-size check is generic: every Lulu p11 trim (Pocketbook, Novella,
Digest, A5, US Trade, Royal, Comic Book, Executive, Crown Quarto, Small
Square, A4, Square, US Letter, Small Landscape, US Letter Landscape, A4
Landscape, Calendar) is accepted, with or without Lulu's bleed added.
The linter identifies which trim the PDF is at and reports it. By default
the intended trim is inferred from the .sty file's geometry
paperwidth/paperheight and enforced; pass --trim NAME to override, or
--trim any to disable enforcement. Everything else the linter checks
(fonts, image PPI, encryption, safety/gutter margins, page count, spine
width against the p14 hardcover table, and so on) is trim-agnostic.

Usage:
    python3 scripts/lulu_lint.py [PDF] [--cover PDF|none] [--trim NAME]
                                 [--sty PATH] [--main-tex PATH]
                                 [--cover-tex PATH] [--recipes-dir PATH]
                                 [--frontmatter-dir PATH] [--images-dir PATH]
                                 [--log PATH] [--cover-log PATH]
                                 [--repo-root DIR] [--strict]

Every source path defaults from --repo-root; supply the individual flags
when your project's layout differs, or drop them entirely to run
PDF-only. In PDF-only mode the linter prints a skip note for each
source-dependent check and falls back to an empirical PDF-side margin
measurement so Lulu's 12.7mm safety zone still gets checked. --log and
--cover-log likewise default to the interior/cover PDF path with a .log
extension, and are skipped with a note if the latexmk/xelatex .log isn't
there (e.g. a PDF-only run, or a build tool that doesn't keep .log files).

Errors are things that will actually break a Lulu print job (wrong or
unrecognized trim size, unembedded fonts, encrypted PDF, full-bleed art
without a bleed margin, margins below Lulu's minimum, page count over
Lulu's cap, a recipe \\input-ing a file that doesn't exist, an images/...
reference with no matching file, or a LaTeX log showing undefined
references/citations, missing glyphs, or errors survived in nonstopmode).
Warnings are things worth knowing about but that are expected while the
book is still a work in progress (unfinished recipes, low- or high-DPI
art, an odd page count, an inner margin below the recommended gutter for
the current page count, a recipe file that exists but isn't \\input by
main.tex, a recipe with no \\index[register]{...} entries, an unused
images/ file, a multiply-defined LaTeX label, or overfull/underfull
hboxes past the noticeable-on-the-page threshold). Pass --strict to also
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

# Full Lulu Book Creation Guide p11 "Book Trim Sizes" table. Each entry is
# (name, trim_w_mm, trim_h_mm, bleed_w_mm, bleed_h_mm). The guide's "Trim
# Size" and "Interior File Dimensions - No Bleed" columns are the same in
# every row, so only one pair (trim_w/trim_h) is stored; the with-bleed
# pair is the size a publisher uses when they choose to add Lulu's bleed
# to the page dimensions themselves. Two rows (US Letter Landscape and
# Calendar) share the same dimensions — that's how the guide prints it;
# _identify_trim() reports whichever entry it matches first.
LULU_TRIM_SIZES = [
    ("Pocketbook",          108, 175, 114, 181),
    ("Novella",             127, 203, 133, 210),
    ("Digest",              140, 216, 146, 222),
    ("A5",                  148, 210, 154, 216),
    ("US Trade",            152, 229, 159, 235),
    ("Royal",               156, 234, 162, 240),
    ("Comic Book",          168, 260, 175, 267),
    ("Executive",           178, 254, 184, 260),
    ("Crown Quarto",        189, 246, 195, 252),
    ("Small Square",        191, 191, 197, 197),
    ("A4",                  210, 297, 216, 303),
    ("Square",              216, 216, 222, 222),
    ("US Letter",           216, 279, 222, 286),
    ("Small Landscape",     229, 178, 235, 184),
    ("US Letter Landscape", 279, 216, 286, 222),
    ("A4 Landscape",        297, 210, 303, 216),
    ("Calendar",            279, 216, 286, 222),
]

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

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")

# TeX's badness scale runs 0 (perfect) to 10000 (impossible to break well).
# Only the more severe half is visibly loose on the page; low-badness
# underfull boxes are routine and not worth a human look.
UNDERFULL_HBOX_BADNESS_WARN = 5000
# Overfull hboxes under ~10pt are typographically invisible and appear in
# almost every LaTeX document; only flag ones wide enough that text could
# plausibly be running into the margin.
OVERFULL_HBOX_WARN_PT = 10.0

_UNDEFINED_REF_RE = re.compile(r"LaTeX Warning: (Reference|Citation) `([^']*)' on page (\d+) undefined")
_MULTIPLY_DEFINED_RE = re.compile(r"LaTeX Warning: Label `([^']*)' multiply defined")
_MISSING_CHAR_RE = re.compile(r"Missing character: There is no (.+?) in font ([^!]+)!")
_FATAL_ERROR_RE = re.compile(r"^! (.+)$", re.MULTILINE)

# Bookmark titles that mark front/back matter rather than a category chapter.
NON_CHAPTER_TITLES = {"Inhoud", "Register", "Voorwoord", "Kookboek", "Index"}

BOILERPLATE_LINE_RE = re.compile(r"^(Kookboek van onze familie|—\s*\d+\s*—|\d+)$")
# A rendered \begin{steps} item: "8 Zet de oven..." — digits, then a capital
# letter starting the sentence. Deliberately excludes ingredient lines like
# "397 ml gezoete..." (unit abbreviations are lowercase in this book).
STEP_LINE_RE = re.compile(r"^\d{1,2}\s+[A-ZÀ-ÖØ-Þ]")


def mm(pt):
    return pt / PT_PER_MM


class _CheckCtx:
    """Records errors/warnings/notes raised during one named check block.
    Yielded by Report.check(); tracks a check's outcome and lets the
    verbose output print [PASS] / [WARN] / [FAIL] / [SKIP] for it."""

    def __init__(self, report, name, description):
        self.report = report
        self.name = name
        self.description = description
        self._errors_before = len(report.errors)
        self._warnings_before = len(report.warnings)
        self._notes_before = len(report.notes)
        self._skip_reason = None

    def skip(self, reason):
        """Mark this check as skipped and record why."""
        self._skip_reason = reason
        self.report.note(reason)

    def __enter__(self):
        self.report._current = self
        return self

    def __exit__(self, exc_type, exc, tb):
        self.report._current = None
        errors = self.report.errors[self._errors_before:]
        warnings = self.report.warnings[self._warnings_before:]
        notes = self.report.notes[self._notes_before:]
        if self._skip_reason is not None:
            status = "SKIP"
        elif errors:
            status = "FAIL"
        elif warnings:
            status = "WARN"
        else:
            status = "PASS"
        self.report.checks.append({
            "name": self.name,
            "description": self.description,
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "notes": notes,
        })
        # Never swallow real exceptions.
        return False


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []
        self.checks = []       # ordered list of finished-check records
        self._current = None   # currently-active _CheckCtx, if any

    def check(self, name, description=""):
        """Context manager that names a single check. Errors, warnings,
        and notes emitted inside the block are attributed to it, and its
        pass/fail/warn/skip status is recorded for verbose output."""
        return _CheckCtx(self, name, description)

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        """Non-failing informational line (e.g. "detected trim: Crown Quarto")."""
        self.notes.append(msg)


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


TRIM_TOLERANCE_MM = 0.5


def _identify_trim(w_mm, h_mm):
    """Match (w_mm, h_mm) against the Lulu Book Creation Guide p11 table.
    Returns (name, has_bleed, trim_w_mm, trim_h_mm, bleed_w_mm, bleed_h_mm)
    for the matching entry, or None if the size is not a Lulu-supported trim."""
    for name, tw, th, bw, bh in LULU_TRIM_SIZES:
        if abs(w_mm - tw) <= TRIM_TOLERANCE_MM and abs(h_mm - th) <= TRIM_TOLERANCE_MM:
            return (name, False, tw, th, bw, bh)
        if abs(w_mm - bw) <= TRIM_TOLERANCE_MM and abs(h_mm - bh) <= TRIM_TOLERANCE_MM:
            return (name, True, tw, th, bw, bh)
    return None


def _find_trim_by_name(name):
    """Case-insensitive lookup of a p11 table entry by name."""
    key = name.strip().casefold()
    for entry in LULU_TRIM_SIZES:
        if entry[0].casefold() == key:
            return entry
    return None


def _identify_page(page):
    return _identify_trim(mm(page.rect.width), mm(page.rect.height))


def _geometry_paper_size_mm(sty_path):
    """Extract (paperwidth_mm, paperheight_mm) from the .sty file's
    geometry configuration, or None if it can't be parsed. Used to
    determine which Lulu trim size the LaTeX source declares, so the
    linter can enforce that against the built PDF."""
    if not sty_path.exists():
        return None
    text = sty_path.read_text(encoding="utf-8")
    match = re.search(r"\\RequirePackage\[(.*?)\]\{geometry\}", text, re.S)
    if not match:
        return None
    opts = match.group(1)
    w = re.search(r"paperwidth\s*=\s*([\d.]+)mm", opts)
    h = re.search(r"paperheight\s*=\s*([\d.]+)mm", opts)
    if not (w and h):
        return None
    return float(w.group(1)), float(h.group(1))


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


def check_pdf(pdf_path, report, paper_rgb=(255, 255, 255), expected_trim=None):
    """Validate the PDF against Lulu's interior-file rules. Splits into
    several named sub-checks so the verbose output can report a
    PASS/FAIL/WARN line per rule.

    `expected_trim`: optional name (case-insensitive, e.g. "Crown Quarto")
    from the p11 Book Trim Sizes table. When given, the PDF must be at
    that trim; when None, any Lulu trim is accepted and the detected
    one is reported."""
    doc = fitz.open(pdf_path)
    try:
        with report.check("PDF encryption", "guide p23/p24: no security/password protection"):
            if _check_encryption(pdf_path, doc, report):
                return 0

        if doc.page_count == 0:
            with report.check("Basic PDF integrity"):
                report.error(f"{pdf_path}: PDF has no pages")
            return 0

        with report.check("Trim size", "guide p11 Book Trim Sizes table"):
            # Identify every page's trim against the full p11 table. Two
            # variants of one trim are both acceptable — exact trim ("No
            # Bleed" column) or the same trim with Lulu's bleed added
            # ("With Bleed" column) — but the file must be uniform: every
            # page the same trim, and every page in the same bleed vs.
            # no-bleed variant.
            unknown = []
            seen_trims = {}  # (name, has_bleed) -> [page_numbers]
            for i, page in enumerate(doc, start=1):
                match = _identify_page(page)
                if match is None:
                    unknown.append((i, mm(page.rect.width), mm(page.rect.height)))
                    continue
                key = (match[0], match[1])
                seen_trims.setdefault(key, []).append(i)

            if unknown:
                sample = ", ".join(f"page {i} ({w:.1f}x{h:.1f}mm)" for i, w, h in unknown[:5])
                report.error(
                    f"{len(unknown)} page(s) don't match any Lulu trim size from the "
                    f"Book Creation Guide p11 table: {sample}"
                )

            if len(seen_trims) > 1:
                parts = []
                for (name, has_bleed), pages in seen_trims.items():
                    _, tw, th, bw, bh = _find_trim_by_name(name)
                    w, h = (bw, bh) if has_bleed else (tw, th)
                    variant = " with bleed" if has_bleed else ""
                    parts.append(f"{len(pages)} page(s) at {name}{variant} ({w}x{h}mm)")
                report.error(
                    f"PDF mixes multiple trim sizes — Lulu requires every page to be the "
                    f"same size within one file: {'; '.join(parts)}"
                )

            detected = next(iter(seen_trims), None) if len(seen_trims) == 1 else None
            # Only treat the file as "using bleed" (and skip the
            # bleed-touching error below) when the whole file is uniformly
            # the with-bleed variant of a Lulu trim.
            file_has_bleed = detected is not None and detected[1]

            if expected_trim is not None:
                expected_entry = _find_trim_by_name(expected_trim)
                if expected_entry is None:
                    report.error(
                        f"expected trim {expected_trim!r} is not a Lulu Book Creation Guide "
                        f"p11 trim size — known names: "
                        + ", ".join(e[0] for e in LULU_TRIM_SIZES)
                    )
                elif detected is not None and detected[0].casefold() != expected_entry[0].casefold():
                    d_name, d_bleed = detected
                    _, dtw, dth, dbw, dbh = _find_trim_by_name(d_name)
                    d_w, d_h = (dbw, dbh) if d_bleed else (dtw, dth)
                    variant = "with bleed" if d_bleed else "no bleed"
                    report.error(
                        f"PDF is {d_name} ({d_w}x{d_h}mm, {variant}) but this project "
                        f"expects {expected_entry[0]} "
                        f"({expected_entry[1]}x{expected_entry[2]}mm, no bleed / "
                        f"{expected_entry[3]}x{expected_entry[4]}mm, with bleed)"
                    )

            if detected is not None and not unknown:
                variant = "with bleed" if detected[1] else "no bleed"
                report.note(f"detected trim: {detected[0]} ({variant})")

        n = doc.page_count
        with report.check("Page count", "guide p13 minimums, p14 hardcover cap, multiples of 4"):
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

        with report.check("Font embedding", "guide p23/p24: all fonts must be embedded"):
            _check_fonts_embedded(pdf_path, doc, report)

        # DPI and bleed-touching share the same per-page image loop.
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

        with report.check("Image resolution", f"guide p4/p23: {MIN_DPI}-{MAX_DPI} PPI at printed size"):
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

        with report.check("Full-bleed safety", "guide p10: art at the trim edge needs bleed"):
            if bleed_risk_pages and not file_has_bleed and not unknown and detected is not None:
                # Page size matches exact trim (no bleed margin added) but
                # art touches the edge — Lulu will trim into that art.
                name, _has_bleed = detected
                _, tw, th, bw, bh = _find_trim_by_name(name)
                pages = ", ".join(str(p) for p in sorted(bleed_risk_pages)[:5])
                report.error(
                    f"full-bleed image(s) touch the page edge on page(s) {pages}, but pages are "
                    f"sized to exact {name} trim ({tw:.0f}x{th:.0f}mm) with no {BLEED_MM:.2f}mm "
                    f"bleed margin — Lulu needs bleed added to the page size for full-bleed "
                    f"artwork (page grows to {bw:.0f}x{bh:.0f}mm), or the image should be "
                    f"inset from the edge"
                )

        return n
    finally:
        doc.close()


def check_transparency(pdf_path, report, name_prefix=""):
    label = f"{name_prefix}Transparency flattening" if name_prefix else "Transparency flattening"
    with report.check(label, "Lulu recommends flattening all transparency before upload") as ctx:
        if pdf_path is None or not pdf_path.exists():
            ctx.skip(f"no PDF at {pdf_path} — transparency check skipped")
            return
        doc = fitz.open(pdf_path)
        try:
            if doc.is_encrypted or doc.needs_pass:
                ctx.skip(f"{pdf_path}: PDF is encrypted — transparency check skipped")
                return
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


def _find_hbox_warnings(text, kind):
    """Return [(metric, line_no), ...] for every 'Overfull'/'Underfull \\hbox'
    warning in a LaTeX log. metric is pt-too-wide (float) for Overfull, or
    badness (int) for Underfull. Covers all three forms latexmk emits: inside
    a paragraph, inside a tabular/array alignment, or a bare box (e.g. from
    \\parbox) reported by line number alone."""
    if kind == "Overfull":
        pattern = re.compile(
            r"^Overfull \\hbox \(([\d.]+)pt too wide\) "
            r"(?:in paragraph at lines (\d+)|in alignment at lines (\d+)|detected at line (\d+))",
            re.MULTILINE,
        )
        cast = float
    else:
        pattern = re.compile(
            r"^Underfull \\hbox \(badness (\d+)\) "
            r"(?:in paragraph at lines (\d+)|in alignment at lines (\d+)|detected at line (\d+))",
            re.MULTILINE,
        )
        cast = int
    results = []
    for m in pattern.finditer(text):
        line = next(g for g in m.groups()[1:] if g is not None)
        results.append((cast(m.group(1)), int(line)))
    return results


def check_latex_log(log_path, report, name_prefix=""):
    """Parse a latexmk/xelatex .log for defects that a PDF-only check can't
    see: undefined references/citations (render as literal "??" in print),
    multiply-defined labels, missing glyphs, hboxes wide/loose enough to be
    visible on the page, and LaTeX errors that a nonstopmode run may have
    survived past. Genuinely print-breaking issues (undefined refs/cites,
    missing glyphs, LaTeX errors) are errors; the rest are warnings."""
    label = f"{name_prefix}LaTeX log" if name_prefix else "LaTeX log"
    with report.check(label, "undefined refs/citations, multiply-defined labels, missing glyphs, box warnings") as ctx:
        if not log_path.exists():
            ctx.skip(f"no {log_path} — LaTeX log check skipped (run the build first)")
            return
        text = log_path.read_text(encoding="utf-8", errors="replace")

        undefined = _UNDEFINED_REF_RE.findall(text)
        if undefined:
            names = sorted({f"{kind.lower()} `{name}'" for kind, name, _page in undefined})
            report.error(
                f"{log_path}: {len(undefined)} undefined reference(s)/citation(s) — these render "
                f"as a literal \"??\" in the printed book: " + ", ".join(names[:8])
            )

        multiply = _MULTIPLY_DEFINED_RE.findall(text)
        if multiply:
            names = sorted(set(multiply))
            report.warn(
                f"{log_path}: {len(multiply)} multiply-defined label(s) — \\ref/\\pageref to these "
                f"resolves to whichever definition happened to run last: " + ", ".join(names[:8])
            )

        missing_chars = _MISSING_CHAR_RE.findall(text)
        if missing_chars:
            detail = sorted({f"{ch!r} in {font.strip()}" for ch, font in missing_chars})
            report.error(
                f"{log_path}: {len(missing_chars)} missing-character warning(s) — these glyphs "
                f"aren't in the embedded font and print as blank boxes: " + ", ".join(detail[:8])
            )

        overfull = _find_hbox_warnings(text, "Overfull")
        big_overfull = [(amt, line) for amt, line in overfull if amt > OVERFULL_HBOX_WARN_PT]
        if big_overfull:
            worst = sorted(big_overfull, key=lambda t: -t[0])[:5]
            detail = ", ".join(f"line {l} ({amt:.1f}pt)" for amt, l in worst)
            report.warn(
                f"{log_path}: {len(big_overfull)} overfull hbox(es) wider than "
                f"{OVERFULL_HBOX_WARN_PT:.0f}pt (of {len(overfull)} total) — text running this far "
                f"past the text-block edge can visibly spill into the margin: {detail}"
            )
        elif overfull:
            report.note(
                f"{log_path}: {len(overfull)} minor overfull hbox(es), all under "
                f"{OVERFULL_HBOX_WARN_PT:.0f}pt (typographically invisible)"
            )

        underfull = _find_hbox_warnings(text, "Underfull")
        bad_underfull = [(b, line) for b, line in underfull if b >= UNDERFULL_HBOX_BADNESS_WARN]
        if bad_underfull:
            worst = sorted(bad_underfull, key=lambda t: -t[0])[:5]
            detail = ", ".join(f"line {l} (badness {b})" for b, l in worst)
            report.warn(
                f"{log_path}: {len(bad_underfull)} underfull hbox(es) with badness >= "
                f"{UNDERFULL_HBOX_BADNESS_WARN} (of {len(underfull)} total) — visibly loose, gappy "
                f"spacing: {detail}"
            )
        elif underfull:
            report.note(
                f"{log_path}: {len(underfull)} minor underfull hbox(es), all under badness "
                f"{UNDERFULL_HBOX_BADNESS_WARN}"
            )

        fatal = _FATAL_ERROR_RE.findall(text)
        if fatal:
            uniq = list(dict.fromkeys(msg.strip() for msg in fatal))
            report.error(
                f"{log_path}: {len(fatal)} LaTeX error(s) found in the log (a nonstopmode run can "
                f"continue past these and still produce a PDF): " + "; ".join(uniq[:5])
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


def check_pdf_margins(pdf_path, report):
    """Empirically verify that no rendered text sits inside Lulu's
    12.7mm safety margin (guide p8, p23). Runs on the PDF alone —
    useful either as a belt-and-suspenders check alongside the .sty
    check or as a fallback when the LaTeX source isn't available.
    Only text is measured; images can legitimately extend to the edge
    on full-bleed pages (the bleed check in check_pdf handles those)."""
    with report.check("Empirical margin (PDF-side)", f"guide p8/p23: no content inside {SAFETY_MARGIN_MM:.1f}mm safety zone") as ctx:
        doc = fitz.open(pdf_path)
        try:
            if doc.is_encrypted or doc.needs_pass:
                ctx.skip(f"{pdf_path}: PDF is encrypted — empirical margin check skipped")
                return
            safety_pt = SAFETY_MARGIN_MM * PT_PER_MM
            offenders = []
            for pno, page in enumerate(doc, start=1):
                pw, ph = page.rect.width, page.rect.height
                page_worst_pt = float("inf")
                for block in page.get_text("blocks"):
                    bx0, by0, bx1, by1, text, *_ = block
                    if not text.strip():
                        continue
                    worst = min(bx0, by0, pw - bx1, ph - by1)
                    if worst < page_worst_pt:
                        page_worst_pt = worst
                if page_worst_pt < safety_pt:
                    offenders.append((pno, mm(page_worst_pt)))
            if offenders:
                worst = sorted(offenders, key=lambda t: t[1])[:5]
                detail = ", ".join(f"page {p} (~{d:.1f}mm from trim edge)" for p, d in worst)
                report.warn(
                    f"{len(offenders)} page(s) have text sitting inside Lulu's "
                    f"{SAFETY_MARGIN_MM:.1f}mm safety margin (guide p8, p23) — content this "
                    f"close to the trim edge risks being cut off: {detail}"
                )
        finally:
            doc.close()


def check_geometry(sty_path, page_count, report):
    with report.check("Interior margins (source-side)", "guide p8/p9/p23: safety, gutter floor, p9 gutter table") as ctx:
        if not sty_path.exists():
            ctx.skip(
                f"no .sty file at {sty_path} — source-side margin/gutter check skipped "
                f"(the PDF-side empirical check runs regardless)"
            )
            return False
        text = sty_path.read_text(encoding="utf-8")
        match = re.search(r"\\RequirePackage\[(.*?)\]\{geometry\}", text, re.S)
        if not match:
            report.warn(f"{sty_path}: couldn't find a geometry configuration to check margins")
            return False
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
        # 2.08mm gutter added to the safety margin. In a twoside book class
        # the `inner` value IS the binding-side (gutter) margin, so it must
        # clear safety + minimum gutter to satisfy Lulu's absolute floor —
        # and it SHOULD meet the recommended total inside margin for the
        # page count bucket in the p9 "Gutter Additions" table.
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
        return True


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
    with report.check("Widow pages", "single-step recipe endings on their own page") as ctx:
        if not main_tex_path.exists():
            ctx.skip(
                f"no {main_tex_path} — widow-page check skipped (needs main.tex "
                f"to distinguish subchapter dividers from recipes in the PDF outline)"
            )
            return
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
                # Require at least one recognizable step line before trusting
                # this page belongs to the recipe at all — guards against the
                # page range spilling into the next chapter/Register's own
                # opening page (a known quirk of the bookmark-derived page
                # boundaries).
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
    embedded, images 300-600 PPI, no encryption, single integrated
    spread page. Trim size and bleed are tied to the specific hardcover
    casewrap template rather than the generic paperback bleed
    (0.125 in), so they're covered separately by check_cover_spine's
    page-count-to-spine-table check on cover/cover.tex."""
    with report.check("Cover PDF integrity", "guide p24: single-page spread, fonts embedded, no encryption") as ctx:
        if not cover_pdf_path.exists():
            ctx.skip(f"no cover PDF at {cover_pdf_path} — cover PDF checks skipped")
        else:
            doc = fitz.open(cover_pdf_path)
            try:
                if not _check_encryption(cover_pdf_path, doc, report):
                    if doc.page_count == 0:
                        report.error(f"{cover_pdf_path}: cover PDF has no pages")
                    elif doc.page_count != 1:
                        # Lulu's cover spec (guide p24): "a single-page
                        # integrated spread PDF (back cover, spine, and
                        # front cover)".
                        report.error(
                            f"{cover_pdf_path}: cover PDF has {doc.page_count} pages, but Lulu "
                            f"requires a single-page integrated spread (back cover + spine + "
                            f"front cover on one page)"
                        )
                    _check_fonts_embedded(cover_pdf_path, doc, report)
            finally:
                doc.close()

    with report.check("Cover image resolution", f"guide p4/p24: {MIN_DPI}-{MAX_DPI} PPI") as ctx:
        if not cover_pdf_path.exists():
            ctx.skip(f"no cover PDF at {cover_pdf_path} — cover image resolution check skipped")
            return
        doc = fitz.open(cover_pdf_path)
        try:
            if doc.is_encrypted or doc.needs_pass:
                ctx.skip(f"{cover_pdf_path}: encrypted — cover image resolution check skipped")
                return
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
    with report.check("Cover spine width", "guide p14 hardcover spine-width table vs \\interiorpagecount / \\spinew") as ctx:
        if not interior_page_count:
            ctx.skip("interior page count unavailable — cover spine-width check skipped")
            return
        if not cover_tex_path.exists():
            ctx.skip(
                f"no {cover_tex_path} — cover spine-width check skipped (needs the "
                f"cover source to read \\interiorpagecount and \\spinew)"
            )
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
            # The p14 table uses 1mm-precision buckets; Lulu's own template
            # can differ by up to a bucket. Warn only when the value is
            # more than one bucket off, which usually means the wrong page
            # count was used to regenerate the template.
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
    with report.check("Cover spine text", f"guide p17: no spine text on books ≤ {MAX_SPINE_TEXT_PAGES} pages") as ctx:
        if not interior_page_count:
            ctx.skip("interior page count unavailable — spine-text check skipped")
            return
        if interior_page_count > MAX_SPINE_TEXT_PAGES:
            # Rule doesn't apply — book is thick enough for spine text.
            return
        if not cover_tex_path.exists():
            ctx.skip(
                f"no {cover_tex_path} — spine-text check skipped (book is "
                f"{interior_page_count} pages, ≤ {MAX_SPINE_TEXT_PAGES}; guide p17 "
                f"says no spine text this thin)"
            )
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
    with report.check("Unfinished recipe placeholders", "no \\heroplaceholder/\\ingredientsketch/\\writelines left") as ctx:
        if not recipes_dir.exists():
            ctx.skip(
                f"no {recipes_dir}/ — recipe-placeholder check skipped (needs the "
                f"per-recipe .tex sources)"
            )
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


def check_recipe_inclusion(recipes_dir, main_tex_path, report):
    """Every recipes/*.tex should be \\input by main.tex (per CLAUDE.md's
    "Adding a recipe" steps) — a file left out never makes it into the book,
    and a reference to a file that's gone would break the build before this
    linter is even reached, but is worth flagging with a clear message
    instead of a raw LaTeX trace if it's ever run standalone."""
    with report.check("Recipe inclusion", "every recipes/*.tex is \\input by main.tex, and vice versa") as ctx:
        if not recipes_dir.exists() or not main_tex_path.exists():
            ctx.skip(f"needs both {recipes_dir}/ and {main_tex_path} — recipe-inclusion check skipped")
            return
        input_re = re.compile(r"\\input\{recipes/([^}]+)\}")
        referenced = []
        for line in main_tex_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("%"):
                continue
            m = input_re.search(line)
            if m:
                referenced.append(m.group(1))

        missing_files = sorted(r for r in referenced if not (recipes_dir / f"{r}.tex").exists())
        if missing_files:
            report.error(
                f"{main_tex_path}: \\input{{recipes/...}} references file(s) that don't exist: "
                + ", ".join(f"recipes/{r}.tex" for r in missing_files)
            )

        on_disk_stems = {p.stem for p in recipes_dir.glob("*.tex")}
        orphaned = sorted(on_disk_stems - set(referenced))
        if orphaned:
            report.warn(
                f"{len(orphaned)} recipe file(s) exist in {recipes_dir}/ but aren't \\input by "
                f"{main_tex_path} — they won't appear in the book: "
                + ", ".join(f"{o}.tex" for o in orphaned)
            )


def check_recipe_index_entries(recipes_dir, report):
    with report.check("Recipe index entries", "every recipe has at least one \\index[register]{...}") as ctx:
        if not recipes_dir.exists():
            ctx.skip(f"no {recipes_dir}/ — recipe index-entry check skipped")
            return
        missing = [
            path.name
            for path in sorted(recipes_dir.glob("*.tex"))
            if r"\index[register]{" not in path.read_text(encoding="utf-8")
        ]
        if missing:
            report.warn(
                f"{len(missing)} recipe file(s) have no \\index[register]{{...}} entries — the "
                f"dish won't be findable in the Register: " + ", ".join(missing)
            )


_IMAGE_REF_RE = re.compile(r"images/([\w-]+)")


def check_images(images_dir, tex_paths, report):
    """Cross-check images/*.{png,jpg,jpeg} against every images/... reference
    in the LaTeX sources. Referenced names are matched without their
    extension — [\\w-]+ stops at the '.', so this works whether a reference
    spells out an extension (rare direct \\includegraphics use) or, as is
    the norm here, leaves the extension for LaTeX's graphics-extension
    search to resolve (\\heroimage{images/foo}, \\marginimage{images/foo})."""
    with report.check("Image references", "every images/ file is used; every reference resolves to a file") as ctx:
        if not images_dir.exists():
            ctx.skip(f"no {images_dir}/ — image-reference check skipped")
            return
        existing = [p for p in tex_paths if p.exists()]
        if not existing:
            ctx.skip("none of the LaTeX sources exist — image-reference check skipped")
            return

        referenced = set()
        for tex_path in existing:
            for line in tex_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("%"):
                    continue
                referenced.update(_IMAGE_REF_RE.findall(line))

        on_disk = {
            p.stem: p.name
            for p in images_dir.iterdir()
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        }

        missing = sorted(referenced - on_disk.keys())
        if missing:
            report.error(
                f"{len(missing)} image reference(s) have no matching file in {images_dir}/: "
                + ", ".join(f"images/{m}" for m in missing)
            )

        unused = sorted(on_disk.keys() - referenced)
        if unused:
            report.warn(
                f"{len(unused)} file(s) in {images_dir}/ are never referenced from any LaTeX "
                f"source: " + ", ".join(on_disk[u] for u in unused)
            )


def _resolve_expected_trim(cli_trim, sty_path, report):
    """Decide which Lulu p11 trim the PDF is supposed to be at. Priority:
    (1) explicit --trim CLI flag, (2) the .sty file's geometry
    paperwidth/paperheight (looked up in the p11 table), (3) nothing —
    the linter then accepts any Lulu trim it detects."""
    if cli_trim:
        if cli_trim.lower() == "any":
            return None
        if _find_trim_by_name(cli_trim) is None:
            report.error(
                f"--trim {cli_trim!r} is not a Lulu Book Creation Guide p11 trim name — "
                f"known names: " + ", ".join(e[0] for e in LULU_TRIM_SIZES)
            )
            return None
        return cli_trim
    paper = _geometry_paper_size_mm(sty_path)
    if paper is None:
        return None
    match = _identify_trim(*paper)
    if match is None:
        report.warn(
            f"{sty_path} declares paperwidth×paperheight = {paper[0]}×{paper[1]}mm, which "
            f"isn't in the Lulu Book Creation Guide p11 trim-size table — the PDF's trim "
            f"can't be cross-checked against a known Lulu size"
        )
        return None
    return match[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", nargs="?", default="main.pdf", help="path to the built interior PDF (default: main.pdf)")
    parser.add_argument(
        "--cover", default=None,
        help="path to the built wraparound cover PDF (default: <PDF stem>-cover.pdf next "
             "to the interior). Pass \"none\" to skip cover-PDF checks entirely.",
    )
    parser.add_argument(
        "--trim", default=None,
        help='Lulu p11 trim to enforce (e.g. "Crown Quarto", "A5", "US Trade"). '
             'Default: infer from the .sty file\'s geometry paperwidth/paperheight. '
             'Pass "any" to accept any Lulu trim without enforcing a specific one.',
    )

    # Individual LaTeX source paths. Each defaults from --repo-root when
    # not given explicitly. Any source that doesn't exist is reported as
    # a skip note; the PDF-side check runs whenever it can substitute.
    parser.add_argument(
        "--sty", default=None,
        help="path to the .sty file with the geometry package (default: "
             "<repo-root>/kookboek.sty). Used for margin, gutter, and "
             "paper-colour checks.",
    )
    parser.add_argument(
        "--main-tex", default=None, dest="main_tex",
        help="path to the root .tex file (default: <repo-root>/main.tex). "
             "Used to distinguish subchapter dividers from recipes in the "
             "widow-page check.",
    )
    parser.add_argument(
        "--cover-tex", default=None, dest="cover_tex",
        help="path to the wraparound cover source (default: "
             "<repo-root>/cover/cover.tex). Used for spine-width and "
             "spine-text checks.",
    )
    parser.add_argument(
        "--recipes-dir", default=None, dest="recipes_dir",
        help="directory containing individual recipe .tex files (default: "
             "<repo-root>/recipes). Used for the unfinished-placeholder, "
             "recipe-inclusion, and index-entry checks.",
    )
    parser.add_argument(
        "--frontmatter-dir", default=None, dest="frontmatter_dir",
        help="directory containing front-matter .tex files (default: "
             "<repo-root>/frontmatter). Used for the image-reference check.",
    )
    parser.add_argument(
        "--images-dir", default=None, dest="images_dir",
        help="directory containing recipe artwork (default: <repo-root>/images). "
             "Used for the image-reference check.",
    )
    parser.add_argument(
        "--log", default=None,
        help="path to the interior's latexmk/xelatex .log (default: the PDF path "
             "with a .log extension). Used for the LaTeX-log check.",
    )
    parser.add_argument(
        "--cover-log", default=None, dest="cover_log",
        help="path to the cover's latexmk/xelatex .log (default: the cover PDF "
             "path with a .log extension). Used for the LaTeX-log check.",
    )
    parser.add_argument("--repo-root", default=".", help="fallback root for defaulting the source paths above (default: current directory)")
    parser.add_argument(
        "--strict", action="store_true", help="also fail on warnings (use before a real Lulu upload)"
    )
    args = parser.parse_args()

    root = Path(args.repo_root)
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"error: {pdf_path} not found — build the book first (./build.sh)", file=sys.stderr)
        return 2

    sty_path = Path(args.sty) if args.sty else root / "kookboek.sty"
    main_tex_path = Path(args.main_tex) if args.main_tex else root / "main.tex"
    cover_tex_path = Path(args.cover_tex) if args.cover_tex else root / "cover" / "cover.tex"
    recipes_dir = Path(args.recipes_dir) if args.recipes_dir else root / "recipes"
    frontmatter_dir = Path(args.frontmatter_dir) if args.frontmatter_dir else root / "frontmatter"
    images_dir = Path(args.images_dir) if args.images_dir else root / "images"

    if args.cover is None:
        # Auto-detect the sibling cover PDF alongside the interior file.
        cover_pdf_path = pdf_path.with_name(pdf_path.stem + "-cover.pdf")
    elif args.cover.lower() == "none":
        cover_pdf_path = None
    else:
        cover_pdf_path = Path(args.cover)

    log_path = Path(args.log) if args.log else pdf_path.with_suffix(".log")
    if args.cover_log:
        cover_log_path = Path(args.cover_log)
    elif cover_pdf_path is not None:
        cover_log_path = cover_pdf_path.with_suffix(".log")
    else:
        cover_log_path = None

    report = Report()
    expected_trim = _resolve_expected_trim(args.trim, sty_path, report)
    page_count = check_pdf(
        pdf_path, report,
        paper_rgb=_paper_rgb(sty_path),
        expected_trim=expected_trim,
    )
    check_transparency(pdf_path, report)
    # Source-side margin check when the .sty is available; PDF-side empirical
    # check always runs, so a PDF-only user still gets margin coverage.
    check_geometry(sty_path, page_count, report)
    check_pdf_margins(pdf_path, report)
    check_orphan_pages(pdf_path, main_tex_path, report)
    check_placeholders(recipes_dir, report)
    check_recipe_inclusion(recipes_dir, main_tex_path, report)
    check_recipe_index_entries(recipes_dir, report)
    check_images(
        images_dir,
        [main_tex_path, cover_tex_path] + sorted(recipes_dir.glob("*.tex")) + sorted(frontmatter_dir.glob("*.tex")),
        report,
    )
    check_latex_log(log_path, report)
    if cover_pdf_path is not None:
        check_cover_pdf(cover_pdf_path, report)
        check_transparency(cover_pdf_path, report, name_prefix="Cover ")
    if cover_log_path is not None:
        check_latex_log(cover_log_path, report, name_prefix="Cover ")
    check_cover_spine(cover_tex_path, page_count, report)
    check_spine_text(cover_tex_path, page_count, report)

    print(f"Lulu print check: {pdf_path}")
    for check in report.checks:
        status = check["status"]
        marker = {"PASS": "  [PASS]", "WARN": "  [WARN]", "FAIL": "  [FAIL]", "SKIP": "  [SKIP]"}[status]
        line = f"{marker} {check['name']}"
        if check["description"]:
            line += f" — {check['description']}"
        print(line)
        for e in check["errors"]:
            print(f"         ERROR:   {e}")
        for w in check["warnings"]:
            print(f"         WARNING: {w}")
        for n in check["notes"]:
            print(f"         note:    {n}")

    n_err = len(report.errors)
    n_warn = len(report.warnings)
    print()
    if n_err or n_warn:
        print(f"{n_err} error(s), {n_warn} warning(s).")
    else:
        print("Lulu print check passed with no issues.")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
