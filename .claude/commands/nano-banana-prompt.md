# Generate a nano banana illustration prompt for a recipe

The user will name a recipe (by dish title or filename). Your job is to output a ready-to-paste prompt for nano banana (Google's Gemini image model) that combines this project's fixed illustration-style instruction with the recipe's full LaTeX source as inspiration — reproducing the workflow the user has been doing by hand.

## Steps

1. **Find the recipe.** Match the named dish against the `\begin{recipe}{...}` titles in `recipes/*.tex`, or against the filename if the user gives a slug. If nothing matches exactly, grep for close matches and ask which one they mean rather than guessing.

2. **Read the full recipe file.**

3. **Output the prompt** in this exact shape — the fixed style instruction first, then the complete, unmodified `.tex` source of the recipe as inspiration, so the user can copy the whole block straight into nano banana:

   ```
   Gebruik dit recept als inspiratie. Maak een verfijnde waterverfillustratie die de essentie van het gerecht weergeeft. Stijl: handgeschilderde aquarel, zachte natuurlijke kleuren, veel witruimte, witte achtergrond, geen tekst, geen rand, geschikt voor een professioneel kookboek

   <full contents of recipes/<file>.tex>
   ```

   Put it in a single fenced code block so it's easy to copy in one go.

4. **Don't summarize, translate, or rewrite the recipe.** Paste the `.tex` content verbatim, LaTeX macros and all — that's what the user has been feeding nano banana so far, and there's no indication it needs cleaning up first.

5. **Flag existing art.** If the recipe already has a `\heroimage{...}{...}` or `\heroimagefade{...}` call (i.e. it's past the `\heroplaceholder` stage), say so briefly so the user knows a new illustration would replace existing art — but still produce the prompt if they want it anyway.

6. **Stop there.** This skill's job is producing the prompt, not generating the image, saving it under `images/`, or wiring it into the recipe with `\heroimage`/`\heroimagefade`. Only help with those follow-up steps if the user separately asks.
