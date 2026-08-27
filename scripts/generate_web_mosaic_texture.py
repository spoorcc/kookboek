#!/usr/bin/env python3
"""Generate a very light gray mosaic-photo texture for the website background.

docs/index.html shows the built PDF as a page that "floats" over a plain
grey field (the #canvas-area / main viewer background, --viewer-bg). This
reuses the same tightly-cropped recipe photos that cover/cover.tex tiles
into the physical book's hardcover mosaic (cover/mosaic/*.png, produced by
scripts/generate_cover_mosaic_crops.py) to build a small tileable texture
out of that same mosaic: a grid of the recipe photos, desaturated and
blended almost entirely into white, so it reads as a faint paper-like
texture behind the page rather than a busy photo collage. Writes
docs/mosaic-texture.png, referenced by docs/index.html as a repeating
background image.

Usage:
    python3 scripts/generate_web_mosaic_texture.py
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
MOSAIC_DIR = REPO_ROOT / "cover" / "mosaic"
OUT_FILE = REPO_ROOT / "docs" / "mosaic-texture.png"

COLUMNS = 6
ROWS = 6
CELL_W = 140
CELL_H = 95
GUTTER = 4  # white gap between tiles, px

# Blend weight toward white: 0 = original photo colours, 1 = solid white.
# Tuned so the result's average lightness lands close to --viewer-bg
# (#e8e8e8) in docs/index.html, so the tiled texture reads as the same
# light-gray field with a faint photo texture rather than a separate,
# lighter patch.
WHITE_BLEND = 0.74

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
    canvas = Image.new("RGB", (grid_w, grid_h), "white")

    for i, path in enumerate(tiles):
        col, row = i % COLUMNS, i // COLUMNS
        with Image.open(path) as im:
            im = im.convert("RGB")
            tile = center_crop_to_aspect(im, CELL_W, CELL_H)
        x = GUTTER + col * (CELL_W + GUTTER)
        y = GUTTER + row * (CELL_H + GUTTER)
        canvas.paste(tile, (x, y))

    gray = canvas.convert("L").convert("RGB")
    arr = np.asarray(gray, dtype=np.float32)
    white = np.full_like(arr, 255.0)
    blended = arr * (1 - WHITE_BLEND) + white * WHITE_BLEND
    result = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), mode="RGB")

    # The blend-toward-white step collapses the image to a few dozen close
    # gray levels, so a small adaptive palette keeps this crisp while
    # cutting the file size dramatically for a texture that tiles on
    # every page load.
    quantized = result.quantize(colors=32, method=Image.MEDIANCUT, dither=Image.Dither.NONE)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    quantized.save(OUT_FILE, optimize=True)
    print(f"wrote {OUT_FILE} ({result.size[0]}x{result.size[1]}, {OUT_FILE.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
