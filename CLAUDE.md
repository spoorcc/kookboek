# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A vintage, two-color family cookbook (*Kookboek — Familie Spoor*) typeset in LaTeX, printed via Lulu as a **hardcover casewrap**. Output is `main.pdf` at Lulu Crown Quarto trim (189 × 246 mm / 7.44 × 9.68 in) — this is the interior *text-block* trim. The case (cover) is physically larger (438.27 × 290.31 mm wrapped sheet, per `q6qdvpe-cover-template.pdf`) since a hardcover case wraps around the block with a small overhang; see "Wraparound cover" below.

## Development environment

Open the repo in VS Code and choose **Reopen in Container**. The devcontainer (`.devcontainer/devcontainer.json` + `Dockerfile`) provides:

- **texlive/texlive** (full TeX Live) with XeLaTeX and `latexmk`
- **EB Garamond** and **Nothing You Could Do** vendored as TTF files in `fonts/`
- **LaTeX Workshop** VS Code extension (auto-builds on save)
- **Claude Code** VS Code extension

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

- Trim size matches 189×246mm (Lulu Crown Quarto text-block trim) on every page
- All fonts are embedded
- Full-bleed artwork doesn't touch the page edge unless the page includes Lulu's bleed margin
- Image resolution is at least 300 DPI at printed size
- Margins in `kookboek.sty`'s `geometry` settings meet Lulu's 12.7mm safety margin
- Page count meets Lulu's binding minimums and is a multiple of 4
- Recipes don't still contain placeholder macros (`\heroplaceholder`, `\ingredientsketch`, `\writelines`)
- No recipe leaves just one leftover step behind on its last page (a single-step widow page)

`build.sh` runs it automatically after every build. Run it manually with:

```sh
python3 scripts/lulu_lint.py KookboekFamilieSpoor.pdf
```

Trim-size, font-embedding, bleed, and margin problems are reported as errors and fail the build. Unfinished-recipe placeholders, low-resolution art, odd page counts, and single-step widow pages are reported as warnings and don't fail the build — pass `--strict` to also fail on those (e.g. right before uploading to Lulu). The checks target the interior file's text-block trim size and don't apply to the wraparound cover (see below), which is deliberately sized larger for the hardcover case.

## Wraparound cover (`cover/cover.tex`)

`cover/cover.tex` is a standalone LaTeX document (not `\input` by `main.tex`) producing Lulu's wraparound cover: back cover, spine, and front cover as one page, sized to the hardcover case size (195.33 × 258.57mm, larger than the interior's 189×246mm text-block trim — see "Project" above) plus Lulu's 15.87mm wrap area on every outer edge. It reuses the same fonts and colours as `kookboek.sty` and the front cover's photo and title block from `main.tex`. The cover's `\trimw`/`\trimh` intentionally do **not** match `kookboek.sty`'s `paperwidth`/`paperheight` — don't "fix" that.

Hardcover casewrap spine width is **not** a formula — Lulu computes it from an internal lookup table keyed on page count, and the true value is only known once you generate a cover template from Lulu's Project Creation Tool after uploading the interior file. `\spinew` in `cover/cover.tex` is hardcoded from one such template (generated for 164 pages, matching the interior's current page count) and must be reconfirmed (and `\interiorpagecount` updated to match) whenever the interior's page count changes, before ordering a real proof.

## Architecture

| File | Role |
|---|---|
| `main.tex` | Document root: cover, front matter, chapter/recipe order, Inhoud (ToC), Register (index) |
| `kookboek.sty` | All styling and every recipe macro |
| `cover/cover.tex` | Lulu wraparound cover (back + spine + front), built and uploaded separately |
| `frontmatter/voorwoord.tex` | Foreword |
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
| `\writelines{n}` | Ruled lines for recipes whose method hasn't been written yet |
| `\lettrine{X}{rest}` | Terracotta drop cap opening a paragraph |

### Kicker vs. meta

`\kicker` and `\meta` look alike (same small-caps terracotta style) but split different information — don't let a tag drift into the wrong one:

- **`\kicker[Terms]{...}`** — what you get on the table. Up to four `·`-separated segments, in order: course (Hoofdgerecht/Bijgerecht/Voorgerecht/Dessert/Bakken/Brood & basis), protein/diet (Vlees/Vis/Vegetarisch/Vegan/Zoet), cuisine (Italiaans, Mexicaans, ...), and an optional context tag (Doordeweeks, Kinderen, Kerst, Hartig, Pittig, Basisrecept, Snack, ...). Example: `\kicker[Hoofdgerecht,Vlees,Italiaans,Doordeweeks]{Hoofdgerecht · vlees · Italiaans · doordeweeks}`.
- **`\meta{...}`** — what cooking it takes. Up to three `\dvd`-separated segments, in order: bereidingstijd, optional portie-opbrengst (omit "Voor 5 personen" — that's the book's default), and an optional effort/method tag (Eén pan, Snel, Eenvoudig, an oven temperature). Example: `\meta{40 minuten \dvd Voor 6 porties \dvd Eén pan}`.
- Cuisine belongs only in `\kicker`, never repeated in `\meta`.
- Diet/allergen tags (glutenvrij, lactosevrij, notenvrij) are intentionally not part of this scheme — mislabeling those is a food-safety risk, not just a style slip.

