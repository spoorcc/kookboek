# Kookboek — Familie Spoor

A vintage, two-color family cookbook typeset in LaTeX. Cream paper, EB Garamond
with a handwriting accent, drop caps, running heads, margin "Tip van Ben" notes,
hand-drawn ingredient/hero illustration placeholders, a category table of
contents (*Inhoud*) and an alphabetical *Register* (index).

**Browse it online:** [spoorcc.github.io/kookboek](https://spoorcc.github.io/kookboek/)

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
`KookboekFamilieSpoor.pdf` (19 × 24 cm trim) and `KookboekFamilieSpoor-cover.pdf`.

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
