# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A vintage, two-color family cookbook (*Kookboek — Familie Spoor*) typeset in LaTeX, printed via Lulu as a **hardcover casewrap**. Output is `main.pdf` at Lulu Crown Quarto trim (189 × 246 mm / 7.44 × 9.68 in) — this is the interior *text-block* trim. The case (cover) is physically larger (443.05 × 290.32 mm wrapped sheet, per `q6qdvpe-cover-template.pdf`) since a hardcover case wraps around the block with a small overhang; see "Wraparound cover" below.

## Development environment

Open the repo in VS Code and choose **Reopen in Container**. The devcontainer (`.devcontainer/devcontainer.json` + `Dockerfile`) provides:

- **texlive/texlive** (full TeX Live) with XeLaTeX and `latexmk`
- **EB Garamond** and **Nothing You Could Do** vendored as TTF files in `fonts/`
- **LaTeX Workshop** VS Code extension (auto-builds on save)
- **Claude Code** VS Code extension

### Installing the toolchain outside the devcontainer

Some sessions (e.g. Claude Code on the web) run in a plain Ubuntu container without the devcontainer image, so `xelatex`/`latexmk` aren't preinstalled there. Install the same toolchain the devcontainer's `Dockerfile` and `.github/workflows/build-pdf.yml` use, via `apt-get` (needs root/sudo):

```sh
apt-get update
apt-get install -y --no-install-recommends \
  texlive-xetex texlive-latex-extra texlive-fonts-extra texlive-fonts-recommended texlive-lang-european texlive-pictures latexmk \
  texlive-bibtex-extra biber \
  hunspell hunspell-nl \
  qpdf ghostscript python3-pip
pip3 install --no-cache-dir pymupdf || pip3 install --no-cache-dir --break-system-packages pymupdf
```

This installs enough of TeX Live (xetex + latex-extra + fonts-extra + fonts-recommended + lang-european + pictures, not the multi-GB `texlive-full`) to build `main.tex` and `cover/cover.tex`, plus `texlive-bibtex-extra`/`biber` for the Bibliografie (see "Bibliografie" below), `hunspell`/`hunspell-nl` for `scripts/spellcheck.py`, and `qpdf`/`ghostscript`/`pymupdf` for `scripts/flatten_transparency.py` and `scripts/lulu_lint.py`. Takes a few minutes and roughly 1–2 GB of disk; check available space first (`df -h /`) since some remote sessions have a fixed disk allowance. `texlive-fonts-recommended` specifically is needed for `hyperref`'s `pzdr` (Zapf Dingbats) metric — without it XeLaTeX fails with `Font \XeTeXLink@font=pzdr ... not loadable`. Fonts for the book's own typefaces are already vendored in `fonts/`, no separate font install needed for those.

## Build

```sh
./build.sh
```

This runs `latexmk -xelatex main.tex` and writes `main.pdf`. Fonts are vendored in `fonts/` so no system-level font installation is needed.

For a manual build (needed when `latexmk` is unavailable):
```sh
xelatex main.tex
makeindex -o register.ind register.idx
xelatex main.tex
xelatex main.tex   # third pass resolves all cross-references
```

`build.sh` also builds `cover/cover.tex` into `KookboekFamilieSpoor-cover.pdf` — the wraparound cover uploaded to Lulu separately from the interior file.

CI (`.github/workflows/build-pdf.yml`) runs the same `latexmk` commands for both files, runs the Lulu print-readiness check on the interior, and uploads both PDFs as artifacts.

## Lulu print-readiness check

