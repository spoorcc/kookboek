# Generate a nano banana illustration prompt for a recipe

The user will name a recipe (by dish title or filename). Your job is to output a ready-to-paste prompt for nano banana (Google's Gemini image model) that combines this project's fixed illustration-style instruction with the recipe's content, stripped of LaTeX markup, as inspiration.

## Steps

1. **Find the recipe.** Match the named dish against the `\begin{recipe}{...}` titles in `recipes/*.tex`, or against the filename if the user gives a slug. If nothing matches exactly, grep for close matches and ask which one they mean rather than guessing.

2. **Read the full recipe file.**

3. **Strip the LaTeX noise.** Convert the recipe into plain, readable Dutch text before it goes anywhere near the prompt — an image model reads `\index[register]{...}`, `\label{...}`, `\dvd`, brace groups, and `\item` markers as visual noise, not content. Concretely:
   - Title: from `\begin{recipe}{Naam}`, plain, no braces.
   - Kicker: the human-readable text argument of `\kicker[...]{...}` (e.g. `Voorgerecht · vlees · Nederlands`), not the bracketed tag list.
   - Meta: the `\meta{...}` text with `\dvd` replaced by `·`.
   - Intro: the `\lettrine{X}{rest}` paragraph reassembled into a normal sentence (`X` + `rest`), with any trailing `\index`/`\label`/comments dropped.
   - Ingredients: one line per `\ing{amount}{name}` → `amount name`, and per `\ingb{name}` → `name`, dropping every `\index[register]{...}` tag.
   - Steps: the text of each `\item`, dropping `\index`/`\label`, as a numbered or bulleted list.
   - Tip: the plain text of `\tip{...}`, if present.
   - Drop entirely: `\heroimage`/`\heroimagefade`/`\heroplaceholder`/`\ingredientsketch`/`\marginimage` calls, `\blockrule{...}` labels (the "Ingrediënten"/"Bereiding" section names can stay as plain headings if useful, but the macro itself goes), and any `%` comments.

4. **Output the prompt** in this exact shape — the fixed style instruction first, then the cleaned recipe text as inspiration, so the user can copy the whole block straight into nano banana:

   ```
   Gebruik dit recept als inspiratie. Maak een verfijnde waterverfillustratie die de essentie van het gerecht weergeeft. Stijl: handgeschilderde aquarel, zachte natuurlijke kleuren, veel witruimte, witte achtergrond, geen tekst, geen rand, geschikt voor een professioneel kookboek

   <cleaned plain-text version of the recipe>
   ```

   Put it in a single fenced code block so it's easy to copy in one go.

5. **Don't otherwise summarize, translate, or embellish the recipe.** Keep every ingredient, amount, and step — only the LaTeX markup is removed, not the content.

6. **Flag existing art.** If the recipe already has a `\heroimage{...}{...}` or `\heroimagefade{...}` call (i.e. it's past the `\heroplaceholder` stage), say so briefly so the user knows a new illustration would replace existing art — but still produce the prompt if they want it anyway.

7. **Stop there.** This skill's job is producing the prompt, not generating the image, saving it under `images/`, or wiring it into the recipe with `\heroimage`/`\heroimagefade`. Only help with those follow-up steps if the user separately asks.
