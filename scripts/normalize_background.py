#!/usr/bin/env python3
"""Whiten off-white (yellowish/greyish) backgrounds in recipe images.

The hero/margin illustrations in `images/*.{png,jpg,jpeg}` are generated
against a background that's meant to read as plain white, but often comes
out a few points off pure white with a warm (yellowish) or cool (greyish)
cast. This finds the background — the region of near-white pixels
connected to the image border — and pushes just that region to pure white,
feathering the edge so the transition into the subject stays smooth.

Every processed image also gets a thin, fixed-width vignette forced to
true (255,255,255) right at its outer edge, regardless of how far the
flood fill reaches inward. `\heroimagefade`/`\marginimage` fade the art
into the page's own pure-white background over a small band, so if the
image's *true* edge pixels are still a few points off white, that fade
can leave a faint seam that's invisible on screen but shows up once
printed. The flood fill alone doesn't guarantee this: on some images
(e.g. a plate that reaches close to the frame edge) making it reach all
the way to the true border means the mask has to cover most of the frame,
which also flattens the plate's own watercolor shading. The vignette
sidesteps that by being unconditional and edge-only — it never reaches
far enough inward to touch subject detail.

Usage:
    python3 scripts/normalize_background.py [FILE ...]
    python3 scripts/normalize_background.py --dry-run
    python3 scripts/normalize_background.py --edge-only [FILE ...]

With no FILE arguments, processes every `images/*.png`, `*.jpg`, `*.jpeg`
(not `images/originals/`, which is kept as historical source material).
`--dry-run` reports which files would change without writing anything.
`--edge-only` skips the interior flood-fill whitening and applies just the
edge vignette — use this for images where the full flood fill reaches
into real subject detail (a plate, a bowl) and flattens its shading.
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

VIGNETTE_MARGIN_FRAC = 0.02  # guaranteed pure-white band at the true edge, as a fraction of the shorter side


def edge_vignette_alpha(h, w):
    """Alpha ramp that is 1.0 exactly at the image border and fades to 0.0
    over VIGNETTE_MARGIN_FRAC of the shorter side. Unlike the flood-fill
    mask, this never depends on colour or connectivity, so it can't reach
    into real subject detail — it only ever affects a thin band at the
    true edge."""
    margin = max(1.0, VIGNETTE_MARGIN_FRAC * min(h, w))
    y = np.arange(h)[:, None].astype(np.float32)
    x = np.arange(w)[None, :].astype(np.float32)
    dist = np.minimum(np.minimum(y, h - 1 - y), np.minimum(x, w - 1 - x))
    dist = np.broadcast_to(dist, (h, w))
    return np.clip(1.0 - dist / margin, 0.0, 1.0)


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


def whiten(path, edge_only=False):
    im = Image.open(path)
    has_alpha = im.mode == "RGBA"
    rgb = im.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)
    h, w, _ = arr.shape

    vignette = edge_vignette_alpha(h, w)

    if edge_only:
        border = np.zeros((h, w), bool)
        border[:BORDER_WIDTH, :] = True
        border[-BORDER_WIDTH:, :] = True
        border[:, :BORDER_WIDTH] = True
        border[:, -BORDER_WIDTH:] = True
        ref_colour = arr[border].mean(axis=0)
        if 255 - ref_colour.min() < MIN_CAST:
            return None, f"background already near white {tuple(int(c) for c in ref_colour)}"
        alpha = np.clip(vignette, 0.0, 1.0)[..., None]
        fraction = float((vignette > 0.01).mean())
    else:
        mask, ref_colour = background_mask(arr.astype(np.int16))
        if mask is None or not mask.any():
            return None, "no clear background region found"
        if 255 - ref_colour.min() < MIN_CAST:
            return None, f"background already near white {tuple(int(c) for c in ref_colour)}"

        flood_alpha = ndimage.gaussian_filter(mask.astype(np.float32), sigma=FEATHER_SIGMA)
        alpha = np.maximum(flood_alpha, vignette)
        alpha = np.clip(alpha, 0.0, 1.0)[..., None]
        fraction = mask.mean()

    out = arr * (1 - alpha) + 255.0 * alpha
    out = np.clip(np.round(out), 0, 255).astype(np.uint8)
    out_im = Image.fromarray(out, mode="RGB")

    if has_alpha:
        out_im = out_im.convert("RGBA")
        out_im.putalpha(im.getchannel("A"))

    return (out_im, ref_colour, fraction), None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path, help="image files to process (default: all of images/)")
    parser.add_argument("--dry-run", action="store_true", help="report changes without writing files")
    parser.add_argument(
        "--edge-only",
        action="store_true",
        help="skip the interior flood-fill whitening and apply only the edge vignette "
        "(use when the flood fill reaches into real subject detail, e.g. a plate)",
    )
    args = parser.parse_args()

    files = args.files or default_files()
    if not files:
        print("no images found", file=sys.stderr)
        return 1

    for path in files:
        result, skip_reason = whiten(path, edge_only=args.edge_only)
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