This book is printed via [Lulu](https://www.lulu.com). `scripts/lulu_lint.py` checks the built PDF and LaTeX source against Lulu's print requirements:

- Trim size is one of the 17 Lulu trims from the Book Creation Guide p11 table (Crown Quarto, A5, US Trade, etc.) on every page — no-bleed or with-bleed variant. The intended trim is inferred from `kookboek.sty`'s `geometry` paperwidth/paperheight (this project pins to Crown Quarto, 189×246mm) and the PDF is enforced against it; pass `--trim NAME` to override, `--trim any` to accept any Lulu trim without enforcement
- All fonts are embedded (interior and wraparound cover)
- The PDF is not encrypted / password-protected (Lulu Book Creation Guide p23/p24)
- Full-bleed artwork doesn't touch the page edge unless the page includes Lulu's bleed margin
- Image resolution is between 300 and 600 DPI at printed size (Lulu's stated PPI band)
- Margins in `kookboek.sty`'s `geometry` settings meet Lulu's 12.7mm safety margin
- The `geometry` `inner` margin meets Lulu's absolute gutter floor and, ideally, the "Recommended Total Inside Margin" for the current page count (guide p9 "Gutter Additions" table)
- Page count meets Lulu's binding minimums, is a multiple of 4, and doesn't exceed the 800-page hardcover cap (guide p14 spine table)
- The wraparound cover's `\interiorpagecount` matches the built interior page count and `\spinew` is close to Lulu's hardcover-spine table bucket for that page count (guide p14)
- No spine text on books ≤ 80 pages (guide p17)
- Recipes don't still contain placeholder macros (`\heroplaceholder`, `\ingredientsketch`, `\writelines`)
- No recipe leaves just one leftover step behind on its last page (a single-step widow page)
- Every `recipes/*.tex` file is `\input` by `main.tex`, and every such `\input` points at a file that actually exists
- Every recipe has at least one `\index[register]{...}` entry, so the dish is findable in the Register
- Every `images/...` reference in the LaTeX sources resolves to a file in `images/`, and every file in `images/` is referenced from somewhere
- The interior and cover `.log` from the latexmk/xelatex run have no undefined references/citations, no missing glyphs, no LaTeX errors survived in nonstopmode, no multiply-defined labels, and no overfull/underfull `\hbox`es past a noticeable-on-the-page threshold

`build.sh` runs it automatically after every build. Run it manually with:

```sh
python3 scripts/lulu_lint.py KookboekFamilieSpoor.pdf
```

Every source path (`--sty`, `--main-tex`, `--cover-tex`, `--recipes-dir`, `--frontmatter-dir`, `--images-dir`, `--log`, `--cover-log`) defaults from `--repo-root` (or, for the two `.log` paths, from the PDF path with a `.log` extension) but can be overridden individually. In PDF-only mode (no sources available) the linter prints an explicit skip note per source-dependent check and falls back to an empirical PDF-side margin measurement so Lulu's 12.7mm safety zone still gets checked; the same applies to the `.log`-dependent check when no `.log` file is found. The linter auto-detects the sibling wraparound cover PDF (`KookboekFamilieSpoor-cover.pdf` alongside the interior) and runs cover-specific checks on it when it exists; pass `--cover none` to skip cover-PDF checks explicitly. Trim-size, font-embedding, encryption, bleed, margin, over-cap page-count, missing `\input`/image references, and undefined-reference/missing-glyph/LaTeX-error log problems are reported as errors and fail the build. Unfinished-recipe placeholders, low- or high-DPI art, odd page counts, single-step widow pages, a below-recommendation inner margin, a stale cover `\interiorpagecount`/`\spinew`, a recipe file that exists but isn't `\input`, a recipe with no Register entry, an unused image file, and multiply-defined labels or noticeable overfull/underfull `\hbox`es are reported as warnings and don't fail the build — pass `--strict` to also fail on those (e.g. right before uploading to Lulu). The interior trim-size, bleed and margin checks target the interior file's text-block trim; the wraparound cover (see below) is deliberately sized larger for the hardcover case and has its own separate cover checks.

## Dutch spelling check

`scripts/spellcheck.py` checks the Dutch prose in `main.tex`, `frontmatter/*.tex`, and `recipes/*.tex` against hunspell's `nl_NL` dictionary. It strips this project's LaTeX macros (`\ing`, `\kicker`, `\lettrine`, `\tip`, TikZ diagrams, cross-references, etc.) down to plain prose first — the generic hunspell TeX filter doesn't know these custom macros and mangles them — then runs the result through `hunspell`. Words that are correct but missing from the dictionary (recipe/dish names, loanwords like *prosciutto* or *cacio e pepe*, brand names, Dutch elision-hyphen fragments like `boven-` in "boven- en onderwarmte") live in `scripts/spellcheck-wordlist.txt`, matched case-insensitively. CI (`.github/workflows/build-pdf.yml`) installs `hunspell`/`hunspell-nl` and runs this before the build; it fails the build on any word outside the dictionary and wordlist. Run it locally with:

```sh
python3 scripts/spellcheck.py
```

New recipe vocabulary that's correct but unrecognised should be added to `scripts/spellcheck-wordlist.txt` (one word per line, lowercase) rather than worked around — only add a word after confirming it isn't actually a typo.

## Image background normalization

`scripts/normalize_background.py` whitens off-white (yellowish or greyish) backgrounds in `images/*.png`/`.jpg`/`.jpeg`. It finds the near-white region connected to each image's border (via a colour-distance flood fill from the border, not a naive brightness threshold, so it doesn't bleed into white elements that are part of the subject itself, like a plate or bowl), pushes just that region to pure white, and feathers the mask edge so the transition into the subject stays smooth. Images whose background is already close to pure white are left untouched. Run it with:

```sh
python3 scripts/normalize_background.py [FILE ...]   # defaults to all of images/
python3 scripts/normalize_background.py --dry-run    # report only, no writes
```

Needs `pillow`, `numpy`, and `scipy` (see `scripts/requirements.txt`). Not wired into `build.sh` or CI — this is a one-off/as-needed cleanup tool for new or re-generated illustrations, not a check that should run on every build. Re-run it after adding new hero/margin art if the generated background comes out with a visible cast.

## Wraparound cover (`cover/cover.tex`)

`cover/cover.tex` is a standalone LaTeX document (not `\input` by `main.tex`) producing Lulu's wraparound cover: back cover, spine, and front cover as one page, sized to the hardcover case size (195.33 × 258.57mm, larger than the interior's 189×246mm text-block trim — see "Project" above) plus Lulu's 15.87mm wrap area on every outer edge. It reuses the same fonts and colours as `kookboek.sty` and the front cover's photo and title block from `main.tex`. The cover's `\trimw`/`\trimh` intentionally do **not** match `kookboek.sty`'s `paperwidth`/`paperheight` — don't "fix" that.

