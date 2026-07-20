#!/usr/bin/env python3
"""Measure and enlarge the real content of recipe hero images.

`\\heroimagefade` in kookboek.sty always scales a hero image to a fixed
target width (`\\textwidth` plus the margin column) and lets the height
follow the image's own aspect ratio. That means an image with a lot of
wasted white space around the actual dish renders *smaller* on the page
than one cropped tight to its content, even at the same physical width —
the wasted margin just becomes proportionally more empty height instead
of more dish.

This script measures the horizontal width of an image's real content (the
region NOT connected to a flood fill from the border, reusing
normalize_background.py's background-detection logic) as a fraction of
the full canvas width, and reports it for every `\\heroimagefade` image.
Any image whose content fraction falls below a threshold is a candidate
for a tighter crop, which enlarges the dish without touching a single
pixel of the artwork itself.

With --apply, candidates are actually cropped. Because a taller rendered
image can push a recipe onto an extra page, --apply rebuilds the book
(via latexmk, same as build.sh) and checks each affected recipe's page
count using the PDF's own bookmark outline (scripts/lulu_lint.py's
_recipe_page_ranges). Crops are tried from tightest to loosest (--tiers);
whichever tier keeps a recipe's page count unchanged is kept, and a
recipe that can't be enlarged at any tier without changing its page count
is left at its original image. `\\marginimage` images never affect
pagination (they live entirely in the margin column), so those are
cropped directly without a rebuild.

Usage:
    python3 scripts/enlarge_hero_images.py                    # scan + report only
    python3 scripts/enlarge_hero_images.py --apply             # crop candidates, verified by rebuild
    python3 scripts/enlarge_hero_images.py --apply --no-verify # crop tightest tier without rebuilding (fast, unsafe)
    python3 scripts/enlarge_hero_images.py images/foo.png --apply

With no FILE arguments, scans every image referenced by `\\heroimagefade`
or `\\marginimage` in recipes/*.tex.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize_background import background_mask  # noqa: E402
from lulu_lint import _recipe_page_ranges  # noqa: E402

import fitz  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"
RECIPES_DIR = REPO_ROOT / "recipes"
MAIN_TEX = REPO_ROOT / "main.tex"
PDF_PATH = REPO_ROOT / "KookboekFamilieSpoor.pdf"

HERO_RE = re.compile(r"\\heroimagefade(?:\[[^\]]*\])?\{images/([^}]+)\}")
MARGIN_RE = re.compile(r"\\marginimage\{images/([^}]+)\}")
TITLE_RE = re.compile(r"\\begin\{recipe\}\{([^}]+)\}")

DEFAULT_MIN_FRACTION = 0.6
DEFAULT_TIERS = "0.15,0.25,0.4,0.6"


def default_files():
    exts = ("*.png", "*.jpg", "*.jpeg")
    files = []
    for ext in exts:
        files += sorted(IMAGES_DIR.glob(ext))
    return files


def content_bbox(path):
    """Bounding box (left, top, right, bottom), half-open, of the
    non-background content of an image. Background is the border-connected
    near-white region (same flood fill as normalize_background.py); a
    transparent border counts as background too. Returns None if the whole
    frame is background (nothing to measure)."""
    im = Image.open(path)
    has_alpha = im.mode == "RGBA"
    rgb = im.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)
    mask, _ref_colour = background_mask(arr.astype(np.int16))
    h, w = arr.shape[:2]
    content = np.ones((h, w), bool) if mask is None else ~mask
    if has_alpha:
        alpha = np.asarray(im.getchannel("A"))
        content &= alpha > 10
    ys, xs = np.where(content)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def width_fraction(path, bbox=None):
    im = Image.open(path)
    if bbox is None:
        bbox = content_bbox(path)
    if bbox is None:
        return 1.0
    left, _top, right, _bottom = bbox
    return (right - left) / im.size[0]


def cropped_box(bbox, canvas_size, padding_frac):
    """A crop box centred on bbox, padded by padding_frac of the content's
    own width/height on every side, clipped to the canvas."""
    left, top, right, bottom = bbox
    w, h = canvas_size
    cw, ch = right - left, bottom - top
    cx, cy = (left + right) / 2, (top + bottom) / 2
    half_w = cw / 2 + cw * padding_frac
    half_h = ch / 2 + ch * padding_frac
    l = max(0, int(round(cx - half_w)))
    t = max(0, int(round(cy - half_h)))
    r = min(w, int(round(cx + half_w)))
    b = min(h, int(round(cy + half_h)))
    return l, t, r, b


def build_image_maps():
    """Return (hero_map, margin_map): image stem -> recipe .tex path, for
    every `\\heroimagefade{images/...}` and `\\marginimage{images/...}`
    reference in recipes/*.tex."""
    hero_map, margin_map = {}, {}
    for path in sorted(RECIPES_DIR.glob("*.tex")):
        text = path.read_text(encoding="utf-8")
        for m in HERO_RE.finditer(text):
            hero_map[m.group(1)] = path
        for m in MARGIN_RE.finditer(text):
            margin_map[m.group(1)] = path
    return hero_map, margin_map


def recipe_title(recipe_path):
    m = TITLE_RE.search(recipe_path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def build_book():
    result = subprocess.run(
        ["latexmk", "-xelatex", "-jobname=KookboekFamilieSpoor", "main.tex"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout[-4000:], file=sys.stderr)
        print(result.stderr[-4000:], file=sys.stderr)
        raise RuntimeError("latexmk failed — see output above")


def recipe_page_counts(titles):
    """{title: page_count} for the given recipe titles, read from the
    currently-built PDF_PATH via its own bookmark outline."""
    doc = fitz.open(PDF_PATH)
    try:
        ranges = {r["title"]: r["endPage"] - r["page"] + 1 for r in _recipe_page_ranges(doc, MAIN_TEX)}
    finally:
        doc.close()
    return {title: ranges.get(title) for title in titles}


def scan(files, hero_map, margin_map, min_fraction):
    rows = []
    for path in files:
        stem = path.stem
        recipe = hero_map.get(stem) or margin_map.get(stem)
        kind = "heroimagefade" if stem in hero_map else ("marginimage" if stem in margin_map else "unreferenced")
        bbox = content_bbox(path)
        frac = width_fraction(path, bbox)
        im_size = Image.open(path).size
        candidate = kind in ("heroimagefade", "marginimage") and frac < min_fraction
        rows.append(
            {
                "path": path,
                "size": im_size,
                "bbox": bbox,
                "fraction": frac,
                "kind": kind,
                "recipe": recipe,
                "candidate": candidate,
            }
        )
    return rows


def print_scan(rows):
    for row in rows:
        w, h = row["size"]
        tag = "candidate" if row["candidate"] else row["kind"]
        print(f"{row['path'].name:38s} {w:5d}x{h:<5d}  content width {row['fraction']:5.0%}  {tag}")


def is_noop_box(box, size):
    """True if a crop box covers the whole canvas — i.e. the requested
    padding was too generous to remove any margin at all, so cropping to
    it would leave the file byte-for-byte the image it already is."""
    l, t, r, b = box
    w, h = size
    return l <= 0 and t <= 0 and r >= w and b >= h


def apply_margin_images(rows, tiers):
    """`\\marginimage` crops never affect pagination — apply the tightest
    tier that actually crops anything, no rebuild needed."""
    for row in rows:
        if row["kind"] != "marginimage" or not row["candidate"]:
            continue
        for frac in tiers:
            box = cropped_box(row["bbox"], row["size"], frac)
            if not is_noop_box(box, row["size"]):
                break
        else:
            print(f"skipped {row['path'].name}  (marginimage, content already fills the frame at every tier)")
            continue
        Image.open(row["path"]).crop(box).save(row["path"])
        print(f"cropped {row['path'].name} (marginimage, padding {frac:g}, no page-count risk)")


def apply_hero_images(rows, tiers):
    """`\\heroimagefade` crops can push a recipe onto an extra page. Try
    tiers from tightest to loosest, rebuilding and checking each affected
    recipe's page count after every tier; keep whichever tier is the
    tightest that leaves the page count unchanged, and revert to the
    original image for any recipe that can't be enlarged safely. A tier
    whose padding is so generous the crop box covers the whole canvas is
    skipped without a rebuild — it wouldn't change the file at all, so it
    would trivially "pass" the page-count check without enlarging anything."""
    candidates = [r for r in rows if r["kind"] == "heroimagefade" and r["candidate"]]
    if not candidates:
        return

    backups = {row["path"]: row["path"].read_bytes() for row in candidates}
    titles = {row["path"]: recipe_title(row["recipe"]) for row in candidates}

    print(f"building baseline ({len(candidates)} candidate image(s)) ...")
    build_book()
    baseline = recipe_page_counts(list(titles.values()))

    remaining = list(candidates)
    locked = {}
    exhausted = []  # every tier was a no-op for this image: nothing to crop
    for frac in tiers:
        if not remaining:
            break
        to_build, noop_this_tier = [], []
        for row in remaining:
            box = cropped_box(row["bbox"], row["size"], frac)
            if is_noop_box(box, row["size"]):
                noop_this_tier.append(row)
                continue
            Image.open(row["path"]).crop(box).save(row["path"])
            to_build.append(row)

        # A no-op at this tier is a no-op at every looser tier too (the box
        # only ever grows), so these images are done for good.
        exhausted.extend(noop_this_tier)
        remaining = to_build
        if not remaining:
            continue

        print(f"building with padding {frac:g} for {len(remaining)} image(s) ...")
        build_book()
        after = recipe_page_counts([titles[row["path"]] for row in remaining])

        still_remaining = []
        for row in remaining:
            title = titles[row["path"]]
            if after.get(title) == baseline.get(title):
                locked[row["path"]] = frac
            else:
                row["path"].write_bytes(backups[row["path"]])
                still_remaining.append(row)
        remaining = still_remaining

    for row in remaining + exhausted:
        row["path"].write_bytes(backups[row["path"]])

    for row in candidates:
        path = row["path"]
        if path in locked:
            print(f"kept    {path.name}  padding {locked[path]:g}  (page count unchanged: {baseline[titles[path]]})")
        elif row in exhausted:
            print(f"skipped {path.name}  (content already too close to full width; no tier gives a real crop)")
        else:
            print(f"skipped {path.name}  (every crop that changed the file also changed '{titles[path]}''s page count from {baseline[titles[path]]})")

    print("re-run build.sh to get a PDF that matches the final images/ state.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="image files to scan (default: every hero/margin image)")
    parser.add_argument(
        "--min-fraction",
        type=float,
        default=DEFAULT_MIN_FRACTION,
        help=f"content-width fraction below which an image is a candidate (default {DEFAULT_MIN_FRACTION})",
    )
    parser.add_argument("--apply", action="store_true", help="crop candidates instead of only reporting")
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="with --apply, crop heroimagefade candidates at the tightest tier without rebuilding to check "
        "page counts (fast, unsafe — only use if you'll check the build yourself)",
    )
    parser.add_argument(
        "--tiers",
        default=DEFAULT_TIERS,
        help=f"comma-separated padding fractions, tightest first (default {DEFAULT_TIERS})",
    )
    args = parser.parse_args()

    files = args.files or default_files()
    if not files:
        print("no images found", file=sys.stderr)
        return 1

    hero_map, margin_map = build_image_maps()
    rows = scan(files, hero_map, margin_map, args.min_fraction)
    print_scan(rows)

    if not args.apply:
        return 0

    tiers = [float(x) for x in args.tiers.split(",")]
    if not any(row["candidate"] for row in rows):
        print("no candidates to enlarge")
        return 0

    apply_margin_images(rows, tiers)

    if args.no_verify:
        tightest = min(tiers)
        for row in rows:
            if row["kind"] != "heroimagefade" or not row["candidate"]:
                continue
            box = cropped_box(row["bbox"], row["size"], tightest)
            Image.open(row["path"]).crop(box).save(row["path"])
            print(f"cropped {row['path'].name} (padding {tightest:g}, UNVERIFIED — page count not checked)")
        return 0

    apply_hero_images(rows, tiers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
