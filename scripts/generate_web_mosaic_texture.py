#!/usr/bin/env python3
"""Generate a faint mosaic-photo overlay texture for the website background.

docs/index.html shows the built PDF as a page that "floats" over a plain
grey field (the #canvas-area / main viewer background, --viewer-bg). This
reuses the actual mosaic the hardcover cover (cover/cover.tex) tiles onto
its front/back panels: the \\frontgrid/\\backgrid lists in cover.tex name,
in order, every cropped photo in cover/mosaic/*.png (produced by
scripts/generate_cover_mosaic_crops.py) that panel places. Parsing those
same lists means this texture is always the same composition as the
printed cover, in the same order, and never drifts out of sync with it.

Like \\drawmosaic in cover.tex, each tile is placed with an object-fit:
contain fit — scaled down to fit inside its cell on the longer axis and
centered, never cropped — so a dish is never cut off the way a hard
center-crop would (e.g. clipping the outer blinis off
blinis-vier-toppings.png, which is wider than the cell). The grid is then
desaturated down to a single dark tone whose per-pixel alpha follows the
photos' contrast, so compositing it over --viewer-bg in CSS darkens the
field only slightly where a dish's outline falls and leaves it at its
original grey everywhere else. Writes docs/mosaic-texture.png, referenced
by docs/index.html as a repeating, semi-transparent background image
layered on top of --viewer-bg.

Usage:
    python3 scripts/generate_web_mosaic_texture.py
"""

import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
MOSAIC_DIR = REPO_ROOT / "cover" / "mosaic"
COVER_TEX = REPO_ROOT / "cover" / "cover.tex"
OUT_FILE = REPO_ROOT / "docs" / "mosaic-texture.png"

COLUMNS = 6
CELL_W = 140
CELL_H = 95
GUTTER = 4  # fully transparent gap between tiles, px

# Overlay colour: darkens --viewer-bg where it's opaque. Kept dark and
# neutral so it reads as "the grey got slightly deeper" rather than an
# obvious colour tint.
OVERLAY_RGB = (0, 0, 0)

# Ceiling on the overlay's opacity (0-255), applied where a photo has the
# most contrast/detail (e.g. a bowl's rim). Still low enough that the
# field reads as its original grey, but high enough that each dish's
# outline is actually recognisable rather than a near-invisible haze.
MAX_ALPHA = 55

# Gaussian blur radius (px) applied before computing alpha, so fine photo
# detail (individual bread-crumb-level texture) softens into broad shapes
# instead of staying sharp enough to read as an actual photo.
BLUR_RADIUS = 1.2

# Not a recipe photo (the cover tiles its QR code into the mosaic as one
# of the tiles); skip it when picking mosaic tiles for the texture.
EXCLUDE = {"kookboek-qr"}


def cover_mosaic_names() -> list[str]:
    """Read the \\frontgrid/\\backgrid tile lists straight out of cover.tex.

    Each list is a comma-separated name/w/h1... string; only the name
    (before the first '/') is needed here.
    """
    text = COVER_TEX.read_text(encoding="utf-8")
    names = []
    for grid in ("frontgrid", "backgrid"):
        m = re.search(rf"\\def\\{grid}\{{(.*?)\}}", text)
        if not m:
            print(f"could not find \\def\\{grid}{{...}} in {COVER_TEX}", file=sys.stderr)
            continue
        for entry in m.group(1).split(","):
            name = entry.split("/")[0].strip()
            if name and name not in EXCLUDE:
                names.append(name)
    return names


def fit_contain(img: Image.Image, cell_w: int, cell_h: int) -> Image.Image:
    """Scale img to fit inside cell_w x cell_h preserving aspect ratio,
    centered on a white (cell_w x cell_h) canvas — like \\drawmosaic's
    \\includegraphics[width=\\w, height=\\h] tiles, never cropping the
    photo to force it onto the cell's own aspect ratio."""
    src_w, src_h = img.size
    scale = min(cell_w / src_w, cell_h / src_h)
    new_w = max(1, round(src_w * scale))
    new_h = max(1, round(src_h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("L", (cell_w, cell_h), 255)
    canvas.paste(resized, ((cell_w - new_w) // 2, (cell_h - new_h) // 2))
    return canvas


def main() -> int:
    names = cover_mosaic_names()
    if not names:
        print(f"no mosaic tile names parsed from {COVER_TEX}", file=sys.stderr)
        return 1

    tiles = []
    for name in names:
        path = MOSAIC_DIR / f"{name}.png"
        if not path.exists():
            print(f"skipping {name}: {path} not found", file=sys.stderr)
            continue
        tiles.append(path)
    if not tiles:
        print(f"none of the parsed mosaic tile names exist in {MOSAIC_DIR}", file=sys.stderr)
        return 1

    rows = (len(tiles) + COLUMNS - 1) // COLUMNS
    grid_w = COLUMNS * CELL_W + (COLUMNS + 1) * GUTTER
    grid_h = rows * CELL_H + (rows + 1) * GUTTER
    # Alpha starts at 0 (fully transparent gutters); tiles get pasted with
    # their per-pixel alpha derived from the photo below.
    canvas_l = Image.new("L", (grid_w, grid_h), 255)  # grayscale, white = transparent later

    for i, path in enumerate(tiles):
        col, row = i % COLUMNS, i // COLUMNS
        with Image.open(path) as im:
            tile = fit_contain(im.convert("L"), CELL_W, CELL_H)
        x = GUTTER + col * (CELL_W + GUTTER)
        y = GUTTER + row * (CELL_H + GUTTER)
        canvas_l.paste(tile, (x, y))

    canvas_l = canvas_l.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
    gray = np.asarray(canvas_l, dtype=np.float32)
    # A near-white source pixel (the photo's own background) contributes
    # ~0 alpha; a dark pixel (a dish's outline/shadow) contributes up to
    # MAX_ALPHA, so the overlay only darkens --viewer-bg near actual
    # photo detail.
    alpha = np.clip((255.0 - gray) / 255.0, 0.0, 1.0) * MAX_ALPHA

    rgba = np.zeros((grid_h, grid_w, 4), dtype=np.uint8)
    rgba[..., 0] = OVERLAY_RGB[0]
    rgba[..., 1] = OVERLAY_RGB[1]
    rgba[..., 2] = OVERLAY_RGB[2]
    rgba[..., 3] = alpha.astype(np.uint8)
    result = Image.fromarray(rgba, mode="RGBA")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.save(OUT_FILE, optimize=True)
    print(f"wrote {OUT_FILE} ({result.size[0]}x{result.size[1]}, {OUT_FILE.stat().st_size} bytes, {len(tiles)} tiles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