Hardcover casewrap spine width isn't a continuous formula — per Lulu's Developer Portal ("How is spine width calculated?", help.lulu.com), it comes from a fixed page-count bucket table (mirrored in `scripts/lulu_lint.py`'s `HARDCOVER_SPINE_TABLE`), where every page count within a bucket gets the exact same spine width. `\spinew` in `cover/cover.tex` was confirmed against a real template from Lulu's Project Creation Tool for a 223-page interior (0.813in / 20.65mm), which matches the documented 223–250-page bucket value (0.8125in / 20.6375mm) almost exactly. `\interiorpagecount` must still be updated whenever the interior's page count changes; `\spinew` only needs updating if the new page count falls in a *different* bucket (look it up in the table rather than re-deriving it) — regenerating a template from Lulu's Project Creation Tool is still the ultimate check before ordering a real proof, but isn't strictly required just to know the number.

## Architecture

| File | Role |
|---|---|
| `main.tex` | Document root: cover, front matter, chapter/recipe order, Inhoud (ToC), Register (index) |
| `kookboek.sty` | All styling and every recipe macro |
| `cover/cover.tex` | Lulu wraparound cover (back + spine + front), built and uploaded separately |
| `frontmatter/voorwoord.tex` | Foreword, `\input` first, right after `\frontmatter` |
| `frontmatter/hoe-dit-boek-te-lezen.tex` | Hoe dit boek te lezen: book structure (Inhoud/Register) and bakkerspercentage explainer, part of the Inleiding section, `\input` first within it, right after Inhoud (the ToC) |
| `frontmatter/seizoenskalender.tex` | Groente- en fruitkalender, part of the Inleiding section, `\input` after hoe-dit-boek-te-lezen |
| `frontmatter/basisvoorraad.tex` | Basisvoorraad checklist (pantry staples), part of the Inleiding section, `\input` after the seizoenskalender |
| `frontmatter/basisapparatuur.tex` | Basisapparatuur checklist (pans, bakeware, small appliances, hand tools, measuring tools, with sizes/capacities), part of the Inleiding section, `\input` after basisvoorraad |
| `frontmatter/portiegrootte.tex` | Portiegrootte (default portie count, hoeveelheden per persoon), part of the Inleiding section, `\input` after basisapparatuur |
| `frontmatter/kleine-maten.tex` | Kleine maten: vertical timeline of vague quantity terms (mespunt to scheutje), part of the Inleiding section, `\input` after portiegrootte, last thing before `\mainmatter` |
| `backmatter/kerntemperatuur.tex` | Kerntemperatuur appendix: meat pasteurization time/temperature table and food-safety guidance, `\input` after `\backmatter`, before the Register |
| `backmatter/kooktemperaturen.tex` | Kooktemperaturen appendix: vertical timeline of cooking-chemistry temperature milestones (4 °C to 230+ °C), `\input` after kerntemperatuur, before the Register |
| `backmatter/bibliografie.tex` | Bibliografie: every external source/link used anywhere in the book, `\input` after `\printindex[register]`, the literal last thing before `\end{document}` — see "Bibliografie" below |
| `recipes/*.tex` | Individual recipes, one file each |

**Chapters = categories** (e.g. `\chapter{Hoofdgerechten}`), **sections = recipes** (created by the `recipe` environment), **subsections = groups of recipes within a chapter** (created by `\subchapter{…}`, e.g. `\subchapter{Pasta \& risotto}`). The Inhoud and Register rebuild automatically on the next LaTeX run.

## Macros defined in `kookboek.sty`

| Macro / env | Purpose |
|---|---|
| `\begin{recipe}{Titel}` | Opens a new page + `\section`; close with `\end{recipe}` |
| `\subchapter{Naam}` | Opens a new page + `\subsection`; groups recipes within a chapter, listed in the Inhoud |
| `\kicker{…}` | Small-caps category line above the title — properties of the dish itself: course · protein/diet · cuisine · optional context tag (see below) |
| `\meta{… \dvd … \dvd …}` | Properties of the cooking itself: time · optional servings · optional effort/method tag (`\dvd` = ♦ separator). No cuisine here — that lives in `\kicker` |
| `\blockrule{Ingrediënten}` / `\blockrule{Bereiding}` | Labelled terracotta rule |
| `\begin{ingredients}` … `\end{ingredients}` | Two-column ingredient list |
| `\ing{amount}{name}` | Ingredient with right-aligned amount |
| `\ingb{name}` | Bullet ingredient (no fixed amount) |
| `\begin{steps}` … `\end{steps}` | Numbered preparation steps |
| `\tip{…}` | Margin note (*Tip van Ben*) in handwriting font |
| `\heroplaceholder{caption}` | Dashed placeholder box for the hero illustration |
| `\heroimage{file}{caption}` | Real hero illustration (swap in when art is ready) |
| `\ingredientsketch{label}` | Dashed margin sketch placeholder |
| `\marginimage{file}` | Small real photo confined to the margin column, no caption or border (unlike `\heroimage`/`\heroimagefade`, costs no vertical space in the main text column — keeps a short recipe on one page) |
| `\writelines{n}` | Ruled lines for recipes whose method hasn't been written yet |
| `\lettrine{X}{rest}` | Terracotta drop cap opening a paragraph |

### Kicker vs. meta

`\kicker` and `\meta` look alike (same small-caps terracotta style) but split different information — don't let a tag drift into the wrong one:

- **`\kicker[Terms]{...}`** — what you get on the table. Up to four `·`-separated segments, in order: course (Hoofdgerecht/Bijgerecht/Voorgerecht/Dessert/Bakken/Brood & basis), protein/diet (Vlees/Vis/Vegetarisch/Vegan/Zoet), cuisine (Italiaans, Mexicaans, ...), and an optional context tag (Doordeweeks, Kinderen, Kerst, Hartig, Pittig, Basisrecept, Snack, ...). Example: `\kicker[Hoofdgerecht,Vlees,Italiaans,Doordeweeks]{Hoofdgerecht · vlees · Italiaans · doordeweeks}`.
- **`\meta{...}`** — what cooking it takes. Up to three `\dvd`-separated segments, in order: bereidingstijd, optional portie-opbrengst (omit "Voor 5 personen" — that's the book's default), and an optional effort/method tag (Eén pan, Snel, Eenvoudig, an oven temperature). Example: `\meta{40 minuten \dvd Voor 6 porties \dvd Eén pan}`.
- Cuisine belongs only in `\kicker`, never repeated in `\meta`.
- Diet/allergen tags (glutenvrij, lactosevrij, notenvrij) are intentionally not part of this scheme — mislabeling those is a food-safety risk, not just a style slip.
- Bereidingstijd is written purely in minutes, not a mixed "uur + minuten" combo: `100 minuten`, not `1 uur 40`; `70 minuten`, not `1 uur 10`. A clean round hour count (`1 uur`, `2 uur`, `1{,}5 uur`) is fine as-is — it's the mixed notation that gets converted.

## Reuse existing Register and kicker terms

Before adding a new `\index[register]{...}` entry or picking a `\kicker` cuisine/context term, grep `recipes/*.tex` for how the same concept is already spelled elsewhere in the book and reuse that exact term rather than inventing a synonym or a different grammatical form. The Register and the kicker cuisine tags are flat lists with no synonym-merging, so any drift creates a duplicate heading or an inconsistent tag between otherwise-similar recipes:

- **Register entries**: match existing singular/plural and spelling choices (`Tomaat` not `Tomaten`, `Maïs` with the trema, plain `Kip` rather than splitting into `Kipfilet`/`Kipdijfilet`) so the same ingredient always collects under one Register heading instead of splitting across near-duplicates.
- **Kicker cuisine tags**: reuse the term already used by other recipes from the same cuisine/region (`Midden-Oosters`, not `Arabisch`, to match falafel/kofta/shoarma/shoarmabroodjes) rather than a synonym, and match the specificity level of comparable dishes (if a sibling dish from another region of the same country gets the region-specific tag — e.g. `Elzassisch` for flammkuchen — a dish whose intro text names its own specific region, like quiche lorraine's "Lotharingse", should get equally specific treatment rather than falling back to the generic country name).
- **Bakken/Dessert sweet dishes**: use `Zoet` in the protein/diet kicker slot like their sibling recipes in the same chapter, rather than substituting an unrelated tag or dropping the slot entirely.

## Bibliografie

Every external source or link used anywhere in the book — recipe attributions (e.g. "Met dank aan ... naar haar recept") as well as sourced facts in the appendices (e.g. the Kerntemperatuur richttabel's USDA/FDA sources) — is a BibTeX entry in `backmatter/bibliografie.bib`, cited from the running text with `\cite{key}` and typeset as a numbered list by `\printbibliography` in `backmatter/bibliografie.tex`. That file is `\input` after `\printindex[register]` in `main.tex`, deliberately the very last thing in the book, after the Register. Building requires `biber` (see the devcontainer/CI toolchain — `texlive-bibtex-extra` + `biber`); `latexmk` invokes it automatically, no separate build step needed.

The bibliography is powered by `biblatex` (`style=numeric, sorting=none, backend=biber`), configured in `kookboek.sty`. `sorting=none` lists entries in citation order — i.e. wherever the source is first `\cite`'d in the book — which is what keeps entry numbers matching the "recipes before backmatter appendices, earlier before later" convention below without any manual reordering. `kookboek.dbx` declares one custom field, `urldisplay` (biblatex data-model changes can only come from a `.dbx` file, not the document preamble); it holds the short, print-friendly link text shown in place of the full URL. Custom `\DeclareBibliographyDriver` definitions for the `online` and `book` entry types in `kookboek.sty` reproduce the book's plain "Auteur. Titel, korte context." look rather than biblatex's academic defaults.

When a recipe or appendix cites an external source:
- Add a new entry to `backmatter/bibliografie.bib` (`@online` for a web page/video, `@book` for a printed book) rather than embedding the raw URL or a bare domain in the recipe/appendix text. Fields: `author` (wrap an organisation name in double braces, e.g. `{{Voedingscentrum}}`, so BibTeX doesn't try to parse it as a personal name), `title`, `note` (the short "gebruikt voor .../de basis voor ..." context, no trailing period), `url` and `urldisplay` for `@online`; `publisher` and `year` instead of `url`/`urldisplay` for `@book`.
- Cite it from the text with `\cite{key}` (renders as a terracotta `[n]`) — don't add a "zie de bibliografie achterin" pointer phrase, the numbered citation already does that job. Multiple sources for the same claim can share one call: `\cite{key-one,key-two}`.
- Set `urldisplay` to a short, readable form of the URL (e.g. `ah.nl/r/1055570`, `voedingscentrum.nl/...`) rather than relying on the raw URL — a long URL, especially one with encoded `%20` spaces, often won't break cleanly and overflows the page margin, and nobody retypes a 150-character URL from a page anyway.
- New entries just need to exist in the `.bib` file with a `\cite` pointing at them somewhere in citation order; there's no need to touch `backmatter/bibliografie.tex` itself or manually renumber anything — `sorting=none` handles ordering automatically.
- Double-check names and titles against the actual source (a misspelled author name is worse than no attribution) — see the `khoo-tartetatin`/`witzenhausen-risotto` entries for the pattern.

## Ingredient ordering

Within a `\begin{ingredients}` … `\end{ingredients}` block, order matters:

0. **Named-in-the-title ingredient(s) first, above all else.** If the recipe title itself names an ingredient — as the first half of a compound dish name (bloemkool**pasta**, andijvie**stamp**, boerenkool**stamp**, spinazie**quiche**, venkel**risotto**, pastinaak**soep**) or via an explicit "met X(, Y en Z)" / "van X" clause (*Boerenkoolstamp met rookworst*, *Quiche met ham en prei*, *Tomatensoep van geroosterde tomaten*) — that ingredient leads the list, in the order the title names it, ahead of the protein/starch/vegetable heuristic below. This applies even when the named ingredient wouldn't otherwise be the protein/starch/vegetable pick (e.g. *Riso freddo* → rijst first; *IJstaart met karamel en chocolade* → karamel, chocolade first). Generic dish-type words that aren't themselves a specific ingredient (pasta, gnocchi, tortellini, quiche, stamp, soep, risotto, salade, taart used as the bare head noun with no modifier) don't force anything — only an actual named foodstuff does. This is why the `gnocchi-*` and `tortellini-al-forno` recipes keep gnocchi/tortellini itself at the front of their lists ahead of the "met X en Y" ingredients named alongside it in the title — gnocchi and tortellini are treated the same as pasta, not as a named ingredient.
1. **Protein** first (vlees, vis, gehakt, worst, ei, peulvruchten — or, in a vegetarian dish where cheese carries the dish, a cheese like feta/geitenkaas/gorgonzola).
2. **Zetmeel** (the classic starchy staple: aardappel/rijst/pasta/couscous/noodles, or a bread/wrap/tortilla serving as the dish's carrier).
3. **Hoofdgroente** (the single vegetable that's central to the dish), if there is one clear candidate.
4. Everything else, in whatever order already reads naturally (aromatics, dairy, spices, liquids).
5. `\ingb{…}` items always last, in their existing relative order — these are bullet ingredients without a fixed amount (to taste, a splash, a garnish) and stay at the back regardless of category.

This ordering applies to a dish's main ingredient list. It does **not** apply to:
- Pastry/dough sub-blocks (a quiche crust, bread dough, pizza dough) — keep the standard baking order (bloem, vet, ei, zout, ...) since there's no protein/starch/vegetable split to make. When ingredients in the block carry a baker's-percentage annotation relative to flour (`(56\%)`, `(2\%)`, ...), bloem/broodmix still leads, then the other percentage-annotated ingredients follow in descending order of their stated percentage, then the remaining unannotated ingredients in whatever order already reads naturally, with `\ingb{}` bullet ingredients still last as always (see `brood`, `focaccia`, `hamburgerbolletjes`, `pretzels` for the pattern).
- Puff pastry (bladerdeeg) used as a wrapper or crust — treat it as a structural component, not as "zetmeel".
- Desserts, sauces, spice-mix sub-recipes, and dishes with several vegetables of genuinely equal weight (a primavera, a ratatouille-style quiche) — don't force a single "hoofdgroente" pick where none exists.

When several ingredients qualify as protein (e.g. two meats, or meat plus egg), group them together at the front in their original relative order rather than picking just one.

**A small splash of water never needs an ingredient line.** If a step just needs "een scheutje water", "wat water", or "een klein scheutje water" to deglaze a pan, loosen a mixture, or adjust consistency, mention it inline in that step and don't add it to the `\begin{ingredients}` block at all (see `pasta-bolognese`, `worstjes-rode-rijst-salade`, `shakshuka`, `roti` for the existing pattern). This only covers casual, unmeasured splashes — a "scheutje" is roughly 50 ml; once a step needs meaningfully more than that, it's no longer a casual splash. Any water that's actually measured and matters for the recipe to work — dough hydration (`\ing{275 ml}{lauwwarm water}`), cooking/soaking liquid (couscous, rice, risotto), a soup or sauce base, a dip bath — stays a normal `\ing{amount}{water}` line like any other ingredient.

## Units

Use abbreviated units in `\ing{amount}{...}`, matching the overwhelming convention already in `recipes/*.tex`: `g` (not "gram" or "gr"), `el` (not "eetlepel(s)"), `tl` (not "theelepel(s)"), `ml`, `kg`. The one exception is liter, which stays spelled out as `liter` (not abbreviated to `l`) since that's how the handful of existing recipes using it write it.

**Strong ground spice powders are measured in `tl`, not `el`.** An `el` (eetlepel) of a potent powder like kerrie, komijn, kaneel, kurkuma, gember(poeder) or chilipoeder is roughly 6--8 g and overpowers most home-portion dishes; a `tl` (theelepel) at roughly 2--3 g is the right scale, matching how these spices already appear elsewhere in the book. This doesn't apply to a bulk spice-mix sub-recipe meant to be portioned out a spoonful at a time (e.g. the cajunkruiden mix in `jambalaya`, only 1--2 el of which goes into the dish itself), nor to milder dried herbs (Provençaalse kruiden, oregano) or paprikapoeder, which are conventionally used more generously.

## Explicit cooking technique cues

Every stovetop step in `\begin{steps}` that puts something in a pan to actively cook (bakken, fruiten, roosteren, verhitten in a koekenpan/hapjespan/wokpan/pannetje) should be explicit about two things, not left implicit:

- **Heat level**: state it on the hob step itself (`op laag vuur`, `op middelhoog vuur`, `op hoog vuur`, or `zachtjes` as the low-heat equivalent), unless the immediately preceding step already set the pan's heat and this step is a direct continuation in the same pan with no pan-swap in between — in that case the level carries over and doesn't need repeating.
- **Duration or doneness cue**: a concrete time (`2 tot 3 minuten`) and/or a sensory cue for when it's done (`tot de ui glazig is`, `tot ze goudbruin zijn`, `tot hij geurig is`, `tot het vet is uitgebakken`). Vague words like `kort` or `even` on their own, with no time and no cue, aren't enough — a reader who's never made the dish has no way to judge "kort".

This doesn't apply to oven-baking steps (the `°C` already tells you the heat) or to plain boiling-water steps that defer to packaging (`kook de pasta volgens de verpakking`) — those aren't a technique judgment call.

## Washing skin-on produce

Any vegetable or fruit that goes into the dish with its skin/peel still on must be washed before it's cut, and the step should say so explicitly rather than leaving it implied: `was & snij de tomaat`, not just `snij de tomaat`. This covers produce like tomaat, komkommer, courgette, aubergine, paprika, appel, peer, wortel (unpeeled), radijs, citroen/limoen, druiven, pruim, perzik, and unpeeled aardappel. It doesn't apply once the skin itself is removed and discarded (a peeled ui, knoflook, or geschilde aardappel/wortel), or to produce already covered by an earlier wash in the same recipe (don't repeat the instruction for every vegetable in a single wash-and-chop step — one `was` covering the group is enough).

## Geen blender of keukenmachine: staafmixer en standmixer

This kitchen doesn't own a blender or a keukenmachine, only a staafmixer (no attachments — used directly in the pan or in a separate/loose kom) and a standmixer (KitchenAid Artisan) for kneading — see `frontmatter/basisapparatuur.tex`. Recipes should never call for a blender or keukenmachine; use whichever of these actually does the job:

- **Pureeing a soup**: staafmixer directly in the pan (see `tomatensoep`, `pastinaaksoep`, `broccolisoep-geitenkaas`) — it skips the ladle-into-a-jug-and-back step a jug blender needs, and gives a smoother result than a keukenmachine would for a soup that's meant to be velvety. For an extra-smooth result worth the effort (a festive occasion, a dinner-party starter), a `\tip{}` can mention pushing the pureed soup through a fine zeef with the back of a lepel, as in `tomatensoep` and `broccolisoep-geitenkaas`.
- **Kneading bread or pizza dough**: standmixer (see `ciabatta`), or by hand.
- **Grinding or pureeing a small batch** (a falafelmix, a herb butter, a vegetable topping): the staafmixer in a separate kom (see `falafel`, `kalkoen-in-spek`, `lahmacun`), not a keukenmachine.
- **Blending frozen fruit into a soft-serve texture**: the staafmixer directly, in a tall beker with a splash of liquid, letting fully frozen fruit soften a few minutes first (see `bananenijs`).
- **Cooked aardappelpuree**: a staafmixer works against you here, it makes the puree gluey instead of light — use a pureeknijper instead.

## Writing style for recipe text

When writing or editing recipe prose (introductions, tips, foreword), follow these rules:

- **Natural, conversational language.** Write the way a person actually talks, not the way a lifestyle blog writes.
- **No em-dashes.** Use a comma, a full stop, or rewrite the sentence instead.
- **No emoticons or emoji** inserted between or after sentences.
- **No overconfident claims.** Avoid superlatives like "perfect", "the best", "guaranteed to impress", "everyone will love". Prefer honest, measured language.

## Adding a recipe

1. Create `recipes/yourdish.tex` following the pattern in any existing recipe file.
2. Add `\input{recipes/yourdish}` under the appropriate `\chapter{…}` in `main.tex`.
3. Use `\index[register]{…}` on the dish name and key ingredients so they appear in the Register, reusing existing Register and kicker terms (see "Reuse existing Register and kicker terms" above) rather than introducing a new spelling or synonym for something already in the book.
4. If the recipe is based on someone else's published recipe, credit them in the intro or in a closing note, and add the source to `backmatter/bibliografie.tex` rather than embedding the link inline (see "Bibliografie" above).
