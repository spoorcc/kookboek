#!/usr/bin/env python3
"""Generate docs/recipes.json and docs/register.json from the PDF and LaTeX index."""
import json
import re
import sys
from pathlib import Path

SKIP = {"Inhoud", "Register", "Voorwoord", "Kookboek", "Index"}


def extract_recipes(pdf_path: Path) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    recipes: list[dict] = []
    chapter_boundaries: list[int] = []
    chapter: str | None = None

    def walk(items, depth: int = 0) -> None:
        nonlocal chapter
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
                continue
            title = item.title.strip()
            try:
                page = reader.get_destination_page_number(item) + 1
            except Exception:
                page = None
            if depth == 0:
                if page:
                    chapter_boundaries.append(page)
                if title not in SKIP:
                    chapter = title
            elif depth == 1 and chapter and page:
                recipes.append({"title": title, "chapter": chapter, "page": page})

    walk(reader.outline)

    for i, recipe in enumerate(recipes):
        sp = recipe["page"]
        candidates: list[int] = []
        if i + 1 < len(recipes):
            candidates.append(recipes[i + 1]["page"])
        for b in chapter_boundaries:
            if b > sp:
                candidates.append(b)
        recipe["endPage"] = (min(candidates) - 1) if candidates else total_pages

    return recipes


def extract_register(idx_path: Path) -> list[dict]:
    """Parse LaTeX .idx file into a sorted list of {entry, pages} dicts."""
    if not idx_path.exists():
        return []

    entries: dict[str, set[int]] = {}
    display: dict[str, str] = {}
    pattern = re.compile(r'\\indexentry\{([^}]+)\}\{(-?\d+)\}')

    for line in idx_path.read_text(encoding='utf-8', errors='replace').splitlines():
        m = pattern.match(line.strip())
        if not m:
            continue
        raw_term = m.group(1)
        page = int(m.group(2))
        if page <= 0:
            continue

        term = raw_term.split('|')[0]
        if '!' in term:
            term = term.split('!', 1)[1]
        term = term.strip()
        if not term:
            continue

        key = term.lower()
        if key not in entries:
            entries[key] = set()
            display[key] = term
        entries[key].add(page)

    return [
        {"entry": display[k], "pages": sorted(entries[k])}
        for k in sorted(entries)
    ]


if __name__ == "__main__":
    pdf = Path("KookboekFamilieSpoor.pdf")
    if not pdf.exists():
        sys.exit(f"ERROR: {pdf} not found — run the LaTeX build first")

    out_dir = Path("docs")
    out_dir.mkdir(exist_ok=True)

    recipes = extract_recipes(pdf)
    if not recipes:
        sys.exit(
            "ERROR: no recipes found in PDF outline.\n"
            "Check that hyperref is loaded and the PDF has bookmarks."
        )
    recipes_out = out_dir / "recipes.json"
    recipes_out.write_text(json.dumps(recipes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(recipes)} recipes to {recipes_out}")
    for r in recipes:
        print(f"  p.{r['page']:3d}–{r['endPage']:3d}  [{r['chapter']}]  {r['title']}")

    register = extract_register(Path("register.idx"))
    register_out = out_dir / "register.json"
    register_out.write_text(json.dumps(register, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(register)} register entries to {register_out}")