## Ingredient ordering

Within a `\begin{ingredients}` … `\end{ingredients}` block, order matters:

0. **Named-in-the-title ingredient(s) first, above all else.** If the recipe title itself names an ingredient — as the first half of a compound dish name (bloemkool**pasta**, andijvie**stamp**, boerenkool**stamp**, spinazie**quiche**, venkel**risotto**, pastinaak**soep**) or via an explicit "met X(, Y en Z)" / "van X" clause (*Boerenkoolstamp met rookworst*, *Quiche met ham en prei*, *Tomatensoep van geroosterde tomaten*) — that ingredient leads the list, in the order the title names it, ahead of the protein/starch/vegetable heuristic below. This applies even when the named ingredient wouldn't otherwise be the protein/starch/vegetable pick (e.g. *Riso freddo* → rijst first; *IJstaart met karamel en chocolade* → karamel, chocolade first). Generic dish-type words that aren't themselves a specific ingredient (pasta, gnocchi, tortellini, quiche, stamp, soep, risotto, salade, taart used as the bare head noun with no modifier) don't force anything — only an actual named foodstuff does. This is why the `gnocchi-*` and `tortellini-al-forno` recipes keep gnocchi/tortellini itself at the front of their lists ahead of the "met X en Y" ingredients named alongside it in the title — gnocchi and tortellini are treated the same as pasta, not as a named ingredient.
1. **Protein** first (vlees, vis, gehakt, worst, ei, peulvruchten — or, in a vegetarian dish where cheese carries the dish, a cheese like feta/geitenkaas/gorgonzola).
2. **Zetmeel** (the classic starchy staple: aardappel/rijst/pasta/couscous/noodles, or a bread/wrap/tortilla serving as the dish's carrier).
3. **Hoofdgroente** (the single vegetable that's central to the dish), if there is one clear candidate.
4. Everything else, in whatever order already reads naturally (aromatics, dairy, spices, liquids).
5. `\ingb{…}` items always last, in their existing relative order — these are bullet ingredients without a fixed amount (to taste, a splash, a garnish) and stay at the back regardless of category.

This ordering applies to a dish's main ingredient list. It does **not** apply to:
- Pastry/dough sub-blocks (a quiche crust, bread dough, pizza dough) — keep the standard baking order (bloem, vet, ei, zout, ...) since there's no protein/starch/vegetable split to make.
- Puff pastry (bladerdeeg) used as a wrapper or crust — treat it as a structural component, not as "zetmeel".
- Desserts, sauces, spice-mix sub-recipes, and dishes with several vegetables of genuinely equal weight (a primavera, a ratatouille-style quiche) — don't force a single "hoofdgroente" pick where none exists.

When several ingredients qualify as protein (e.g. two meats, or meat plus egg), group them together at the front in their original relative order rather than picking just one.

**A small splash of water never needs an ingredient line.** If a step just needs "een scheutje water", "wat water", or "een klein scheutje water" to deglaze a pan, loosen a mixture, or adjust consistency, mention it inline in that step and don't add it to the `\begin{ingredients}` block at all (see `pasta-bolognese`, `worstjes-rode-rijst-salade`, `shakshuka`, `roti` for the existing pattern). This only covers casual, unmeasured splashes. Any water that's actually measured and matters for the recipe to work — dough hydration (`\ing{275 ml}{lauwwarm water}`), cooking/soaking liquid (couscous, rice, risotto), a soup or sauce base, a dip bath — stays a normal `\ing{amount}{water}` line like any other ingredient.

## Writing style for recipe text

When writing or editing recipe prose (introductions, tips, foreword), follow these rules:

- **Natural, conversational language.** Write the way a person actually talks, not the way a lifestyle blog writes.
- **No em-dashes.** Use a comma, a full stop, or rewrite the sentence instead.
- **No emoticons or emoji** inserted between or after sentences.
- **No overconfident claims.** Avoid superlatives like "perfect", "the best", "guaranteed to impress", "everyone will love". Prefer honest, measured language.

## Adding a recipe

1. Create `recipes/yourdish.tex` following the pattern in any existing recipe file.
2. Add `\input{recipes/yourdish}` under the appropriate `\chapter{…}` in `main.tex`.
3. Use `\index[register]{…}` on the dish name and key ingredients so they appear in the Register.
