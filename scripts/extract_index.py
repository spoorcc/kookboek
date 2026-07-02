#!/usr/bin/env python3
"""Generate docs/recipes.json and docs/register.json from the PDF and LaTeX index."""
import json
import re
import sys
from pathlib import Path

SKIP = {"Inhoud", "Register", "Voorwoord", "Kookboek", "Index"}


def extract_depth1_kinds(main_tex_path: Path) -> list[str]:
    """Read main.tex and return, in document order, 'subchapter' or 'recipe' for
    each \\subchapter{...} and \\input{recipes/...} line. hyperref's bookmark tree
    only nests a chapter's *first* \\subsection as the chapter's direct child;
    every later \\subsection in the same chapter nests one level deeper, as a
    child of the \\section (recipe) immediately before it. pypdf still visits
    every one of these nodes in document order regardless of nesting depth, so
    zipping this list against that visiting order (see extract_recipes) stays
    correct without having to model the exact bookmark tree shape."""
    kinds: list[str] = []
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


def extract_recipes(pdf_path: Path, main_tex_path: Path) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    kinds = iter(extract_depth1_kinds(main_tex_path))

    recipes: list[dict] = []
    boundaries: list[int] = []
    chapter: str | None = None
    subchapter: str | None = None

    def walk(items, depth: int = 0) -> None:
        nonlocal chapter, subchapter
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
                    boundaries.append(page)
                subchapter = None
                if title not in SKIP:
                    chapter = title
            elif depth >= 1 and chapter and page:
                kind = next(kinds, "recipe")
                if kind == "subchapter":
                    subchapter = title
                    boundaries.append(page)
                else:
                    recipes.append(
                        {"title": title, "chapter": chapter, "subchapter": subchapter, "page": page}
                    )

    walk(reader.outline)

    for i, recipe in enumerate(recipes):
        sp = recipe["page"]
        candidates: list[int] = []
        if i + 1 < len(recipes):
            candidates.append(recipes[i + 1]["page"])
        for b in boundaries:
            if b > sp:
                candidates.append(b)
        recipe["endPage"] = (min(candidates) - 1) if candidates else total_pages

    return recipes


def extract_register(idx_path: Path, pdf_path: Path) -> list[dict]:
    """Parse LaTeX .idx file into a sorted list of {entry, pages} dicts.

    \\index writes out \\thepage as it's printed in the book — roman numerals
    in the front matter, arabic afterwards — and \\mainmatter resets the page
    counter to 1, so that printed number is *not* the PDF's raw (1-based)
    page index needed to navigate there; e.g. printed page "1" of the main
    matter is several raw pages in, after the title page and front matter.
    Each entry in `pages` therefore pairs the printed `label` (for display,
    matching the book) with the resolved raw `page` (for navigation),
    looked up via the PDF's embedded page-label table (hyperref writes one
    automatically whenever \\pagenumbering changes). If a PDF has no page
    labels, the printed number is used as the raw index directly.
    """
    if not idx_path.exists():
        return []

    label_to_index: dict[str, int] = {}
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        for i, label in enumerate(reader.page_labels, start=1):
            label_to_index.setdefault(label, i)
    except Exception:
        pass

    entries: dict[str, dict[str, int]] = {}
    display: dict[str, str] = {}
    pattern = re.compile(r'\\indexentry\{([^}]+)\}\{([^}]+)\}')

    for line in idx_path.read_text(encoding='utf-8', errors='replace').splitlines():
        m = pattern.match(line.strip())
        if not m:
            continue
        raw_term = m.group(1)
        label = m.group(2)

        raw_index = label_to_index.get(label)
        if raw_index is None:
            try:
                raw_index = int(label)
            except ValueError:
                continue
        if raw_index <= 0:
            continue

        term = raw_term.split('|')[0]
        if '!' in term:
            term = term.split('!', 1)[1]
        term = term.strip()
        if not term:
            continue

        key = term.lower()
        if key not in entries:
            entries[key] = {}
            display[key] = term
        entries[key][label] = raw_index

    result = []
    for k in sorted(entries):
        pairs = sorted(entries[k].items(), key=lambda kv: kv[1])
        result.append({
            "entry": display[k],
            "pages": [{"label": label, "page": raw_index} for label, raw_index in pairs],
        })
    return result


if __name__ == "__main__":
    pdf = Path("KookboekFamilieSpoor.pdf")
    if not pdf.exists():
        sys.exit(f"ERROR: {pdf} not found — run the LaTeX build first")

    out_dir = Path("docs")
    out_dir.mkdir(exist_ok=True)

    recipes = extract_recipes(pdf, Path("main.tex"))
    if not recipes:
        sys.exit(
            "ERROR: no recipes found in PDF outline.\n"
            "Check that hyperref is loaded and the PDF has bookmarks."
        )
    recipes_out = out_dir / "recipes.json"
    recipes_out.write_text(json.dumps(recipes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(recipes)} recipes to {recipes_out}")
    for r in recipes:
        group = f"{r['chapter']} / {r['subchapter']}" if r["subchapter"] else r["chapter"]
        print(f"  p.{r['page']:3d}–{r['endPage']:3d}  [{group}]  {r['title']}")

    register = extract_register(Path("register.idx"), pdf)
    register_out = out_dir / "register.json"
    register_out.write_text(json.dumps(register, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(register)} register entries to {register_out}")
    for r in register:
        pages = ", ".join(f"{p['label']} (p.{p['page']})" for p in r["pages"])
        print(f"  {r['entry']}: {pages}")
