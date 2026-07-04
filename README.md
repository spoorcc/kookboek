# Kookboek — Familie Spoor

<img src="docs/cover-preview.png" alt="Cover of Kookboek — Familie Spoor" width="360">

This isn't a book for outsiders. It's the recipes one family actually cooked over
the years — doordeweeks and met kerst, for two adults and three kids — written
down for the first time so they'd stop living only in one person's head. Nothing
in it was invented here: every recipe started somewhere else and slowly turned
into "how we make it." Quantities are approximate, a few Italian classics have
been quietly Dutch-ified, and a cookbook is never really finished — margins are
there to be written in. (The full note is in the book itself: `frontmatter/voorwoord.tex`.)

Typeset in LaTeX as a vintage, two-color cookbook: cream paper, EB Garamond with
a handwriting accent, drop caps, running heads, margin "Tip van Ben" notes,
hand-drawn ingredient/hero illustration placeholders, a category table of
contents (*Inhoud*) and an alphabetical *Register* (index).

**Browse it online:** [spoorcc.github.io/kookboek](https://spoorcc.github.io/kookboek/)

This book is made to be printed via [Lulu.com](https://www.lulu.com). Want a physical
copy? Go to [lulu.com/create](https://www.lulu.com/create), start a new print book,
upload `KookboekFamilieSpoor.pdf` and `KookboekFamilieSpoor-cover.pdf`, and pick
**Crown Quarto** (189 × 246 mm / 7.44 × 9.68 in) as the trim size — this book is
typeset to that exact format.

## Requirements

- **XeLaTeX** or **LuaLaTeX** (the style uses `fontspec` — plain pdfLaTeX won't work).
- Fonts are vendored in `fonts/` — no system installation needed.
  - *(optional)* **Juliana** (Sem Hartz) for the family name on the cover — a
    licensed face; falls back to EB Garamond until you add it.

## Build

```sh
./build.sh
```

This runs `latexmk -xelatex` for both the interior and the wraparound cover,
then checks the interior against Lulu's print requirements. Output:
`KookboekFamilieSpoor.pdf` (189 × 246 mm Crown Quarto trim) and
`KookboekFamilieSpoor-cover.pdf`.

For a manual build (note the index pass):

```sh
xelatex main.tex
makeindex -o register.ind register.idx   # or: xindy
xelatex main.tex
xelatex main.tex
```

## Swapping placeholders for real drawings

Replace `\heroplaceholder{caption}` with `\heroimage{path/to/drawing.png}{caption}`,
and the dashed `\ingredientsketch{label}` boxes likewise once you have the art.

## License

The book itself — recipes, prose, and illustrations (`frontmatter/`, `recipes/`,
`images/`) — is licensed under
[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/) —
see [LICENSE](LICENSE). Copy it, adapt it, print your own family's version —
just credit Familie Spoor and share it under the same license.

The LaTeX styling/build code and tooling (`kookboek.sty`, `main.tex`,
`cover/cover.tex`, `scripts/`, `build.sh`, `docs/index.html`) is licensed
separately under [MIT](LICENSE-MIT) — Creative Commons licenses are meant for
creative works, not software, so the code is split out on purpose.

Neither license covers the vendored fonts in `fonts/` (EB Garamond and Nothing
You Could Do), which keep their own SIL Open Font License.
