# Add recipe from notes

The user will paste a recipe in freeform text (from a notes app, a website, or handwritten). Your job is to convert it into a proper `.tex` file and wire it into `main.tex`.

## Steps

1. **Parse the pasted recipe.** Extract:
   - Dish name (Dutch if the source is Dutch, otherwise translate)
   - Category (Hoofdgerecht / Bijgerecht / Soep / Salade / Brood & basis / Dessert / etc.)
   - Estimated cooking time and number of servings — use the original; do **not** scale to a target headcount
   - Cuisine or style tag (optional)
   - Ingredients with amounts — use the original amounts exactly; do **not** scale or adjust them
   - Preparation steps
   - Any tip worth calling out in a `\tip{}`

2. **Derive a filename.** Use a short, lowercase, hyphenated Dutch name, e.g. `recipes/tomaten-soep.tex`.

3. **Write the `.tex` file** using the macros from `kookboek.sty`:

```latex
\begin{recipe}{Naam van het gerecht}
\kicker{Categorie · kenmerk}          % e.g. Hoofdgerecht · vegetarisch
\index[register]{Naam van het gerecht}
\index[register]{Hoofdingredient}     % add 2-4 index entries for key ingredients

\meta{XX minuten \dvd Voor N personen \dvd Keuken}

\lettrine{E}{erste} woord van een korte, neutrale inleiding van 2-3 zinnen.
% Plain language, no em-dashes, no emoticons, no superlatives.

\blockrule{Ingrediënten}
\begin{ingredients}
  \ing{hoeveelheid}{ingrediënt}\index[register]{Ingrediënt}
  \ingb{iets op gevoel}
\end{ingredients}

\blockrule{Bereiding}
\tip{Een praktische kooktip.}          % only if a genuine tip exists
\begin{steps}
  \item Eerste stap.
\end{steps}
\end{recipe}
```

   Writing style rules for the intro and tip:
   - Natural, conversational Dutch
   - No em-dashes — rewrite with a comma or a new sentence
   - No emoticons or emoji
   - No overconfident language ("perfect", "iedereen zal dit geweldig vinden", etc.)

4. **Update `main.tex`.** Add `\input{recipes/filename}` under the correct `\chapter{…}`. If no chapter fits, propose a new one and ask before adding it.

5. **Check the seizoenskalender.** For each vegetable ingredient the recipe uses, check `backmatter/seizoenskalender.tex` for a commented-out `% \seizoenrij{Naam}{...}` line with that name. If one exists, uncomment it and move it into the active, alphabetically-sorted `\seizoenrij` table rows in the `Groente` block (and delete the now-empty comment line). Leave fruit and already-active vegetables alone.

6. **Report back.** Show the generated `.tex` content and confirm the line added to `main.tex` (and any vegetable moved out of the seizoenskalender comment block). Ask the user to verify the servings, cooking time, and category before considering the task done.
