#!/usr/bin/env python3
"""Generate a faint mosaic-photo overlay texture for the website background.

docs/index.html shows the built PDF as a page that "floats" over a plain
grey field (the #canvas-area / main viewer background, --viewer-bg). This
reuses the same tightly-cropped recipe photos that cover/cover.tex tiles
into the physical book's hardcover mosaic (cover/mosaic/*.png, produced by
scripts/generate_cover_mosaic_crops.py) to build a small tileable texture
out of that same mosaic: a grid of the recipe photos, desaturated down to
a single dark tone whose per-pixel alpha follows the photos' contrast, so
compositing it over --viewer-bg in CSS darkens the field only slightly
where a dish's outline falls and leaves it at its original grey everywhere
else (mostly-transparent gutters between tiles). Writes
docs/mosaic-texture.png, referenced by docs/index.html as a repeating,
semi-transparent background image layered on top of --viewer-bg.

Usage:
    python3 scripts/generate_web_mosaic_texture.py
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

REPO_ROOT = Path(__file__).resolve().parent.parent
MOSAIC_DIR = REPO_ROOT / "cover" / "mosaic"
OUT_FILE = REPO_ROOT / "docs" / "mosaic-texture.png"

COLUMNS = 6
ROWS = 6
CELL_W = 140
CELL_H = 95
GUTTER = 4  # fully transparent gap between tiles, px

# Overlay colour: darkens --viewer-bg where it's opaque. Kept dark and
# neutral so it reads as "the grey got slightly deeper" rather than an
# obvious colour tint.
OVERLAY_RGB = (0, 0, 0)

# Ceiling on the overlay's opacity (0-255), applied where a photo has the
# most contrast/detail (e.g. a bowl's rim). Kept very low so the mosaic
# reads as a slight darkening of the grey, not a legible photo grid.
MAX_ALPHA = 16

# Gaussian blur radius (px) applied before computing alpha, so fine photo
# detail (individual bread-crumb-level texture) softens into broad shapes
# instead of staying sharp enough to read as an actual photo.
BLUR_RADIUS = 2.5

# Not a recipe photo; skip it when picking mosaic tiles for the texture.
EXCLUDE = {"kookboek-qr.png"}


def center_crop_to_aspect(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        box = (left, 0, left + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        box = (0, top, src_w, top + new_h)
    return img.crop(box).resize((target_w, target_h), Image.LANCZOS)


def main() -> int:
    sources = sorted(
        p for p in MOSAIC_DIR.glob("*.png") if p.name not in EXCLUDE
    )
    if not sources:
        print(f"no source images found in {MOSAIC_DIR}", file=sys.stderr)
        return 1

    needed = COLUMNS * ROWS
    tiles = [sources[i % len(sources)] for i in range(needed)]

    grid_w = COLUMNS * CELL_W + (COLUMNS + 1) * GUTTER
    grid_h = ROWS * CELL_H + (ROWS + 1) * GUTTER
    # Alpha starts at 0 (fully transparent gutters); tiles get pasted with
    # their per-pixel alpha derived from the photo below.
    canvas_l = Image.new("L", (grid_w, grid_h), 255)  # grayscale, white = transparent later

    for i, path in enumerate(tiles):
        col, row = i % COLUMNS, i // COLUMNS
        with Image.open(path) as im:
            im = im.convert("RGB")
            tile = center_crop_to_aspect(im, CELL_W, CELL_H).convert("L")
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
    print(f"wrote {OUT_FILE} ({result.size[0]}x{result.size[1]}, {OUT_FILE.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
