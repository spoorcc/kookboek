#!/usr/bin/env python3
"""Generate docs/recipes.json from PDF bookmarks (requires: pip install pypdf)."""
import json
import sys
from pathlib import Path

# Chapter-level bookmark titles that are not recipe groups
SKIP = {"Inhoud", "Register", "Voorwoord", "Kookboek", "Index"}


def extract(pdf_path: Path) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    recipes: list[dict] = []
    chapter_boundaries: list[int] = []   # page numbers of every depth-0 bookmark
    chapter: str | None = None

    def walk(items, depth: int = 0) -> None:
        nonlocal chapter
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
                continue
            title = item.title.strip()
            try:
                page = reader.get_destination_page_number(item) + 1  # 1-indexed
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

    # Compute endPage for each recipe.
    # A recipe ends just before the earliest of:
    #   • the next recipe's start page, or
    #   • the next chapter-level boundary (chapter heading / Register / …)
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


if __name__ == "__main__":
    pdf = Path("KookboekFamilieSpoor.pdf")
    if not pdf.exists():
        sys.exit(f"ERROR: {pdf} not found — run the LaTeX build first")

    data = extract(pdf)
    if not data:
        sys.exit(
            "ERROR: no recipes found in PDF outline.\n"
            "Check that hyperref is loaded and the PDF has bookmarks."
        )

    out = Path("docs/recipes.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(data)} recipes to {out}")
    for r in data:
        print(f"  p.{r['page']:3d}–{r['endPage']:3d}  [{r['chapter']}]  {r['title']}")
