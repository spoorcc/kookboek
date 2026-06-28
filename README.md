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

## Layout of the repo

```
main.tex                 cover, front matter, chapter order, prints Inhoud + Register
kookboek.sty             all styling + recipe macros (\recipe, \ing, \tip, etc.)
frontmatter/voorwoord.tex
recipes/
  risotto.tex            Tomaten-pestorisotto
  venkelworstpasta.tex   Pasta met venkelworst & kool
  shakshuka.tex
  jambalaya.tex          ingredients + cajun blend; method left blank to fill in
  bloemkoolpasta.tex
  pita.tex               Puffy pita
```

## Adding a recipe

1. Create `recipes/yourdish.tex`:

   ```latex
   \begin{recipe}{Naam van het gerecht}
   \kicker{Hoofdgerecht · vegetarisch}
   \index[register]{Naam van het gerecht}

   \heroplaceholder{handgetekende illustratie}
   \meta{30 minuten \dvd Voor 4 personen \dvd Italiaans}

   \lettrine{E}{erste} woord van de inleiding ...

   \blockrule{Ingrediënten}
   \begin{ingredients}
     \ing{200 g}{een ingrediënt}\index[register]{Een ingrediënt}
     \ingb{iets op gevoel}        % bullet, no amount
   \end{ingredients}

   \blockrule{Bereiding}
   \tip{Een tip van Ben.}
   \ingredientsketch{schets in de kantlijn}
   \begin{steps}
     \item Eerste stap.
   \end{steps}
   \end{recipe}
   ```

2. `\input{recipes/yourdish}` under the right `\chapter{...}` (category) in `main.tex`.

The *Inhoud* (chapters = categories, sections = recipes) and the *Register*
(`\index[register]{...}` entries) update automatically on the next build.

## Swapping placeholders for real drawings

Replace `\heroplaceholder{caption}` with `\heroimage{path/to/drawing.png}{caption}`,
and the dashed `\ingredientsketch{label}` boxes likewise once you have the art.
