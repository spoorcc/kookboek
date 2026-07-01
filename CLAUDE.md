# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A vintage, two-color family cookbook (*Kookboek — Familie Spoor*) typeset in LaTeX. Output is `main.pdf` at 19 × 24 cm trim.

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

- Trim size matches 190×240mm on every page
- All fonts are embedded
- Full-bleed artwork doesn't touch the page edge unless the page includes Lulu's bleed margin
- Image resolution is at least 300 DPI at printed size
- Margins in `kookboek.sty`'s `geometry` settings meet Lulu's 12.7mm safety margin
- Page count meets Lulu's binding minimums and is a multiple of 4
- Recipes don't still contain placeholder macros (`\heroplaceholder`, `\ingredientsketch`, `\writelines`)

`build.sh` runs it automatically after every build. Run it manually with:

```sh
python3 scripts/lulu_lint.py KookboekFamilieSpoor.pdf
```

Trim-size, font-embedding, bleed, and margin problems are reported as errors and fail the build. Unfinished-recipe placeholders, low-resolution art, and odd page counts are reported as warnings and don't fail the build — pass `--strict` to also fail on those (e.g. right before uploading to Lulu). The checks target the interior file's trim size and don't apply to the wraparound cover (see below), which is sized to trim + bleed on purpose.

## Wraparound cover (`cover/cover.tex`)

`cover/cover.tex` is a standalone LaTeX document (not `\input` by `main.tex`) producing Lulu's wraparound cover: back cover, spine, and front cover as one page, sized to trim + Lulu's 3.18mm bleed on every outer edge. It reuses the same fonts and colours as `kookboek.sty` and the front cover's photo and title block from `main.tex`.

Before ordering a real proof, update `\interiorpagecount` in `cover/cover.tex` to match the built interior PDF's actual page count — the spine width is computed from it using Lulu's published rule-of-thumb formula (`pages/444 + 0.06in`). Always confirm the exact spine width against Lulu's own cover calculator for the paper stock you choose before submitting artwork.

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
| `\kicker{…}` | Small-caps category line above the title |
| `\meta{… \dvd … \dvd …}` | Time / servings / cuisine meta line (`\dvd` = ♦ separator) |
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
