#!/usr/bin/env python3
"""Whiten off-white (yellowish/greyish) backgrounds in recipe images.

The hero/margin illustrations in `images/*.{png,jpg,jpeg}` are generated
against a background that's meant to read as plain white, but often comes
out a few points off pure white with a warm (yellowish) or cool (greyish)
cast. This finds the background — the region of near-white pixels
connected to the image border — and pushes just that region to pure white,
feathering the edge so the transition into the subject stays smooth.

Usage:
    python3 scripts/normalize_background.py [FILE ...]
    python3 scripts/normalize_background.py --dry-run

With no FILE arguments, processes every `images/*.png`, `*.jpg`, `*.jpeg`
(not `images/originals/`, which is kept as historical source material).
`--dry-run` reports which files would change without writing anything.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"

BORDER_WIDTH = 2
WHITEISH_MIN_CHANNEL = 220  # border pixels this bright seed the background reference colour
TOLERANCE = 22  # max per-channel distance from the reference colour to count as background
FEATHER_SIGMA = 1.5
MIN_CAST = 3  # skip images whose background is already this close to pure white


def default_files():
    exts = ("*.png", "*.jpg", "*.jpeg")
    files = []
    for ext in exts:
        files += sorted(IMAGES_DIR.glob(ext))
    return files


def background_mask(arr):
    """Boolean mask of background pixels: near-white and connected to the border."""
    h, w, _ = arr.shape
    border = np.zeros((h, w), bool)
    border[:BORDER_WIDTH, :] = True
    border[-BORDER_WIDTH:, :] = True
    border[:, :BORDER_WIDTH] = True
    border[:, -BORDER_WIDTH:] = True

    whiteish = arr.min(axis=2) > WHITEISH_MIN_CHANNEL
    ref_pixels = arr[border & whiteish]
    if len(ref_pixels) == 0:
        return None, None

    ref_colour = ref_pixels.mean(axis=0)
    dist = np.abs(arr - ref_colour).max(axis=2)
    candidate = dist < TOLERANCE

    labels, _ = ndimage.label(candidate, structure=np.ones((3, 3)))
    border_labels = set(np.unique(labels[border])) - {0}
    if not border_labels:
        return None, ref_colour
    mask = np.isin(labels, list(border_labels))
    return mask, ref_colour


def whiten(path):
    im = Image.open(path)
    has_alpha = im.mode == "RGBA"
    rgb = im.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)

    mask, ref_colour = background_mask(arr.astype(np.int16))
    if mask is None or not mask.any():
        return None, "no clear background region found"
    if 255 - ref_colour.min() < MIN_CAST:
        return None, f"background already near white {tuple(int(c) for c in ref_colour)}"

    alpha = ndimage.gaussian_filter(mask.astype(np.float32), sigma=FEATHER_SIGMA)
    alpha = np.clip(alpha, 0.0, 1.0)[..., None]

    out = arr * (1 - alpha) + 255.0 * alpha
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    out_im = Image.fromarray(out, mode="RGB")

    if has_alpha:
        out_im = out_im.convert("RGBA")
        out_im.putalpha(im.getchannel("A"))

    return (out_im, ref_colour, mask.mean()), None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="image files to process (default: all of images/)")
    parser.add_argument("--dry-run", action="store_true", help="report changes without writing files")
    args = parser.parse_args()

    files = args.files or default_files()
    if not files:
        print("no images found", file=sys.stderr)
        return 1

    for path in files:
        result, skip_reason = whiten(path)
        if result is None:
            print(f"skip  {path}  ({skip_reason})")
            continue
        out_im, ref_colour, fraction = result
        ref_str = f"({ref_colour[0]:.0f}, {ref_colour[1]:.0f}, {ref_colour[2]:.0f})"
        if args.dry_run:
            print(f"would whiten  {path}  bg was {ref_str}, {fraction:.0%} of frame")
        else:
            save_kwargs = {"quality": 95} if path.suffix.lower() in (".jpg", ".jpeg") else {}
            out_im.save(path, **save_kwargs)
            print(f"whitened  {path}  bg was {ref_str}, {fraction:.0%} of frame")

    return 0


if __name__ == "__main__":
    sys.exit(main())
