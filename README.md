# Kookboek — Familie Spoor

A vintage, two-color family cookbook typeset in LaTeX. Cream paper, EB Garamond
with a handwriting accent, drop caps, running heads, margin "Tip van Ben" notes,
hand-drawn ingredient/hero illustration placeholders, a category table of
contents (*Inhoud*) and an alphabetical *Register* (index).

## Requirements

- **XeLaTeX** or **LuaLaTeX** (the style uses `fontspec` — plain pdfLaTeX won't work).
- Fonts (install system-wide, or drop the `.ttf` files in a `fonts/` folder and
  uncomment the `Path=` options in `kookboek.sty`):
  - **EB Garamond** — https://fonts.google.com/specimen/EB+Garamond
  - **Nothing You Could Do** — https://fonts.google.com/specimen/Nothing+You+Could+Do
  - *(optional)* **Juliana** (Sem Hartz) for the family name on the cover — a
    licensed face; falls back to EB Garamond until you add it.

## Build

```sh
latexmk -xelatex main.tex
```

or manually (note the index pass):

```sh
xelatex main.tex
makeindex -o register.ind register.idx   # or: xindy
xelatex main.tex
xelatex main.tex
```

Output: `main.pdf` at 19 × 24 cm trim.

## Swapping placeholders for real drawings

Replace `\heroplaceholder{caption}` with `\heroimage{path/to/drawing.png}{caption}`,
and the dashed `\ingredientsketch{label}` boxes likewise once you have the art.
