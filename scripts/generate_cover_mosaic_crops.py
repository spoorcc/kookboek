#!/usr/bin/env python3
"""Generate tightly-cropped copies of the cover mosaic's hero images.

cover/cover.tex tiles every recipe's hero/served-dish photo into a grid.
The source images in images/ carry a lot of plain white margin around the
dish (they're sized for the interior's full-width \\heroimagefade), which
wastes space once shrunk into a small grid cell. This crops each one down
to the smallest bounding box that contains the whole dish — found the same
way scripts/normalize_background.py finds the background: the near-white
region connected to the image border, via flood fill, not a naive
brightness threshold, so it doesn't bite into white subject detail like a
plate or bowl — plus a small fixed margin, and writes the result to
cover/mosaic/. The crop only ever removes background: it can't cut into
the dish, because the flood fill can't cross into a non-background pixel
in the first place. images/ itself is left untouched, since those files
are also used at full size by \\heroimagefade in the interior book.

Usage:
    python3 scripts/generate_cover_mosaic_crops.py
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"
OUT_DIR = REPO_ROOT / "cover" / "mosaic"

BORDER_WIDTH = 2
WHITEISH_MIN_CHANNEL = 220
TOLERANCE = 22
MARGIN_FRAC = 0.03  # small margin added around the dish's tight bbox
MAX_DIM = 900  # cap the cropped copy's longer side (px); these only ever render at a
# few cm in the cover mosaic, so the source images' full resolution is far more than
# Lulu's 600 DPI ceiling needs and would just bloat the repo

# Every \heroimagefade target across recipes/*.tex, the same set cover.tex
# tiles into its front/back mosaic grids.
HERO_NAMES = [
    "aardappel-groente-vlees", "arretjescake", "asperge-lasagne", "blinis-vier-toppings",
    "bloemkoolpasta-hero", "bloemkoolquiche", "bobotie", "broccoli-uit-de-oven-hero",
    "broccolipasta-witvis-olijven-rode-ui", "brood", "broodje-hamburger", "broodje-knakworst",
    "burritos", "chili-con-carne", "ciabatta", "couscous", "doner-kebab", "fajitas", "falafel",
    "flammkuchen", "focaccia", "gegrilde-courgette", "geroerbakte-spruitjes-hero",
    "gevulde-paprika-hero", "gnocchi", "gnocchi-sorrentina", "gnocchi-zongedroogde-tomaten-hero",
    "groene-salade", "hamburgerbolletjes", "horiatiki", "involtini-di-maiale-hero", "jambalaya",
    "kalkoen-in-spek", "kipfilet-parmezaan-knoflook", "kippensoep-simpel", "kofta", "kokos-vis",
    "lasagne-simpel", "mac-n-cheese", "meringues",
    "nasi", "paella-hero", "parmigiana-melanzane", "pasta-amatriciana", "pasta-blauwe-kaas",
    "pasta-bolognese", "pasta-prei-hamblokjes-olijven", "pasta-primavera", "pasta-scarpariello",
    "pastinaaksoep", "pita", "pretzels", "quesadillas", "quiche-chorizo-geitenkaas",
    "quiche-groente-cirkel", "quiche-groente-geitenkaas", "quiche-ham-prei", "quiche-lorraine",
    "ravioli-rode-pesto-hero", "roti", "roze-koeken-hero", "sajoer-boontjes-hero",
    "salade-honing-mosterddressing-hero", "saltimbocca", "sauzijcenbroodjes", "schiacciata-hero",
    "semifreddo", "shakshuka", "spinazie-quiche", "spruitenstamp-hero", "tarte-tatin-witlof",
    "tomaten-pestorisotto-hero", "tompouce-geitenkaas-hero", "tortellini-al-forno-hero",
    "venkel-risotto-hero", "worstjes-rode-rijst-salade",
]


def find_source(name):
    for ext in (".png", ".jpg", ".jpeg"):
        p = IMAGES_DIR / f"{name}{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(name)


def content_bbox(arr):
    """(left, top, right, bottom) pixel bbox of the dish, or None if no
    border-connected background region is found (nothing to crop)."""
    h, w, _ = arr.shape
    border = np.zeros((h, w), bool)
    border[:BORDER_WIDTH, :] = True
    border[-BORDER_WIDTH:, :] = True
    border[:, :BORDER_WIDTH] = True
    border[:, -BORDER_WIDTH:] = True

    whiteish = arr.min(axis=2) > WHITEISH_MIN_CHANNEL
    ref_pixels = arr[border & whiteish]
    if len(ref_pixels) == 0:
        return None
    ref_colour = ref_pixels.mean(axis=0)
    dist = np.abs(arr - ref_colour).max(axis=2)
    candidate = dist < TOLERANCE

    labels, _ = ndimage.label(candidate, structure=np.ones((3, 3)))
    border_labels = set(np.unique(labels[border])) - {0}
    if not border_labels:
        return None
    bg_mask = np.isin(labels, list(border_labels))
    content = ~bg_mask

    rows = np.any(content, axis=1)
    cols = np.any(content, axis=0)
    if not rows.any():
        return None
    top, bottom = np.where(rows)[0][[0, -1]]
    left, right = np.where(cols)[0][[0, -1]]
    return int(left), int(top), int(right), int(bottom)


def crop_with_margin(im, bbox, w, h):
    left, top, right, bottom = bbox
    margin = round(MARGIN_FRAC * max(right - left, bottom - top))
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(w - 1, right + margin)
    bottom = min(h - 1, bottom + margin)
    return im.crop((left, top, right + 1, bottom + 1))


def cap_size(im):
    w, h = im.size
    longer = max(w, h)
    if longer <= MAX_DIM:
        return im
    scale = MAX_DIM / longer
    return im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in HERO_NAMES:
        src = find_source(name)
        im = Image.open(src)
        rgb = im.convert("RGB")
        arr = np.asarray(rgb).astype(np.int16)
        h, w, _ = arr.shape

        bbox = content_bbox(arr)
        if bbox is None:
            print(f"skip crop  {name}  (no clear background found, copying as-is)")
            cropped = im
        else:
            cropped = im.crop((0, 0, w, h))
            cropped = crop_with_margin(cropped, bbox, w, h)
        cropped = cap_size(cropped)

        out_path = OUT_DIR / f"{name}.png"
        cropped.save(out_path, optimize=True)
        print(f"{name}: {w}x{h} -> {cropped.size[0]}x{cropped.size[1]}  ({out_path.relative_to(REPO_ROOT)})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
